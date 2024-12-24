import os
import json
from dotenv import load_dotenv
from loguru import logger
from langchain_openai import ChatOpenAI

from core.agent_srv.node_model import (
    DailyObjective,
    MetaActionSequence,
    CV,
    MayorDecision,
    RunningState,
    CharacterArc,
    Reflection,
)
from core.agent_srv.utils import generate_initial_state_hardcoded
from core.agent_srv.prompts import *
from core.db.database_api_utils import make_api_request_sync
from core.db.game_api_utils import (
    make_api_request_async as make_api_request_async_backend,
    make_api_request_sync as make_api_request_sync_backend,
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
base_url = "https://api.aiproxy.io/v1"

obj_planner = obj_planner_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=1.5
).with_structured_output(DailyObjective)

meta_action_sequence_planner = meta_action_sequence_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0
).with_structured_output(MetaActionSequence)

meta_seq_adjuster = meta_seq_adjuster_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0
).with_structured_output(MetaActionSequence)

character_arc_generator = generate_character_arc_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0.5
).with_structured_output(CharacterArc)

daily_reflection_generator = daily_reflection_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=1
).with_structured_output(Reflection)

cv_generator = generate_cv_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0.7
).with_structured_output(CV)

mayor_decision_generator = mayor_decision_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0.5
).with_structured_output(MayorDecision)


async def generate_daily_reflection(state: RunningState):
    payload = {
        "character_stats": state["character_stats"],
        "daily_objectives": state["decision"]["daily_objective"],
        "failed_actions": str(state["false_action_queue"]),
        "additional_requirements": state["prompts"]["daily_reflection_ar"],
        "focus_topic": state["prompts"]["focus_topic"],
        "depth_of_reflection": state["prompts"]["depth_of_reflection"],
        "level_of_detail": state["prompts"]["level_of_detail"],
        "tone_and_style": state["prompts"]["tone_and_style"],
    }
    daily_reflection = await daily_reflection_generator.ainvoke(payload)

    full_prompt = daily_reflection_prompt.format(**payload)
    logger.info("======generate_daily_reflection======\n" + full_prompt)

    return {"decision": {"daily_reflection": daily_reflection.reflection}}


async def generate_daily_objective(state: RunningState):
    response = make_api_request_sync_backend(
        "GET", f"/characters/getByIdS/{state['userid']}"
    )
    skill_list = response.get("data", {}).get("skillList", [])
    skill_name = [skill["skillName"] for skill in skill_list]
    try:
        with open("core/files/skill2actions.json", "r") as f:
            skills = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load skill actions: {e}")
    role_specific_actions = format_role_actions(skill_name, skills)
    state["meta"]["tool_functions"] += role_specific_actions

    retry_count = 0
    payload = {
        "character_stats": state["character_stats"],
        "tool_functions": state["meta"]["tool_functions"],
        "locations": state["meta"]["available_locations"],
        # get the last 3 objectives
        "past_objectives": state.get("decision", []).get("daily_objective", [])[-3:],
        "daily_goal": state["prompts"]["daily_goal"],
        "refer_to_previous": state["prompts"]["refer_to_previous"],
        "market_data": state["public_data"]["market_data"],
        "life_style": state["prompts"]["life_style"],
        "additional_requirements": state["prompts"]["daily_objective_ar"],
    }
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
    full_prompt = obj_planner_prompt.format(**payload)
    logger.info("======generate_daily_objective======\n" + full_prompt)
    # Store daily objectives in database
    daily_objective_data = {
        "characterId": state["userid"],
        "objectives": planner_response.objectives,
    }
    # print(daily_objective_data)
    # await make_api_request_async_backend(
    #     "POST", "/daily_objectives/store", data=daily_objective_data
    # )

    logger.info(f"🌞 OBJ_PLANNER INVOKED with {planner_response.objectives}")
    return {"decision": {"daily_objective": [planner_response.objectives]}}


async def generate_meta_action_sequence(state: RunningState):
    payload = {
        "daily_objective": (
            state["decision"]["daily_objective"][-1]
            if state["decision"]["daily_objective"]
            else []
        ),
        "tool_functions": state["meta"]["tool_functions"],
        "locations": state["meta"]["available_locations"],
        "inventory": state["character_stats"]["inventory"],
        "market_data": state["public_data"]["market_data"],
        "task_priority": state["prompts"]["task_priority"],
        "max_actions": state["prompts"]["max_actions"],
        "additional_requirements": state["prompts"]["meta_seq_ar"],
    }
    meta_action_sequence = await meta_action_sequence_planner.ainvoke(payload)
    full_prompt = meta_action_sequence_prompt.format(**payload)
    logger.info("======generate_meta_action_sequence======\n" + full_prompt)

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
    logger.info(f"🔧 User {state['userid']}: Error context: {error_context}")
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


async def generate_change_job_cv(instance, msg: dict):
    # 1. 从后端接口调用工作列表
    # 2. 调用LLM，输出申请的jobId和cv内容
    # 3. 存储在数据库cv表中
    available_public_jobs = make_api_request_sync_backend(
        "GET", "/publicWork/getAll"
    ).get("data", [])

    user_id = msg.get("characterId")
    msg_data = msg.get("data", {})
    health = msg_data.get("health", 0)
    studyXp = msg_data.get("studyXp", 0)
    education = msg_data.get("education", "None")
    week = msg_data.get("week", 0)
    date = msg_data.get("date", 0)

    payload = {
        "available_public_jobs": available_public_jobs,
        "health": health,
        "experience": studyXp,
        "education": education,
    }
    cv = await cv_generator.ainvoke(payload)

    logger.info(f"📃 CV: {cv}")

    job_detail = make_api_request_sync_backend(
        "GET", f"/publicWork/getById/{cv.job_id}"
    )
    job_name = job_detail.get("data", {}).get("jobName", "")
    cv_request = {
        "jobid": cv.job_id,
        "characterId": user_id,
        "CV_content": cv.cv,
        "week": week,
        "health": health,
        "studyxp": studyXp,
        "date": date,
        "jobName": job_name,
        "election_status": "not_yet",
    }
    make_api_request_sync("POST", "/cv/", data=cv_request)

    mayor_decision = await generate_mayor_decision(
        cv, user_id, studyXp, education, date
    )
    if instance:
        await instance.send_message(
            {
                "characterId": user_id,
                "messageName": "mayor_decision",
                "messageCode": 10,
                "data": {"jobId": cv.job_id, "cv": cv.cv, **mayor_decision},
            }
        )


async def generate_mayor_decision(
    cv: CV, user_id: int, experience: int, education: str, week: int = 0
):
    public_work_info = make_api_request_sync_backend(
        "GET", f"/publicWork/getById/{cv.job_id}"
    ).get("data", {})

    check_result = make_api_request_sync_backend(
        "POST",
        "/publicWork/checkWork",
        data={
            "characterId": user_id,
            "newJobId": cv.job_id,
            "experience": experience,
            "education": education,
        },
    )
    code = check_result.get("code", 0)
    message = check_result.get("message", "")
    payload = {
        "cv": cv.cv,
        "public_work_info": public_work_info,
        "meet_requirements": {"meet": code == 1, "message": message},
    }
    mayor_decision = await mayor_decision_generator.ainvoke(payload)
    logger.info(f"🧔 Mayor decision: {mayor_decision.decision}")
    logger.info(f"🧔 Mayor comments: {mayor_decision.comments}")

    make_api_request_sync(
        "PUT",
        "/cv/election_status",
        data={
            "characterId": user_id,
            "jobid": cv.job_id,
            "week": week,
            "election_status": mayor_decision.decision,
        },
    )

    return {
        "mayor_decision": mayor_decision.decision,
        "mayor_comments": mayor_decision.comments,
    }


async def generate_character_arc(state: RunningState):
    character_info_task = make_api_request_async_backend(
        "GET", f"/characters/getById/{state['userid']}"
    )
    character_info_response = await character_info_task
    character_info = character_info_response.get("data", {})
    character_arc = await character_arc_generator.ainvoke(
        {
            "character_stats": state["character_stats"],
            "character_info": character_info,
            "daily_objectives": state["decision"]["daily_objective"],
            "daily_reflection": state["decision"].get("daily_reflection", ""),
            "action_results": state["decision"]["action_result"],
        }
    )
    return {"Character_Stats": {"character_arc": dict(character_arc)}}


def format_role_actions(roles, data):
    action_strings = ["Here are the actions you can perform based on your roles:"]

    for index, role in enumerate(roles, start=1):
        role_data = data.get(role, {})
        actions = role_data.get("actions", [])
        materials = role_data.get("materials", {})

        # Format the actions
        action_str = f"{index}. craft [itemType:string] [num:int]: Craft a certain number of items.\n"
        action_str += "Constraints: Item must be in ItemType: ("
        action_str += ", ".join([action.split()[1] for action in actions])
        action_str += ") and you should have enough materials.\nHere's the rule:\n"

        # Format the materials
        for item, constraints in materials.items():
            constraint_str = "None" if not constraints else ", ".join(constraints)
            action_str += f"- {item}: {constraint_str}\n"

        action_strings.append(action_str)

    return "\n".join(action_strings)
