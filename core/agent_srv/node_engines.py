import sys

sys.path.append("..")
from core.agent_srv.node_model import (
    DailyObjective,
    DetailedPlan,
    MetaActionSequence,
    RunningState,
)
from core.agent_srv.prompts import *
from langchain_openai import ChatOpenAI
from loguru import logger
import websockets
import json
import os
from pprint import pprint
import asyncio
from core.db.database_api_utils import make_api_request_async

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

cv_generator = generate_cv_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0.7
)

mayor_decision_generator = mayor_decision_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0.5
)


async def generate_daily_objective(state: RunningState):
    # BUG 这里如果检验失败会报错，需要重试
    # 重试一次
    retry_count = 0
    payload = {
        "character_stats": state["character_stats"],
        "tool_functions": state["meta"]["tool_functions"],
        "locations": state["meta"]["available_locations"],
        # get the last 3 objectives
        "past_objectives": state.get("decision", []).get("daily_objective", [])[-3:],
        "daily_goal": state["prompts"]["daily_goal"],
        "refer_to_previous": state["prompts"]["refer_to_previous"],
        "life_style": state["prompts"]["life_style"],
        "additional_requirements": state["prompts"]["daily_objective_ar"],
    }
    pprint(payload)
    while retry_count < 3:
        try:
            planner_response: RunningState = await obj_planner.ainvoke(payload)
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
    return {"decision": {"daily_objective": [planner_response.objectives]}}


async def generate_detailed_plan(state: RunningState):
    detailed_plan = await detail_planner.ainvoke(state)

    return {"plan": detailed_plan.detailed_plan}


async def generate_meta_action_sequence(state: RunningState):
    payload = {
        "daily_objective": (
            state["decision"]["daily_objective"][-1]
            if state["decision"]["daily_objective"]
            else []
        ),
        "tool_functions": state["meta"]["tool_functions"],
        "locations": state["meta"]["available_locations"],
        "task_priority": state["prompts"]["task_priority"],
        "max_actions": state["prompts"]["max_actions"],
        "additional_requirements": state["prompts"]["meta_seq_ar"],
    }
    pprint(payload)
    meta_action_sequence = await meta_action_sequence_planner.ainvoke(payload)

    await state["instance"].send_message(
        {
            "characterId": state["userid"],
            "messageName": "actionList",
            "messageCode": 6,
            "data": {"command": meta_action_sequence.meta_action_sequence},
        }
    )
    logger.info(
        f"🧠 META_ACTION_SEQUENCE INVOKED with {meta_action_sequence.meta_action_sequence}"
    )
    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}


async def adjust_meta_action_sequence(state: RunningState):
    meta_action_sequence = await meta_seq_adjuster.ainvoke(
        {
            "meta_seq": state["decision"]["meta_seq"][-1],
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
            "replan_time_limit": state["prompts"]["replan_time_limit"],
            "additional_requirements": state["prompts"]["meta_seq_adjuster_ar"],
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
    # logger.info(f"👀 User {state['userid']}: Sensing environment...")

    # # Check if there was a failed action that needs replanning
    # if state.get("decision", {}).get("action_result"):
    #     latest_result = state["decision"]["action_result"][-1]
    #     if latest_result.get("status") == "failed":
    #         logger.info(f"🔄 User {state['userid']}: Action failed, triggering replan")
    #         return {"current_pointer": "Replan_Action"}

    # try:
    #     # Send environment query message
    #     # await state["instance"].send_message(
    #     #     {
    #     #         "characterId": state["userid"],
    #     #         "messageName": "queryEnvironment",
    #     #         "messageCode": 7,
    #     #         "data": {"query": ["location", "nearby_objects", "nearby_characters"]},
    #     #     }
    #     # )

    #     await asyncio.sleep(1)

    #     # Check message queue for environment data
    #     while not state["message_queue"].empty():
    #         message = state["message_queue"].get_nowait()
    #         if message.get("messageName") == "environment_data":
    #             state["environment"] = message.get("data", {})
    #             logger.info(
    #                 f"🌍 User {state['userid']}: Environment updated - {state['environment']}"
    #             )
    # except Exception as e:
    #     logger.error(f"❌ User {state['userid']}: Error sensing environment - {str(e)}")

    return {"current_pointer": "Process_Messages"}


async def replan_action(state: RunningState):
    # 从false_action_queue里取
    false_action = state["false_action_queue"].get_nowait()
    failed_action = false_action.get("actionName")
    error_message = false_action.get("msg")

    # latest_result = state["decision"]["action_result"][-1]
    # failed_action = latest_result.get("action")
    # error_message = latest_result.get("error")
    # current_location = state.get("environment", {}).get("location")

    logger.info(f"🔄 User {state['userid']}: Replanning failed action: {failed_action}")

    # Analyze error type and context
    error_context = {
        "failed_action": failed_action,
        "error_message": error_message,
        "current_meta_seq": state["decision"]["meta_seq"][-1],
        "daily_objective": state["decision"]["daily_objective"][-1],
    }

    # try:
    # Generate new meta sequence with error context
    meta_action_sequence = await meta_seq_adjuster.ainvoke(
        {
            "meta_seq": state["decision"]["meta_seq"][-1],
            "tool_functions": state["meta"]["tool_functions"],
            "locations": state["meta"]["available_locations"],
            "failed_action": failed_action,
            "error_message": error_message,
            "replan_time_limit": state["prompts"]["replan_time_limit"],
            "additional_requirements": state["prompts"]["meta_seq_adjuster_ar"],
        }
    )

    logger.info(
        f"✨ User {state['userid']}: Generated new action sequence: {meta_action_sequence.meta_action_sequence}"
    )

    # Send new action sequence to client
    await state["instance"].send_message(
        {
            "characterId": state["userid"],
            "messageName": "actionList",
            "messageCode": 6,
            "data": {"command": meta_action_sequence.meta_action_sequence},
        }
    )

    return {"decision": {"meta_seq": meta_action_sequence.meta_action_sequence}}


async def generate_change_job_cv(state: RunningState):
    # 1. 获取state中的一些用于判断工作变更的信息
    # 2. 获取可申请的工作列表
    # 3. 根据这些信息生成cv，cv中预留一个字段保存jobId
    # 4. cv内容存储在state中
    payload = {
        "character_stats": state["character_stats"],
        "past_objectives": state.get("decision", []).get("daily_objective", [])[-3:],
        "reflection": state["decision"]["reflection"][-5:],
        "all_public_works": [],
    }
    response = await make_api_request_async("GET", "/publicWork/getAll")
    payload["all_public_works"] = response.get("data", [])
    logger.info(f"💼 All public works: {payload['all_public_works']}")

    cv = await cv_generator.ainvoke(payload)

    logger.info(f"📃 User {state['userid']}: Generated change job CV: {cv}")
    return {"decision": {"cv": cv}}


async def generate_mayor_decision(state: RunningState):
    # 1. 获取state中的一些用于判断工作变更的信息，如cv、个人资料、jobId
    # 2. 获取目前职位的具体情况
    # 3. 获取职位的限制条件
    # 4. 设置随机数种子，增加决策的灵活性
    # 5. 根据这些信息生成决策，包括审核结果、评语
    # 6. 将简历、结果、评语返回发送给游戏端
    job_id = state["decision"]["cv"]["jobId"]
    payload = {
        "character_stats": state["character_stats"],
        "cv": state["decision"]["cv"],
        "public_work_info": {},
    }
    response = await make_api_request_async("GET", f"/publicWork/getById/{job_id}")
    payload["public_work_info"] = response.get("data", {})

    character_info = await make_api_request_async(
        "GET", f"/characters/getById/{state['userid']}"
    )
    experience = character_info.get("data", {}).get("experience", {})
    education = character_info.get("data", {}).get("education", {})

    check_result = await make_api_request_async(
        "POST",
        "/publicWork/checkWork",
        data={
            "characterId": state["userid"],
            "newJobId": job_id,
            "experience": experience,
            "education": education,
        },
    )
    code = check_result.get("data", {}).get("code", 0)
    message = check_result.get("data", {}).get("message", "")
    payload["meet_requirements"] = {"meet": code == 1, "message": message}

    final_decision = await mayor_decision_generator.ainvoke(payload)
    logger.info(
        f"🧔 User {state['userid']}: Generated mayor decision: {final_decision}"
    )
    return {"decision": {"mayor_decision": final_decision}}
