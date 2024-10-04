import asyncio
import random
from datetime import datetime
from agent_workflow import app
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import threading
from concurrent.futures import ThreadPoolExecutor
import os
from loguru import logger
from tool_executor import trade_item
from database.mongo_utils import get_latest_k_documents
tool_functions = """
1. do_freelance_job(): Perform freelance work
2. navigate_to(location): Navigate to a specified location
3. sleep(hours): Sleep for specified number of hours
4. work_change(): Change job
5. get_character_stats(): Get character statistics
6. get_character_status(): Get character status
7. get_character_basic_info(): Get character basic information
8. get_inventory(): Get inventory information
9. submit_resume(): Submit resume
10. vote(): Cast a vote
11. do_public_job(): Perform public work
12. study(hours): Study for specified number of hours
13. talk(person): Talk to a specified person
14. end_talk(): End conversation
15. calculate_distance(location1, location2): Calculate distance between two locations
16. trade(apple, price:float, quantity:int): Trade apple
17. use_item(item): Use an item
18. see_doctor(): Visit a doctor
19. get_freelance_jobs(): Get list of available freelance jobs
20. get_public_jobs(): Get list of available public jobs
21. get_candidates(): Get list of candidates
22. get_activity_subjects(): Get list of activity subjects
23. get_talk_data(): Get conversation data
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


@dataclass
class AgentConfig:
    userid: int
    username: str
    gender: str
    slogan: str
    description: str
    role: str
    task: str


# 定义Agent类
class Agent:
    def __init__(self, config: AgentConfig):
        self.userid = config.userid
        self.username = config.username
        self.gender = config.gender
        self.slogan = config.slogan
        self.description = config.description
        self.stats = {
            "health": round(random.uniform(0, 10), 1),
            "fullness": round(random.uniform(0, 10), 1),
            "energy": round(random.uniform(0, 10), 1),
            "knowledge": round(random.uniform(0, 10), 1),
            "cash": random.randint(500, 10000),
        }
        self.role = config.role
        self.task = config.task
        self.created_at = datetime.now()

        self.location = random.choice(
            ["home", "park", "restaurant", "hospital", "school", "farm"]
        )
        self.inventory = self.generate_initial_inventory()

    def generate_initial_inventory(self):
        possible_items = ["Strength Potion", "Agility Elixir", "Health Tonic"]
        num_items = random.randint(0, 3)
        return random.sample(possible_items, num_items)

    async def take_action(self, app, config):
        # objective = self.generate_objective()
        objective = self.generate_profile()
        logger.info(objective)
        max_steps = 20  # 设置最大步骤数
        step_count = 0
        async for event in app.astream(objective, config=config):
            for k, v in event.items():
                if k != "__end__":
                    print(f"{self.username}: {v}")
                    # 记录信息到文件
                    log_filename = f"agent_{self.userid}.log"
                    with open(log_filename, "a") as log_file:
                        log_file.write(f"{self.username}: {v}\n")
                    # if k == "meta_action_sequence":
                    #     """
                    #     k:v
                    #     meta_action_sequence: {'meta_seq': ['get_inventory()', 'talk(traders)', 'trade(item, price)', 'eat()', 'sleep(8)']}
                    #     """
                    #     for action in v["meta_seq"]:
                    #         if action.find("trade") != -1:
                    #             get_profit = trade_item(0, 2, "apple", 1, 1, 2)
                    #             quantity = get_profit['data']['itemTradeQuantity']
                    #             price = get_profit['data']['averagePrice']
                    #             self.stats["cash"] += quantity * price

            step_count += 1
            if step_count >= max_steps:
                print(f"{self.username}: 达到最大步骤数")
                with open(log_filename, "a") as log_file:
                    log_file.write(f"{self.username}: 达到最大步骤数\n")
                break
        # self.update_stats()

    def generate_objective(self) -> str:
        llm = ChatOpenAI(
            base_url="https://api.aiproxy.io/v1", model="gpt-4o-mini", timeout=30
        )  # 30秒超时

        plan_prompt = ChatPromptTemplate.from_template(
            """Generate a plan based on the agent's personal information and tasks. The plan should detail the agent's actions for an entire day, specifying how many hours each task takes. Avoid using vague terms.

Agent's personal information:
Name: {username}
Description: {description}
Role: {role}
Task: {task}
Location: {location}
Status: {stats}
Inventory: {inventory}

You can use ONLY the following tool functions in your plan. Do not use any functions that are not listed here:
{tool_functions}

Available locations:
{locations}

Output the plan in a single sentence without any unnecessary words.
Here is the format example and your plan should NOT be longer than this example:
Wake up at 7 AM, go to the park and chat with people for 1 hour, study at school for 6 hours, have lunch at the restaurant, study at the school for three hours, return home and sleep."""
        )

        formatted_prompt = plan_prompt.format(
            username=self.username,
            description=self.description,
            role=self.role,
            task=self.task,
            location=self.location,
            stats=self.stats,
            inventory=self.inventory,
            tool_functions=tool_functions,
            locations=locations,
        )

        response = llm.invoke(formatted_prompt)
        print(response.content)
        return response.content

    def generate_profile(self):
        return {
            "userid": self.userid,
            "input": f"""userid={self.userid},
            username="{self.username}",
            gender="{self.gender}",
            slogan="{self.slogan}",
            description="{self.description}",
            role="{self.role}",
            task="{self.task}",
            """,
            "tool_functions": tool_functions,
            "locations": locations,
            "past_objectives": get_latest_k_documents("daily_objective", 2, self.userid),
        }

    def update_stats(self):
        self.stats["energy"] = round(self.stats["energy"] - random.uniform(5, 15), 1)
        self.stats["health"] = round(self.stats["health"] - random.uniform(1, 3), 1)
        self.stats["fullness"] = round(self.stats["fullness"] - random.uniform(1, 5), 1)
        self.stats["cash"] = round(self.stats["cash"] - random.uniform(50, 100), 1)

        for key in ["energy", "health", "fullness"]:
            self.stats[key] = max(0, self.stats[key])
        self.stats["cash"] = max(0, self.stats[key])

    def __str__(self):
        inventory_str = ", ".join(self.inventory)
        stats_str = ", ".join(f"{k}: {v}" for k, v in self.stats.items())
        return f"""
Name: {self.username}
Gender: {self.gender}
Slogan: {self.slogan}
Description: {self.description}
Role: {self.role}
Task: {self.task}
Location: {self.location}
Status: {stats_str}
Inventory: {inventory_str}
"""


# 创建10个代理
agents = [
    Agent(
        AgentConfig(
            userid=1,
            username="Alice",
            gender="Female",
            slogan="Knowledge is power",
            description="A university student who loves learning and always craves new knowledge.",
            role="Student",
            task="Study for 8 hours every day, aiming for excellent results in the final exams",
        )
    ),
    Agent(
        AgentConfig(
            userid=2,
            username="Bob",
            gender="Male",
            slogan="Barter for mutual benefit",
            description="A shrewd trader, passionate about finding the best trading opportunities in the market.",
            role="Trader",
            task="Monitor the market daily, seeking the best trading opportunities to maximize profits",
        )
    ),
    Agent(
        AgentConfig(
            userid=3,
            username="Charlie",
            gender="Male",
            slogan="Casual chat is the spice of life",
            description="A social butterfly who enjoys conversing with people from all walks of life",
            role="Socialite",
            task="Actively engage in conversations with 10 different people every day for entertainment and to increase knowledge",
        )
    ),
    Agent(
        AgentConfig(
            userid=4,
            username="David",
            gender="Male",
            slogan="Labor is glorious",
            description="A hardworking laborer who believes that diligent work leads to a better life.",
            role="Worker",
            task="Work at least 8 hours a day, actively seeking part-time jobs to earn more money",
        )
    ),
    Agent(
        AgentConfig(
            userid=5,
            username="Eva",
            gender="Female",
            slogan="Health is the greatest wealth",
            description="A retiree who enjoys exercising and maintaining good health",
            role="Retiree",
            task="Maintain a regular sleep schedule, ensure sufficient sleep, eat well, and stay healthy",
        )
    ),
    Agent(
        AgentConfig(
            userid=6,
            username="Frank",
            gender="Male",
            slogan="Serve the people",
            description="Enthusiastic about community work, enjoys communicating with people and exploring different places",
            role="Ordinary Resident",
            task="Help complete community voting and election work, communicate with residents to understand their needs and ideas",
        )
    ),
    Agent(
        AgentConfig(
            userid=7,
            username="Grace",
            gender="Female",
            slogan="Strive for a better life",
            description="Busy looking for a job, very occupied",
            role="Job Seeker",
            task="Submit resumes, attend interviews, and search for jobs every day",
        )
    ),
    Agent(
        AgentConfig(
            userid=8,
            username="Henry",
            gender="Male",
            slogan="Wander everywhere",
            description="Restless, loves to travel around",
            role="Traveler",
            task="Visit at least three places every day, even if they are repeated",
        )
    ),
    Agent(
        AgentConfig(
            userid=9,
            username="Ivy",
            gender="Female",
            slogan="Shopping makes me happy",
            description="A fashion blogger who enjoys purchasing various goods.",
            role="Shopping Enthusiast",
            task="Buy different things every day, acquire various items",
        )
    ),
    Agent(
        AgentConfig(
            userid=10,
            username="Jack",
            gender="Male",
            slogan="Sharing is the source of happiness",
            description="An internet celebrity who enjoys sharing life online.",
            role="Streamer",
            task="Communicate with different people every day and sell his own products to them",
        )
    ),
]


def agent_task(agent):
    # objective = agent.generate_objective()
    objective = agent.generate_profile()
    log_filename = f"agent_{agent.userid}.log"
    with open(log_filename, "a") as log_file:
        log_file.write(f"Agent {agent.userid}: {agent.username}\n")
        log_file.write(f"Objective: {objective}\n")
        log_file.write(str(agent) + "\n")
        log_file.write("\n" + "=" * 50 + "\n")  # 分隔线


def whole_day_planning_main():
    threads = []
    for userid in range(1, 11):  # 1 to 10
        agent = agents[userid - 1]  # 因为列表索引从0开始
        thread = threading.Thread(target=agent_task, args=(agent,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()


async def agent_routine(agent, config, days):
    log_filename = f"agent_{agent.userid}.log"
    for day in range(1, days + 1):
        with open(log_filename, "a") as log_file:
            log_file.write(f"\n--- 第 {day} 天 {agent.username} ---\n")
            log_file.write(f"\n{agent.username} 的行动:\n")
        try:
            await asyncio.wait_for(
                agent.take_action(app, config), timeout=120
            )  # 2分钟超时
        except asyncio.TimeoutError:
            with open(log_filename, "a") as log_file:
                log_file.write(f"{agent.username} 行动超时\n")
    with open(log_filename, "a") as log_file:
        log_file.write(f"\n--- {days} 天后 {agent.username} 的状态 ---\n")
        log_file.write(str(agent) + "\n")


async def run_agent(agent, config, days):
    log_filename = f"agent_{agent.userid}.log"
    with open(log_filename, "a") as log_file:
        log_file.write(f"\n--- {agent.username} 的初始状态 ---\n")
        log_file.write(str(agent) + "\n")
        log_file.write("\n" + "=" * 50 + "\n")  # 分隔线
    await agent_routine(agent, config, days)


# 主函数
async def main():
    config = {"recursion_limit": 3000}
    days = 10

    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [
            asyncio.create_task(run_agent(agent, config, days)) for agent in agents[:2]
        ]

        completed, pending = await asyncio.wait(
            tasks, return_when=asyncio.ALL_COMPLETED
        )

        for task in completed:
            try:
                await task
            except Exception as e:
                print(f"代理执行出错: {e}")

        for task in pending:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
    # whole_day_planning_main()
