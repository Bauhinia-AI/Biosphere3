from agent_srv.node_model import PlanExecute, DailyObjective, DetailedPlan, MetaActionSequence
from agent_srv.prompts import *
from langchain_openai import ChatOpenAI
from loguru import logger
import websockets
import json
import os
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




async def generate_daily_objective(state: PlanExecute):
    daily_objective = await obj_planner.ainvoke(
        {
            "messages": [("user", state["input"])],
            "tool_functions": state["tool_functions"],
            "locations": state["locations"],
            "past_objectives": state.get("past_objectives", []),
        }
    )
    # Prepare data for API request
    data = {
        "userid": state["userid"],
        "objectives": daily_objective.objectives,
    }
    # Make API request to store_daily_objective
    # endpoint = "/store_daily_objective"
    # await make_api_request_async(endpoint, data)

    return {"daily_objective": daily_objective.objectives}


async def generate_detailed_plan(state: PlanExecute):
    detailed_plan = await detail_planner.ainvoke(state)
    # Prepare data for API request
    data = {
        "userid": state["userid"],
        "detailed_plan": detailed_plan.detailed_plan,
    }
    # Make API request to store_plan
    # endpoint = "/store_plan"
    # await make_api_request_async(endpoint, data)

    return {"plan": detailed_plan.detailed_plan}


async def generate_meta_action_sequence(state: PlanExecute):
    meta_action_sequence = await meta_action_sequence_planner.ainvoke(state)
    # Prepare data for API request
    data = {
        "userid": state["userid"],
        "meta_sequence": meta_action_sequence.meta_action_sequence,
    }
    # Make API request to store_meta_seq
    # endpoint = "/store_meta_seq"
    # await make_api_request_async(endpoint, data)

    return {"meta_seq": meta_action_sequence.meta_action_sequence}


async def adjust_meta_action_sequence(state: PlanExecute):
    meta_action_sequence = await meta_seq_adjuster.ainvoke(state)
    # Prepare data for the API request
    data = {
        "userid": state["userid"],
        "meta_sequence": meta_action_sequence.meta_action_sequence,
    }
    # Make API request to update_meta_seq
    # endpoint = "/update_meta_seq"
    # await make_api_request_async("POST", endpoint, data=data)
    return {"meta_seq": meta_action_sequence.meta_action_sequence}

async def listen_for_action_results(state: PlanExecute):
    uri = "ws://localhost:8765"  
    meta_seq = state.get("meta_seq", [])
    execution_results = []

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "userid": state["userid"],
            "meta_sequence": meta_seq,
        }))

        print("Started listening for action results...")

        received_actions = 0

        while True:
            try:
                # 等待下一个动作结果
                message = await websocket.recv()
                action_result = json.loads(message)
                received_actions += 1

                # 处理动作结果
                description = await process_action_result(action_result)
                execution_results.append({
                    "action": action_result.get("data", {}).get("actionName", ""),
                    "result": action_result,
                    "description": description
                })

                # 存储结果
                data = {
                    "userid": state["userid"],
                    "action": action_result.get("data", {}).get("actionName", ""),
                    "result": action_result,
                    "description": description,
                }
                # endpoint = "/store_action_result"
                # await make_api_request_async(endpoint, data)

                # 检查动作是否失败
                action_success = action_result.get("data", {}).get("result", False)
                if not action_success:
                    print(f"Action {data['action']} failed. No further actions will be executed.")
                    state["need_replan"] = True
                    break

                # 如果已收到与执行的动作数量相同的结果，且没有失败，则继续等待或退出
                if received_actions >= len(meta_seq):
                    print("All action results received.")
                    break

            except websockets.ConnectionClosed:
                print("WebSocket connection closed.")
                break
            except Exception as e:
                print(f"Error while receiving action result: {e}")
                break

    # 返回执行结果
    return {"execution_results": execution_results}

async def process_action_result(action_result):
    # 提取必要的信息
    data = action_result.get("data", {})
    action_name = data.get("actionName", "")
    result = data.get("result", False)
    msg = data.get("msg", "")

    # 构建描述
    #description = f"Action '{action_name}' execution {'succeeded' if result else 'failed'}. Message: {msg}"
    # 如果需要使用 LLM 生成更丰富的描述，可以取消注释以下代码
    description = await descritor.ainvoke({"action_result": str(data)})
    response = description.content
    logger.info(response)
    return response