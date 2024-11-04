from agent_srv.node_model import (
    DailyObjective,
    DetailedPlan,
    MetaActionSequence,
    RunningState,
)
from agent_srv.prompts import *
from langchain_openai import ChatOpenAI
from loguru import logger
import websockets
import json
import os
import pprint
import asyncio

os.environ["OPENAI_API_KEY"] = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"
obj_planner = obj_planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1.5
).with_structured_output(DailyObjective)

descritor = describe_action_result_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
)
# replanner = replanner_prompt | ChatOpenAI(
#     base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
# ).with_structured_output(Act)

detail_planner = detail_planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
).with_structured_output(DetailedPlan)

meta_action_sequence_planner = meta_action_sequence_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
).with_structured_output(MetaActionSequence)

meta_seq_adjuster = meta_seq_adjuster_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
).with_structured_output(MetaActionSequence)


async def generate_daily_objective(state: RunningState):
    # BUG 这里如果检验失败会报错，需要重试
    # 重试一次
    retry_count = 0
    while retry_count < 3:
        try:
            planner_response: RunningState = await obj_planner.ainvoke(
                {
                    "character_stats": state["character_stats"],
                    "tool_functions": state["meta"]["tool_functions"],
                    "locations": state["meta"]["available_locations"],
                    # get the last 3 objectives
                    "past_objectives": state.get("decision", []).get(
                        "daily_objective", []
                    )[-3:],
                }
            )
            break
        except Exception as e:
            logger.error(
                f"⛔ User {state['userid']} Error in generate_daily_objective: {e}"
            )
            retry_count += 1
            continue
    # Prepare data for API request
    # data = {
    #     "userid": state["userid"],
    #     "objectives": daily_objective.objectives,
    # }
    # Make API request to store_daily_objective
    # endpoint = "/store_daily_objective"
    # await make_api_request_async(endpoint, data)
    logger.info(f"🌞 OBJ_PLANNER INVOKED...")
    return {"decision": {"daily_objective": planner_response.objectives}}


async def generate_detailed_plan(state: RunningState):
    detailed_plan = await detail_planner.ainvoke(state)

    return {"plan": detailed_plan.detailed_plan}


async def generate_meta_action_sequence(state: RunningState):
    meta_action_sequence = await meta_action_sequence_planner.ainvoke(
        {
            "daily_objective": state["decision"]["daily_objective"][-1],
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
        }
    )
    # logger.info(f"🧠 META_ACTION_SEQUENCE INVOKED...")

    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}


async def adjust_meta_action_sequence(state: RunningState):
    meta_action_sequence = await meta_seq_adjuster.ainvoke(
        {
            "meta_seq": state["decision"]["meta_seq"][-1],
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
        }
    )

    logger.info(
        f"🧠 ADJUST_META_ACTION_SEQUENCE INVOKED...with {meta_action_sequence.meta_action_sequence}"
    )
    await state["instance"].send_message(
        {
            "characterId": state["userid"],
            "messageName": "actionList",
            "messageCode": 6,
            "data": {"command": meta_action_sequence.meta_action_sequence},
        }
    )
    # Make API request to update_meta_seq
    # endpoint = "/update_meta_seq"
    # await make_api_request_async("POST", endpoint, data=data)
    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}


async def sensing_environment(state: RunningState):
    logger.info(f"👀 User {state['userid']}: Sensing environment...")
    
    # Check if there was a failed action that needs replanning
    if state.get("decision", {}).get("action_result"):
        latest_result = state["decision"]["action_result"][-1]
        if latest_result.get("status") == "failed":
            logger.info(f"🔄 User {state['userid']}: Action failed, triggering replan")
            return {"current_pointer": "Replan_Action"}
    
    try:
        # Send environment query message
        await state["instance"].send_message({
            "characterId": state["userid"],
            "messageName": "queryEnvironment",
            "messageCode": 7,
            "data": {
                "query": ["location", "nearby_objects", "nearby_characters"]
            }
        })
        
        await asyncio.sleep(1)
        
        # Check message queue for environment data
        while not state["message_queue"].empty():
            message = state["message_queue"].get_nowait()
            if message.get("messageName") == "environment_data":
                state["environment"] = message.get("data", {})
                logger.info(f"🌍 User {state['userid']}: Environment updated - {state['environment']}")
    except Exception as e:
        logger.error(f"❌ User {state['userid']}: Error sensing environment - {str(e)}")
    
    return {"current_pointer": "Process_Messages"}

async def replan_action(state: RunningState):
    latest_result = state["decision"]["action_result"][-1]
    failed_action = latest_result.get("action")
    error_message = latest_result.get("error")
    
    logger.info(f"🔄 User {state['userid']}: Replanning failed action: {failed_action}")
    
    # Generate new meta sequence excluding the failed action
    meta_action_sequence = await meta_seq_adjuster.ainvoke({
        "meta_seq": state["decision"]["meta_seq"][-1],
        "tool_functions": state["meta"]["tool_functions"],
        "locations": state["meta"]["available_locations"],
        "failed_action": failed_action,
        "error_message": error_message
    })
    
    logger.info(f"✨ User {state['userid']}: Generated new action sequence: {meta_action_sequence.meta_action_sequence}")
    
    # Send new action sequence to client
    await state["instance"].send_message({
        "characterId": state["userid"],
        "messageName": "actionList",
        "messageCode": 6,
        "data": {"command": meta_action_sequence.meta_action_sequence},
    })
    
    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}
