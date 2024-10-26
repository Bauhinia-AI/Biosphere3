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
#BUG 这里如果检验失败会报错，需要重试
    planner_response: RunningState = await obj_planner.ainvoke(
        {
            "character_stats": state["character_stats"],
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
            #get the last 3 objectives
            "past_objectives": state.get("decision", []).get("daily_objective", [])[-3:],
        }
    )
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
    #logger.info(f"🧠 META_ACTION_SEQUENCE INVOKED...")
    

    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}


async def adjust_meta_action_sequence(state: RunningState):
    meta_action_sequence = await meta_seq_adjuster.ainvoke(
        {
            "meta_seq": state["decision"]["meta_seq"][-1],
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
        }
    )

    logger.info(f"🧠 ADJUST_META_ACTION_SEQUENCE INVOKED...with {meta_action_sequence.meta_action_sequence}")
    await state["instance"].send_message({"characterId":state["userid"],"messageName": "actionList", "messageCode": 6, "data": {"command": meta_action_sequence.meta_action_sequence}})
    # Make API request to update_meta_seq
    # endpoint = "/update_meta_seq"
    # await make_api_request_async("POST", endpoint, data=data)
    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}





async def sensing_environment(state: RunningState):
    logger.info(f"👀 User {state['userid']}: Sensing environment...")
    #list all the messages in the message_queue
    #logger.info(f"🏃 User {state['userid']} now have task:{state['message_queue']}")
    return {"current_pointer": "Process_Messages"}
