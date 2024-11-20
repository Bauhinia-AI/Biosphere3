import os
import sys
import datetime
from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from agent_srv.node_model import (
    PlanExecute,
    DailyObjective,
    DetailedPlan,
    MetaActionSequence,
    Reflection,
)
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
import asyncio
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.database_api_utils import make_api_request_async

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Bio3_agent"

# 定义工具列表
# tool_list = [
#     pick_apple,
#     go_fishing,
#     mine,
#     harvest,
#     buy,
#     sell,
#     use_item,
#     see_doctor,
#     sleep,
#     study,
#     nav,
# ]

tool_functions = """
1.	submit_cv(targetOccupation: OccupationType, content: string): Submit a resume for a public job.
Constraints: Can only be submitted on ResumeSubmitDay which is Saturday.,OccupationType:(Teacher,Doctor)\n
2.	vote(candidateName: string): Cast a vote for a candidate.
Constraints: Can only vote on VoteDay which is Sunday.\n
3.	work_as_public_occupation(hours: int): Perform work as a public occupation (e.g., teacher or doctor).
Constraints: Must have a public occupation, be in the workplace, and have enough energy.\n
4.	pick_apple(): Pick an apple, costing energy.
Constraints: Must have enough energy and be in the orchard.\n
	5.	go_fishing(): Fish for resources, costing energy.
Constraints: Must have enough energy and be in the fishing area.\n
	6.	mine(): Mine for resources, costing energy.
Constraints: Must have enough energy and be in the mine.\n
	7.	harvest(): Harvest crops, costing energy.
Constraints: Must have enough energy and be in the harvest area.\n
	8.	buy(itemType: ItemType, amount: int): Purchase items, costing money.
Constraints: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	9.	sell(itemType: ItemType, amount: int): Sell items for money.
Constraints: Must have enough items in inventory.ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	10.	use_item(itemType: ItemType, amount: int): Use an item.
Constraints: Must have enough items in inventory.ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	11.	see_doctor(hours: int): Visit a doctor, costing money.
Constraints: Must have enough money and be in the hospital.\n
	12.	sleep(hours: int): Sleep to recover energy and health.
Constraints: Must be at home.\n
13.	study(hours: int): Study to achieve a higher degree.
Constraints: Must be in school and have enough money.\n
14.	nav(placeName: string): Navigate to a specified location.
Constraints: Must in (school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard).
"""
tool_functions_easy = """
    4.	pick_apple(): Pick an apple, costing energy.
Constraints: Must have enough energy and be in the orchard.\n
	5.	go_fishing(): Fish for resources, costing energy.
Constraints: Must have enough energy and be in the fishing area.\n
	6.	mine(): Mine for resources, costing energy.
Constraints: Must have enough energy and be in the mine.\n
	7.	harvest(): Harvest crops, costing energy.
Constraints: Must have enough energy and be in the harvest area.\n
	8.	buy(itemType: ItemType, amount: int): Purchase items, costing money.
Constraints: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	9.	sell(itemType: ItemType, amount: int): Sell items for money.
Constraints: Must have enough items in inventory.ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	10.	use_item(itemType: ItemType, amount: int): Use an item.
Constraints: Must have enough items in inventory.ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	11.	see_doctor(hours: int): Visit a doctor, costing money.
Constraints: Must have enough money and be in the hospital.\n
	12.	sleep(hours: int): Sleep to recover energy and health.
Constraints: Must be at home.\n
    13.	study(hours: int): Study to achieve a higher degree.
Constraints: Must be in school and have enough money.\n
    14.	nav(placeName: string): Navigate to a specified location.
Constraints: Must in (school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard).
"""

locations = """
school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard
"""

# 创建LLM和代理
# llm = ChatOpenAI(base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini")
# prompt = hub.pull("wfh/react-agent-executor")
# tool_node = ToolNode(tool_list)

# agent_with_tools = ChatOpenAI(
#     base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini"
# ).bind_tools(tool_list)


# 定义提示模板
obj_planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are the daily objectives planner in a RPG game. For the given user profile:\n
            Name:
            Description:
            Role:
            Task:
            Location:
            Status:
            Inventory:
            \n
            and the past daily objectives(can be empty) are:
            {past_objectives}.
            \n
            Come up with a general daily objectives. Each daily objectives should be diverse and not repetitive. \n
            These objectives are daily objectives that ONLY related to the following tool functions.\n
            {tool_functions}\n
            and the available locations are:\n
            {locations}\n


            The final format should be a list of daily objectives. Like this:\n
            ["Working: Working in the farm","Studying: Discover something about science", "Socializing: Try to make friends"]\n
            """,
        ),
        ("placeholder", "{messages}"),
    ]
)



detail_planner_prompt = ChatPromptTemplate.from_template(
    """For the given daily objectives,
    \n
    {daily_objective}
    \n
    come up with a detailed plan only associated with the available actions.\n
    actions_available:
    {tool_functions}
]\n
    The detailed plan may involve plans that are not in the daily objectives.(daily actions like eating meals, random actions like chatting with friends.)\n

    The final format should be a list of daily objectives. for example:\n
    Working: "I should navigate to the farm, then do a freelance job."\n,
    daily_action:"I should eat breakfast, lunch and dinner."\n,
    Study:"I should study"\n,
    Socializing:"Perhaps I should go to the square and talk to someone."\n

    """
)

meta_action_sequence_prompt = ChatPromptTemplate.from_template(
    """For the given detailed plan, think step by step to come up with a player action sequence ONLY associated with the available actions/locations.\n
    
    {daily_objective}
    \n

    actions_available:
    {tool_functions}
    \n
    locations_available:\n
    {locations}
    The final format should be a list of meta actions. for example:\n
    [meta_action1(param1),meta_action2(param1),...,meta_actionN(param1,param2,param3)]
    \n
    """
)

meta_seq_adjuster_prompt = ChatPromptTemplate.from_template(
    """For the given meta action sequence, adjust the sequence to make sure the player can finish all the daily objectives and follow the constraints.
    tool_functions and constraints:
    {tool_functions}\n
    available locations:\n
    {locations}
    For example, if you are already at the location, you don't need to navigate to it again.
    {meta_seq}
    \n
    """
)

reflection_prompt = ChatPromptTemplate.from_template(
    """Based on the following meta action sequence and their execution results,
    provide a brief reflection on the success of the plan, any unexpected outcomes,
    and potential improvements for future planning:

    Meta Action Sequence:
    {meta_seq}

    Execution Results:
    {execution_results}

    Reflection:
    """
)

describe_action_result_prompt = ChatPromptTemplate.from_template(
    """Based on the following action result,
    provide a brief description for the action result, like: I successfully studied for 2 hours.
    {action_result}
    """
)

# 创建规划器和重新规划器

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

# reflector = reflection_prompt | ChatOpenAI(
#     base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=0
# ).with_structured_output(Reflection)




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


# async def generate_reflection(state: PlanExecute):
#     meta_seq = state.get("meta_seq", [])
#     execution_results = state.get("execution_results", [])

#     reflection = await reflector.ainvoke(
#         {"meta_seq": meta_seq, "execution_results": execution_results}
#     )

#     # Prepare data for API request
#     data = {
#         "userid": state["userid"],
#         "meta_sequence": meta_seq,
#         "execution_results": execution_results,
#         "reflection": reflection.reflection,
#     }
#     # Make API request to store reflection (assuming an endpoint exists)
#     endpoint = "/store_reflection"
#     await make_api_request_async(endpoint, data)
#
#     return {"reflection": reflection.reflection}


# async def replan_step(state: PlanExecute):
#     try:
#         output = await replanner.ainvoke(state)
#         if isinstance(output.action, Response):
#             return {"response": output.action.response}
#         elif isinstance(output.action, Plan):
#             return {"plan": output.action.steps}
#         else:
#             return {
#                 "response": "Unable to determine next action. Please provide more information."
#             }
#     except Exception as e:
#         error_message = f"An error occurred while planning: {str(e)}"
#         return {"response": error_message}


# def should_end(state: PlanExecute) -> Literal["Executor", "__end__"]:
#     if "response" in state and state["response"]:
#         return "__end__"
#     else:
#         return "Executor"

# agent.py
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
import asyncio
import websockets
import json

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

def should_replan(state: PlanExecute):
    if state.get("need_replan", False):
        return True
    else:
        return False

async def describe_action_results(state: PlanExecute):
    execution_results = state.get("execution_results", [])
    descriptions = []

    for result in execution_results:
        action_result = result.get("result", {})
        description = await process_action_result(action_result)
        descriptions.append(description)
    
    # 将描述存储到状态中，或者发送到需要的地方
    state["action_descriptions"] = descriptions

    # 如果需要，将描述存储到数据库或发送到API
    data = {
        "userid": state["userid"],
        "descriptions": descriptions,
    }
    # endpoint = "/store_action_descriptions"
    # await make_api_request_async(endpoint, data)

    return {"action_descriptions": descriptions}

# # 创建工作流
workflow = StateGraph(PlanExecute)
workflow.add_node("Objectives_planner", generate_daily_objective)
# workflow.add_node("detailed_planner", generate_detailed_plan)
workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
workflow.add_node("adjust_meta_action_sequence", adjust_meta_action_sequence)

workflow.add_node("Action_Result_Listener", listen_for_action_results)
workflow.add_edge("adjust_meta_action_sequence", "Action_Result_Listener")
workflow.add_edge("Action_Result_Listener", END)


# workflow.add_node("reflector", generate_reflection)

workflow.add_edge(START, "Objectives_planner")
workflow.add_edge("Objectives_planner", "meta_action_sequence")
workflow.add_edge("meta_action_sequence", "adjust_meta_action_sequence")
workflow.add_edge("adjust_meta_action_sequence", END)


# workflow.add_conditional_edges("replan", should_end)
app = workflow.compile()


# # 主函数
# async def main():
#     config = {"recursion_limit": 10}
#     test_cases = [
#         # {"input": "go to the farm, do a freelance job for 2 hours, then go home and sleep for 8 hours"},
#         # {"input": "study for 3 hours, then do a public job for 4 hours"},
#         {
#             "userid": 8,
#             "input": """userid=8,
#             username="Henry",
#             gender="男",
#             slogan="到处走走",
#             description="闲不住，喜欢到处旅行",
#             role="旅行家",
#             task="每天至少去三个地方，即使重复了也要去",
#             """,
#             "tool_functions": tool_functions,
#             "locations": locations,
#         },
#         # {"input": "check character stats and inventory, then go to the hospital to see a doctor"},
#         # {"input": "navigate to the park, start a conversation with user123 saying 'Hello!', then end the conversation"},
#         # {"input": "do a freelance job for 4 hours, study for 2 hours, then sleep for 6 hours"},
#         # {"input": "check character stats, do a public job for 3 hours, then study for 2 hours"},
#         # {"input": "navigate to the gym, do a freelance job for 2 hours, then go home and sleep for 7 hours"},
#     ]

#     for case in test_cases:
#         print(f"\nTest case: {case['input']}")
#         try:
#             async for event in app.astream(case, config=config):
#                 for k, v in event.items():
#                     if k != "__end__":
#                         print(v)
#         except Exception as e:
#             print(f"An error occurred: {e}")


# # Run the main function
# if __name__ == "__main__":
#     asyncio.run(main())
