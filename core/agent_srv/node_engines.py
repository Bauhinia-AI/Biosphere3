from agent_srv.node_model import (
    DailyObjective,
    DetailedPlan,
    MetaActionSequence,
    RunningState,
)
from agent_srv.prompts import *
from core.db.database_api_utils import make_api_request_async
from langchain_openai import ChatOpenAI
from loguru import logger
import websockets
import json
import os
import pprint
import asyncio
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

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
                    "past_objectives": (
                        state.get("decision", {}).get("daily_objective", [])[-3:]
                        if len(state.get("decision", {}).get("daily_objective", []))
                        >= 3
                        else []
                    ),
                }
            )
            break
        except Exception as e:
            logger.error(
                f"⛔ User {state['userid']} Error in generate_daily_objective: {e}"
            )
            retry_count += 1
            continue

    # Store daily objectives in database
    daily_objective_data = {
        "characterId": state["userid"],
        "objectives": planner_response.objectives,
    }
    await make_api_request_async(
        "POST", "/daily_objectives/store", data=daily_objective_data
    )
    
    logger.info(f"🌞 OBJ_PLANNER INVOKED with {planner_response.objectives}")
    return {"decision": {"daily_objective": planner_response.objectives}}


async def generate_detailed_plan(state: RunningState):
    detailed_plan = await detail_planner.ainvoke(state)
    # Store detailed plan in database
    plan_data = {
        "characterId": state["userid"],
        "detailed_plan": detailed_plan.detailed_plan,
    }
    await make_api_request_async("POST", "/plans/store", data=plan_data)

    logger.info(f"🌞 DETAIL_PLANNER INVOKED with {detailed_plan.detailed_plan}")
    return {"plan": detailed_plan.detailed_plan}


async def generate_meta_action_sequence(state: RunningState):
    meta_action_sequence = await meta_action_sequence_planner.ainvoke(
        {
            "daily_objective": (
                state["decision"]["daily_objective"][-1]
                if state["decision"]["daily_objective"]
                else []
            ),
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
        }
    )
    

    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}


async def adjust_meta_action_sequence(state: RunningState):
    failed_action = ""
    error_message = ""
    if state.get("decision", {}).get("action_result"):
        latest_result = state["decision"]["action_result"][-1]
        failed_action = latest_result.get("action", "")
        error_message = latest_result.get("error", "")

    if state["decision"]["meta_seq"]:
        meta_seq = state["decision"]["meta_seq"][-1]
    else:
        logger.error("No meta sequence available.")
        return {"decision": {"meta_seq": []}}

    meta_action_sequence = await meta_seq_adjuster.ainvoke(
        {
            "meta_seq": meta_seq,
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
            "failed_action": failed_action,
            "error_message": error_message,
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
    update_meta_seq_data = {
        "characterId": state["userid"],
        "meta_sequence": meta_action_sequence.meta_action_sequence,
    }
    await make_api_request_async(
        "POST", "/meta_sequences/update", data=update_meta_seq_data
    )
    
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
        await state["instance"].send_message(
            {
                "characterId": state["userid"],
                "messageName": "queryEnvironment",
                "messageCode": 7,
                "data": {"query": ["location", "nearby_objects", "nearby_characters"]},
            }
        )

        await asyncio.sleep(1)

        # Check message queue for environment data
        while not state["message_queue"].empty():
            message = state["message_queue"].get_nowait()
            if message.get("messageName") == "environment_data":
                state["environment"] = message.get("data", {})
                logger.info(
                    f"🌍 User {state['userid']}: Environment updated - {state['environment']}"
                )
    except Exception as e:
        logger.error(f"❌ User {state['userid']}: Error sensing environment - {str(e)}")

    return {"current_pointer": "Process_Messages"}


async def replan_action(state: RunningState):
    latest_result = state["decision"]["action_result"][-1]
    failed_action = latest_result.get("action")
    error_message = latest_result.get("error")
    current_location = state.get("environment", {}).get("location")
    
    logger.info(f"🔄 User {state['userid']}: Replanning failed action: {failed_action}")
    logger.info(f"❌ Error message: {error_message}")
    
    # Analyze error type and context
    error_context = {
        "failed_action": failed_action,
        "error_message": error_message,
        "current_location": current_location,
        "current_meta_seq": state["decision"]["meta_seq"][-1],
        "daily_objective": state["decision"]["daily_objective"][-1]
    }
    
    # try:
        # Generate new meta sequence with error context
    meta_action_sequence = await meta_seq_adjuster.ainvoke({
        "meta_seq": state["decision"]["meta_seq"][-1],
        "tool_functions": state["meta"]["tool_functions"],
        "locations": state["meta"]["available_locations"],
        "failed_action": failed_action,
        "error_message": error_message,
        "current_location": current_location,
        "error_context": error_context
    })
    
    logger.info(f"✨ User {state['userid']}: Generated new action sequence: {meta_action_sequence.meta_action_sequence}")
    
    # Send new action sequence to client
    await state["instance"].send_message({
        "characterId": state["userid"],
        "messageName": "actionList",
        "messageCode": 6,
        "data": {"command": meta_action_sequence.meta_action_sequence},
    })
    
    return {
        "decision": {
            "meta_seq": meta_action_sequence.meta_action_sequence,
            "replan_history": state.get("decision", {}).get("replan_history", []) + [{
                "failed_action": failed_action,
                "error": error_message,
                "new_plan": meta_action_sequence.meta_action_sequence
            }]
        }
    }
        
    # except Exception as e:
    #     logger.error(f"⚠️ Replanning failed: {str(e)}")
    #     # If replanning fails, try a simpler fallback plan
    #     return await fallback_plan(state)

async def reflect_and_summarize(state: RunningState):
    try:
        # Get relevant history data
        past_objectives = state.get("decision", {}).get("daily_objective", [])[-5:]  # Last 5 objectives
        replan_history = state.get("decision", {}).get("replan_history", [])
        
        # Create reflection prompt input
        reflection_input = {
            "past_objectives": past_objectives,
            "replan_history": replan_history,
            "character_stats": state["character_stats"],
        }
        
        # Generate reflection using LLM
        reflection = await reflection_prompt.ainvoke(reflection_input)
        
        # Store reflection in state and database
        timestamp = datetime.now().isoformat()
        reflection_data = {
            "userid": state["userid"],
            "timestamp": timestamp,
            "reflection": reflection.reflection,
            "analyzed_period": {
                "objectives": past_objectives,
                "errors": replan_history
            }
        }
        
        # Store in database (assuming you have a database connection)
        await state["instance"].send_message({
            "characterId": state["userid"],
            "messageName": "storeReflection",
            "messageCode": 8,
            "data": reflection_data
        })
        
        logger.info(f"📝 User {state['userid']}: Generated reflection - {reflection.reflection}")
        
        return {
            "decision": {
                "reflections": state.get("decision", {}).get("reflections", []) + [{
                    "timestamp": timestamp,
                    "content": reflection.reflection
                }]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ User {state['userid']}: Error generating reflection - {str(e)}")
        return {}
