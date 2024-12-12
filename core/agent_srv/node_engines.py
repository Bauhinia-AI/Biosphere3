import sys
import os
import json
import asyncio
from pprint import pprint

from dotenv import load_dotenv
from loguru import logger
import websockets


from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

from core.agent_srv.node_model import (
    CV,
    DailyObjective,
    DetailedPlan,
    MayorDecision,
    MetaActionSequence,
    CV,
    MayorDecision,
    RunningState,
    AccommodationDecision,
)
from core.agent_srv.utils import generate_initial_state_hardcoded
from core.agent_srv.prompts import *
from core.db.database_api_utils import make_api_request_async
from core.backend_service.backend_api_utils import (
    make_api_request_async as make_api_request_async_backend,
    make_api_request_sync as make_api_request_sync_backend,
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
base_url = (
    "https://api.aiproxy.io/v1" if os.getenv("ENVIRONMENT") == "production" else None
)
obj_planner = obj_planner_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=1.5
).with_structured_output(DailyObjective)

descritor = describe_action_result_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0
)
# replanner = replanner_prompt | ChatOpenAI(
#     base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
# ).with_structured_output(Act)

detail_planner = detail_planner_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0
).with_structured_output(DetailedPlan)

meta_action_sequence_planner = meta_action_sequence_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0
).with_structured_output(MetaActionSequence)

meta_seq_adjuster = meta_seq_adjuster_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0
).with_structured_output(MetaActionSequence)

cv_generator = generate_cv_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0.7
).with_structured_output(CV)

mayor_decision_generator = mayor_decision_prompt | ChatOpenAI(
    base_url=base_url, model="gpt-4o-mini", temperature=0.5
).with_structured_output(MayorDecision)

accommodation_decision_generator = accommodation_decision_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0.5
).with_structured_output(AccommodationDecision)


async def generate_daily_objective(state: RunningState):
    # BUG 这里如果检验失败会报错，需要重试
    # 重试一次
    # 获取最新的prompt数据
    try:
        prompt = await make_api_request_async("GET", f"/agent_prompt/?characterId={state['userid']}")
        prompt_data = prompt.get("data", [{}])[0]  # 如果data为空，返回一个空字典
        state["prompts"] = {key: prompt_data[key] for key in prompt_data if key not in ["characterId", "created_at", "updated_at"]}
    except (IndexError, KeyError) as e:
        logger.error(f"⛔ Error retrieving prompt data: {e}")
        state["prompts"] = {}  # 设置一个默认值或处理逻辑
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
        "inventory": state["character_stats"]["inventory"],
        "market_data": state["public_data"]["market_data"],
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
            "failed_action": "",
            "error_message": "",
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


async def generate_change_job_cv(state: RunningState):
    # 1. 从后端接口调用获取角色信息和工作列表
    # 2. 从state中获取用户状态信息和过去5条反思
    # 3. 调用LLM，输出申请的jobId和cv内容
    # 4. 存储在state中
    character_info_task = make_api_request_async_backend(
        "GET", f"/characters/getById/{state['userid']}"
    )
    available_public_jobs_task = make_api_request_async_backend(
        "GET", "/publicWork/getAll"
    )
    character_info_response, available_public_jobs_response = await asyncio.gather(
        character_info_task, available_public_jobs_task
    )
    character_info = character_info_response.get("data", {})
    available_public_jobs = available_public_jobs_response.get("data", [])

    payload = {
        "character_stats": state["character_stats"],
        "character_info": character_info,
        "available_public_jobs": available_public_jobs,
    }
    cv = await cv_generator.ainvoke(payload)

    logger.info(f"📃 CV: {cv}")

    if 'instance' in state and state['instance']:
        await state["instance"].send_message(
            {
                "characterId": state["userid"],
                "messageName": "cv_submission",
                "messageCode": 9,
                "data": {"jobId": cv.job_id, "cv": cv.cv},
            }
        )
    return {"decision": {"cv": cv.cv, "newJobId": cv.job_id}}


async def generate_mayor_decision(state: RunningState):
    # 1. 获取state中的一些用于判断工作变更的信息，如cv、个人资料、jobId
    # 2. 获取目前职位的具体情况
    # 3. 获取职位的限制条件
    # 4. 设置随机数种子，增加决策的灵活性
    # 5. 根据这些信息生成决策，包括审核结果、评语
    # 6. 将简历、结果、评语返回发送给游戏端
    job_id = state["decision"]["newJobId"]
    public_work_task = make_api_request_async_backend(
        "GET", f"/publicWork/getById/{job_id}"
    )
    character_info_task = make_api_request_async_backend(
        "GET", f"/characters/getById/{state['userid']}"
    )
    public_work_info_response, character_info_response = await asyncio.gather(
        public_work_task, character_info_task
    )
    public_work_info = public_work_info_response.get("data", {})
    character_info = character_info_response.get("data", {})
    experience = character_info.get("experience", {})
    education = character_info.get("education", {})

    check_result = make_api_request_sync_backend(
        "POST",
        "/publicWork/checkWork",
        data={
            "characterId": state["userid"],
            "newJobId": job_id,
            "experience": experience,
            "education": education,
        },
    )
    code = check_result.get("code", 0)
    message = check_result.get("message", "")
    payload = {
        "character_stats": state["character_stats"],
        "cv": state["decision"]["cv"],
        "public_work_info": public_work_info,
        "meet_requirements": {"meet": code == 1, "message": message},
    }
    mayor_decision = await mayor_decision_generator.ainvoke(payload)
    logger.info(f"🧔 Mayor decision: {mayor_decision.decision}")
    logger.info(f"🧔 Mayor comments: {mayor_decision.comments}")

    if 'instance' in state and state['instance']:
        await state["instance"].send_message(
            {
                "characterId": state["userid"],
                "messageName": "mayor_decision",
                "messageCode": 10,
                "data": {
                    "decision": mayor_decision.decision,
                    "comments": mayor_decision.comments,
                },
            }
        )
    return {
        "decision": {
            "mayor_decision": mayor_decision.decision,
            "mayor_comments": mayor_decision.comments,
        }
    }


async def generate_accommodation_decision(state: RunningState):
    # 1. 获取当前住宿信息
    current_accommodation_response = await make_api_request_async_backend(
        "GET", f"/dormitory/getById/{state['userid']}"
    )
    current_accommodation_data = current_accommodation_response.get("data", None)

    # 默认值：如果没有当前住宿数据，使用默认值
    current_accommodation = {"id": 1, "type": "Shelter"}
    if current_accommodation_data:
        current_accommodation["id"] = current_accommodation_data.get("id", 1)
        current_accommodation["type"] = current_accommodation_data.get(
            "type", "Shelter"
        )

    # 2. 获取角色财务状态
    character_info_response = await make_api_request_async_backend(
        "GET", f"/characters/getById/{state['userid']}"
    )
    character_info = character_info_response.get("data", {})
    financial_status = {"money": character_info.get("money", 0)}
    # print("financial_status: ", financial_status)

    # 3. 获取所有可用住宿信息并保留必要字段
    accommodations_response = await make_api_request_async_backend(
        "GET", "/dormitory/getAll"
    )
    available_accommodations_raw = accommodations_response.get("data", [])

    # 过滤出必要字段
    necessary_fields = [
        "id",
        "type",
        "weeklyRent",
        "energyRecovery",
        "maxEnergy",
        "maxHealth",
        "maxHungry",
    ]
    available_accommodations = [
        {key: accommodation[key] for key in necessary_fields}
        for accommodation in available_accommodations_raw
    ]

    # 计算每个住宿的 affordable_weeks
    for acc in available_accommodations:
        weekly_rent = acc["weeklyRent"]
        if weekly_rent == 0:
            acc["affordable_weeks"] = 12  # 最大租期
        else:
            affordable_weeks = financial_status["money"] // weekly_rent
            affordable_weeks = min(affordable_weeks, 12)
            acc["affordable_weeks"] = int(affordable_weeks)
    # print("available_accommodations with affordable_weeks: ", available_accommodations)

    # 初始化失败原因列表
    failure_reasons = []

    max_retries = 5
    retries = 0

    while retries < max_retries:
        # 为 LLM 构建输入
        payload = {
            "character_stats": state["character_stats"],
            "current_accommodation": current_accommodation,
            "available_accommodations": available_accommodations,
            "financial_status": financial_status,
            "failure_reasons": failure_reasons,  # 传递失败原因列表
        }

        # 调用 LLM
        try:
            accommodation_decision = await accommodation_decision_generator.ainvoke(
                payload
            )
            print("accommodation_decision: ", accommodation_decision)
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            failure_reasons.append(
                f"Attempt {retries + 1}: LLM invocation failed with error: {e}"
            )
            retries += 1
            continue

        logger.info(f"🏠 Attempt {retries + 1}:")
        logger.info(f"🏠 Accommodation ID: {accommodation_decision.accommodation_id}")
        logger.info(f"🏠 Lease Weeks: {accommodation_decision.lease_weeks}")
        logger.info(f"🏠 Comments: {accommodation_decision.comments}")

        # 验证选择的住宿是否存在
        selected_accommodation = next(
            (
                acc
                for acc in available_accommodations
                if acc["id"] == accommodation_decision.accommodation_id
            ),
            None,
        )

        if not selected_accommodation:
            failure_message = (
                f"Attempt {retries + 1}: Selected accommodation ID {accommodation_decision.accommodation_id} "
                f"does not exist. Please choose a valid accommodation."
            )

            failure_reasons.append(failure_message)
            logger.warning(f"🏠 {failure_message}")
            retries += 1
            continue

        lease_weeks = accommodation_decision.lease_weeks

        # 检查租期是否在1-12周
        if not (1 <= lease_weeks <= 12):
            failure_message = (
                f"Attempt {retries + 1}: Lease weeks {lease_weeks} is out of allowed range (1-12). "
                f"Please choose a valid number of weeks."
            )

            failure_reasons.append(failure_message)
            logger.warning(f"🏠 {failure_message}")
            retries += 1
            continue

        weekly_rent = selected_accommodation["weeklyRent"]
        total_rent = weekly_rent * lease_weeks

        # 检查用户是否能负担得起租金
        if total_rent > financial_status["money"]:
            failure_message = (
                f"Attempt {retries + 1}: Cannot afford total rent of {total_rent} for accommodation ID "
                f"{accommodation_decision.accommodation_id} over {lease_weeks} weeks. "
                f"Available money: {financial_status['money']}."
            )

            failure_reasons.append(failure_message)
            logger.warning(f"🏠 {failure_message}")
            retries += 1
            continue
        else:
            # 如果可以负担，执行租赁
            rent_data = {
                "characterId": state["userid"],
                "money": financial_status["money"],
                "dormitoryId": accommodation_decision.accommodation_id,
                "leaseWeeks": lease_weeks,
            }
            print("rent_data: ", rent_data)

            # 租房和扣钱，AI端OR游戏端
            # 游戏端
            logger.info(f"🏠 Successfully rented accommodation.")
            break

            # AI端
            # rent_response = await make_api_request_async_backend(
            #     "POST", "/CharacterDormitoryController/rent", data=rent_data
            # )
            # print("rent_response: ", rent_response)

            # if rent_response.get("code", 0) == 1:
            #     logger.info(f"🏠 Successfully rented accommodation.")
            #     # 更新财务状态
            #     financial_status["money"] -= total_rent
            #     break  # 成功后退出循环
            # else:
            #     failure_message = (
            #         f"Attempt {retries + 1}: Failed to rent accommodation ID {accommodation_decision.accommodation_id} "
            #         f"for {lease_weeks} weeks. Reason: {rent_response.get('message')}"
            #     )
            #     print("failure_message: ", failure_message)

            #     failure_reasons.append(failure_message)
            #     logger.error(f"🏠 {failure_message}")
            #     retries += 1
            #     continue

    else:
        # 如果重试达到上限，仍未找到合适的住宿
        logger.error(
            f"🏠 Could not find an affordable accommodation after {max_retries} attempts."
        )
        return {
            "decision": {
                "accommodation_id": None,
                "lease_weeks": None,
                "accommodation_comments": "Could not find an affordable accommodation.",
            }
        }

    # 通知游戏客户端有关住宿变更的信息
    await state["instance"].send_message(
        {
            "characterId": state["userid"],
            "messageName": "accommodationChange",
            "messageCode": 8,
            "data": {
                "accommodationId": accommodation_decision.accommodation_id,
                "leaseWeeks": lease_weeks,
                "comments": accommodation_decision.comments,
            },
        }
    )

    return {
        "decision": {
            "accommodation_id": accommodation_decision.accommodation_id,
            "lease_weeks": lease_weeks,
            "accommodation_comments": accommodation_decision.comments,
        }
    }


async def main():
    # 测试简历投递系统
    state = RunningState(**generate_initial_state_hardcoded(35, None))
    workflow = StateGraph(RunningState)

    # 简历投递系统的节点和边
    # workflow.add_node("generate_change_job_cv", generate_change_job_cv)
    # workflow.add_node("generate_mayor_decision", generate_mayor_decision)

    # 新增测试住宿系统
    workflow.add_node(
        "generate_accommodation_decision", generate_accommodation_decision
    )

    # workflow.set_entry_point("generate_change_job_cv")
    # workflow.add_edge("generate_change_job_cv", "generate_mayor_decision")

    # 设置住宿系统为入口点
    workflow.set_entry_point("generate_accommodation_decision")

    graph = workflow.compile()

    await graph.ainvoke(state)


if __name__ == "__main__":
    asyncio.run(main())
