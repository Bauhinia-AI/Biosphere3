import os
import sys
import datetime
from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from tools import *
from node_model import (
    PlanExecute,
    DailyObjective,
    DetailedPlan,
    MetaActionSequence,
    Reflection,
)
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
import asyncio
from tool_executor import execute_action_sequence
from loguru import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo_utils import insert_document
from database import config

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Bio3_agent"

# 定义工具列表
tool_list = [
    navigate_to,
    do_freelance_job,
    sleep,
    work_change,
    # get_character_stats,
    # get_character_status,
    # get_character_basic_info,
    get_inventory,
    submit_resume,
    vote,
    do_public_job,
    study,
    talk,
    end_talk,
    calculate_distance,
    trade,
    use_item,
    see_doctor,
    get_freelance_jobs,
    get_public_jobs,
    get_candidates,
    get_activity_subjects,
    get_talk_data,
    get_position,
    eat,
]
# llm-readable
tool_functions = """
1. do_freelance_job(timelength: int): Perform freelance work \n
2. navigate_to(location: str): Navigate to a specified location
3. sleep(hours: int): Sleep for specified number of hours
4. work_change(jobid: int): Change job
8. get_inventory(): Get inventory information
9. submit_resume(jobid: int, cvurl: str): Submit resume
10. vote(userid: int): Cast a vote
11. do_public_job(jobid: int, timelength: int): Perform public work
12. study(hours: int): Study for specified number of hours
13. talk(person: str, talkcontent: str): Talk to a specified person
14. end_talk(userid: str, talkid: str): End conversation
15. calculate_distance(location1: str, location2: str): Calculate distance between two locations
16. trade(merchantid: int, merchantnum: int, transactiontype: int): Trade an item
17. use_item(merchantid: int, merchantnum: int): Use an item
18. see_doctor(): Visit a doctor
19. get_freelance_jobs(): Get list of available freelance jobs
20. get_public_jobs(): Get list of available public jobs
21. get_candidates(): Get list of candidates
22. get_activity_subjects(subjectid: int): Get list of activity subjects
23. get_talk_data(talkid: str): Get conversation data
24. get_position(): Get current position
25. eat(): Eat food
"""

locations = """
1. Home
2. Park
3. Restaurant
4. Hospital
5. School
6. Farm
"""

# 创建LLM和代理
llm = ChatOpenAI(base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini")
prompt = hub.pull("wfh/react-agent-executor")
tool_node = ToolNode(tool_list)

agent_with_tools = ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini"
).bind_tools(tool_list)


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
            and the past daily objectives are:
            {past_objectives}.
            \n
            Come up with a general daily objectives. Each daily objectives should be diverse and not repetitive. \n
            These objectives are daily objectives that ONLY related to the following tool functions.\n
            {tool_functions}\n


            The final format should be a list of daily objectives. Like this:\n
            ["Working: Working in the farm","Studying: Discover something about science", "Socializing: Try to make friends"]\n
            """,
        ),
        ("placeholder", "{messages}"),
    ]
)

# replanner_prompt = ChatPromptTemplate.from_template(
#     """For the given objective, come up with a simple step by step plan. \
# This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
# The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

# Additionally, if during the execution of a step you encounter a tool call with missing required parameters, randomly generate a reasonable parameter value to fill in, rather than throwing an error. For example, if a duration is needed but not specified, you might randomly choose a value between 1 and 8 hours.

# Your objective was this:
# {input}

# Your original plan was this:
# {plan}

# You have currently done the follow steps:
# {past_steps}

# Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
# )

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
    """For the given detailed plan, think step by step to come up with a player action sequence only associated with the available actions/locations.\n
    {plan}
    \n

    actions_available:
    {tool_functions}
    \n
    Use navigate_to to go to the location. \n
    Every day, you start at home. \n
    You need to sleep everyday.\n
    locations_available:\n
    {locations}
    The final format should be a list of meta actions. for example:\n
    [navigate_to(farm),do_public_job(4),navigate_to(restaurant), eat(3), do_freelance_job(4),navigate_to(home),study(3),sleep(8)]
    \n
    """
)

meta_seq_adjuster_prompt = ChatPromptTemplate.from_template(
    """For the given meta action sequence, adjust the sequence to make sure the player can finish all the daily objectives and follow the common sense.
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


# 创建规划器和重新规划器

obj_planner = obj_planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", temperature=1
).with_structured_output(DailyObjective)


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


# # 定义执行步骤函数
# async def execute_step(state: PlanExecute):
#     plan = state["plan"]
#     plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
#     task = plan[0]
#     task_formatted = f"""For the following plan:
# {plan_str}\n\nYou are tasked with executing step {1}, {task}."""
#     agent_response = await agent_executor.ainvoke(
#         {"messages": [("user", task_formatted)]}
#     )
#     return {"past_steps": [(task, agent_response["messages"][-1].content)]}
async def call_tool_node(state: PlanExecute):
    return  {"messages": [agent_with_tools.invoke(state)]}


# async def plan_step(state: PlanExecute):
#     plan = await planner.ainvoke({"messages": [("user", state["input"])]})
#     return {"plan": plan.steps}
async def generate_daily_objective(state: PlanExecute):
    daily_objective = await obj_planner.ainvoke(
        {
            "messages": [("user", state["input"])],
            "tool_functions": state["tool_functions"],
            "locations": state["locations"],
            "past_objectives": state.get("past_objectives", []),
        }
    )
    # Prepare the document to insert
    document = {
        "userid": state["userid"],
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "objectives": daily_objective.objectives,
    }
    # Insert document using insert_document
    # inserted_id = insert_document(config.daily_objective_collection_name, document)
    # print(
    #     f"Inserted daily objective with id {inserted_id} for userid {document['userid']}"
    # )

    return {"daily_objective": daily_objective.objectives}


async def generate_detailed_plan(state: PlanExecute):
    detailed_plan = await detail_planner.ainvoke(state)
    # Prepare the document to insert
    document = {
        "userid": state["userid"],
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detailed_plan": detailed_plan.detailed_plan,
    }
    # Insert document using insert_document
    # inserted_id = insert_document(config.plan_collection_name, document)
    # print(
    #     f"Inserted detailed plan with id {inserted_id} for userid {document['userid']}"
    # )

    return {"plan": detailed_plan.detailed_plan}


async def generate_meta_action_sequence(state: PlanExecute):
    meta_action_sequence = await meta_action_sequence_planner.ainvoke(state)
    meta_action_sequence = await meta_seq_adjuster.ainvoke(meta_action_sequence)
    # Prepare the document to insert
    document = {
        "userid": state["userid"],
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "meta_sequence": meta_action_sequence.meta_action_sequence,
    }
    # Insert document using insert_document
    #inserted_id = insert_document(config.meta_seq_collection_name, document)
    # print(
    #     f"Inserted meta action sequence with id {inserted_id} for userid {document['userid']}"
    # )

    return {"meta_seq": meta_action_sequence.meta_action_sequence}


# async def generate_reflection(state: PlanExecute):
#     meta_seq = state.get("meta_seq", [])
#     execution_results = state.get("execution_results", [])

#     reflection = await reflector.ainvoke(
#         {"meta_seq": meta_seq, "execution_results": execution_results}
#     )

#     # 准备要插入的文档
#     document = {
#         "userid": state["userid"],
#         "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "meta_sequence": meta_seq,
#         "execution_results": execution_results,
#         "reflection": reflection.reflection,
#     }

#     # 使用 insert_document 插入文档
#     #inserted_id = insert_document(config.reflection_collection_name, document)
#     print(f"Inserted reflection with id {inserted_id} for userid {document['userid']}")

#     return {"reflection": reflection.reflection}


async def invoke_tool_executor(state: PlanExecute):
    meta_seq = state.get("meta_seq", [])
    print("Executing the following actions:")
    results = await call_tool_node(meta_seq)
    #results = execute_action_sequence(meta_seq)
    logger.info(results["messages"])
    return {"messages": results["messages"]}
    execution_results = []
    for action, result in zip(meta_seq, results["messages"]):
        print(f"Action: {action}")
        print(f"Result: {result}")
        execution_results.append({"action": action, "result": result})
    return {"execution_results": execution_results}


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


# # 创建工作流
workflow = StateGraph(PlanExecute)
workflow.add_node("Objectives_planner", generate_daily_objective)
workflow.add_node("detailed_planner", generate_detailed_plan)
workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
workflow.add_node("tool_call_generator", invoke_tool_executor)
workflow.add_node("tool_executor", tool_node)
# workflow.add_node("reflector", generate_reflection)

# workflow.add_node("Executor", execute_step)
# workflow.add_node("replan", replan_step)
workflow.add_edge(START, "Objectives_planner")
workflow.add_edge("Objectives_planner", "detailed_planner")
workflow.add_edge("detailed_planner", "meta_action_sequence")
workflow.add_edge("meta_action_sequence", "tool_call_generator")

workflow.add_edge("tool_call_generator", "tool_executor")
workflow.add_edge("tool_executor", END)
# workflow.add_edge("Executor", "replan")
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
