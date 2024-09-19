import os
from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools import (
    do_freelance_job,
    navigate_to,
    sleep,
    study,
    get_character_stats,
    get_inventory,
    do_public_job,
    talk,
    end_talk,
    see_doctor,
)
from node_model import PlanExecute, Plan, Response, Act
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START
import asyncio
from typing import Literal
import json
from datetime import datetime

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Bio3_agent"

# 定义工具列表
tool_list = [
    do_freelance_job,
    navigate_to,
    sleep,
    study,
    get_character_stats,
    get_inventory,
    do_public_job,
    talk,
    end_talk,
    see_doctor,
]

# 创建LLM和代理
llm = ChatOpenAI(base_url="https://api.aiproxy.io/v1", model="gpt-4o")
prompt = hub.pull("wfh/react-agent-executor")
agent_executor = create_react_agent(llm, tool_list, messages_modifier=prompt)

# 定义提示模板
planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """For the given objective, come up with a simple step by step plan. This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Additionally, if during the execution of a step you encounter a tool call with missing required parameters, randomly generate a reasonable parameter value to fill in, rather than throwing an error. For example, if a duration is needed but not specified, you might randomly choose a value between 1 and 8 hours.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

replanner_prompt = ChatPromptTemplate.from_template(
    """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Additionally, if during the execution of a step you encounter a tool call with missing required parameters, randomly generate a reasonable parameter value to fill in, rather than throwing an error. For example, if a duration is needed but not specified, you might randomly choose a value between 1 and 8 hours.

Your objective was this:
{input}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
)

# 创建规划器和重新规划器
planner = planner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o", temperature=0
).with_structured_output(Plan)
replanner = replanner_prompt | ChatOpenAI(
    base_url="https://api.aiproxy.io/v1", model="gpt-4o", temperature=0
).with_structured_output(Act)


# 定义执行步骤函数
async def execute_step(state: PlanExecute):
    plan = state["plan"]
    steps_executed = state.get("steps_executed", 0)
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""For the following plan:
        {plan_str}\n\nYou are tasked with executing step {steps_executed + 1}, {task}."""
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    return {
        "past_steps": state.get("past_steps", []) + [(task, agent_response["messages"][-1].content)],
        "plan": plan[1:],  # Remove the executed step from the plan
        "steps_executed": steps_executed + 1
    }

async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    try:
        output = await replanner.ainvoke(state)
        if isinstance(output.action, Response):
            return {"response": output.action.response}
        elif isinstance(output.action, Plan):
            return {"plan": output.action.steps}
        else:
            return {
                "response": "Unable to determine next action. Please provide more information."
            }
    except Exception as e:
        error_message = f"An error occurred while planning: {str(e)}"
        return {"response": error_message}


def should_replan(state: PlanExecute) -> Literal["replan", "Executor", "__end__"]:
    if not state["plan"]:
        return "replan"
    if state.get("steps_executed", 0) >= 3:  # Replan after every 3 steps
        return "replan"
    return "Executor"

def should_end(state: PlanExecute) -> Literal["Executor", "__end__"]:
    if "response" in state and state["response"]:
        return "__end__"
    else:
        return "Executor"

# 添加反思模块
async def reflect(state: PlanExecute):
    reflection = {
        "timestamp": datetime.now().isoformat(),
        "input": state["input"],
        "steps_executed": state.get("steps_executed", 0),
        "past_steps": state.get("past_steps", []),
        "final_response": state.get("response", "No final response"),
        "execution_result": state,
    }
    
    # 分析可能的失败原因
    if "error" in state:
        reflection["error"] = state["error"]
        reflection["possible_failure_reason"] = "An error occurred during execution"
    elif not state.get("response"):
        reflection["possible_failure_reason"] = "No response generated, possibly due to incomplete execution"
    else:
        reflection["possible_failure_reason"] = "None"

    # 将反思结果写入日志文件
    with open("agent_reflections.jsonl", "a") as f:
        f.write(json.dumps(reflection) + "\n")

    return state

# 创建工作流
workflow = StateGraph(PlanExecute)
workflow.add_node("Reflect", reflect)

workflow.add_node("Objectives_planner", plan_step)
workflow.add_node("Executor", execute_step)
workflow.add_node("replan", replan_step)
workflow.add_edge(START, "Objectives_planner")
workflow.add_edge("Objectives_planner", "Executor")
workflow.add_edge("Executor", "Reflect")
workflow.add_conditional_edges("Reflect", should_replan)
workflow.add_conditional_edges("replan", should_end)

app = workflow.compile()


# 主函数
async def main():
    config = {"recursion_limit": 10}
    test_cases = [
        # {"input": "go to the farm, do a freelance job for 2 hours, then go home and sleep for 8 hours"},
        # {"input": "study for 3 hours, then do a public job for 4 hours"},
        {
            "input": "check character stats, if energy is less than 30, go to sleep, if health is less than 30, go to see a doctor, if knowledge is less than 30, go to study"
        },
        # {"input": "check character stats and inventory, then go to the hospital to see a doctor"},
        # {"input": "navigate to the park, start a conversation with user123 saying 'Hello!', then end the conversation"},
        # {"input": "do a freelance job for 4 hours, study for 2 hours, then sleep for 6 hours"},
        # {"input": "check character stats, do a public job for 3 hours, then study for 2 hours"},
        # {"input": "navigate to the gym, do a freelance job for 2 hours, then go home and sleep for 7 hours"},
    ]

    for case in test_cases:
        print(f"\nTest case: {case['input']}")
        try:
            async for event in app.astream(case, config=config):
                for k, v in event.items():
                    if k != "__end__":
                        print(v)
        except Exception as e:
            print(f"An error occurred: {e}")


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
