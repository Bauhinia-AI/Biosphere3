import asyncio
import random
from datetime import datetime
import time
from agent_workflow import app
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import threading
from concurrent.futures import ThreadPoolExecutor
import os
from loguru import logger

# from tool_executor import trade_item
from database_api_utils import make_api_request_sync
import uuid

# tool_functions = """
# 1. do_freelance_job(): Perform freelance work
# 2. navigate_to(location): Navigate to a specified location
# 3. sleep(hours): Sleep for specified number of hours
# 4. work_change(): Change job
# 5. get_character_stats(): Get character statistics
# 6. get_character_status(): Get character status
# 7. get_character_basic_info(): Get character basic information
# 8. get_inventory(): Get inventory information
# 9. submit_resume(): Submit resume
# 10. vote(): Cast a vote
# 11. do_public_job(): Perform public work
# 12. study(hours): Study for specified number of hours
# 13. talk(person): Talk to a specified person
# 14. end_talk(): End conversation
# 15. calculate_distance(location1, location2): Calculate distance between two locations
# 16. trade(apple, price:float, quantity:int): Trade apple
# 17. use_item(item): Use an item
# 18. see_doctor(): Visit a doctor
# 19. get_freelance_jobs(): Get list of available freelance jobs
# 20. get_public_jobs(): Get list of available public jobs
# 21. get_candidates(): Get list of candidates
# 22. get_activity_subjects(): Get list of activity subjects
# 23. get_talk_data(): Get conversation data
# 24. get_position(): Get current position
# 25. eat(): Eat food
# """

# locations = """
# 1. Home
# 2. Park
# 3. Restaurant
# 4. Hospital
# 5. School
# 6. Farm
# """
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
# setup the log file
logger.add("logs/agent/multi_agent_simulation.log")


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
        self.userid = str(uuid.uuid4())
        self.username = config.username
        self.gender = config.gender
        self.slogan = config.slogan
        self.description = config.description
        self.stats = {
            "health": round(random.uniform(0, 10), 1),
            "fullness": round(random.uniform(0, 10), 1),
            "energy": round(random.uniform(0, 10), 1),
            "knowledge": round(random.uniform(0, 10), 1),
            "cash": round(random.uniform(0, 10), 1),
        }
        self.role = config.role
        self.task = config.task
        self.created_at = datetime.now()
        self.experienced_days = 0

        self.inventory = self.generate_initial_inventory()
        # self.save_agent_to_mongo()

    def generate_initial_inventory(self):
        possible_items = ["Strength Potion", "Agility Elixir", "Health Tonic"]
        num_items = random.randint(0, 3)
        return random.sample(possible_items, num_items)

    def save_agent_to_mongo(self):
        data = {
            "userid": self.userid,
            "username": self.username,
            "gender": self.gender,
            "slogan": self.slogan,
            "description": self.description,
            "role": self.role,
            "task": self.task,
            "created_at": self.created_at,
            "stats": self.stats,
        }
        endpoint = "/store_npc"
        make_api_request_sync(endpoint, data)
        logger.info(
            f"Agent {self.userid} with name {self.username} saved to MongoDB Atlas."
        )

    async def take_action(self, app, config):
        objective = self.generate_profile()
        # logger.info(f"Objective: {objective}")
        max_steps = 20  # 设置最大步骤数
        step_count = 0
        start_time = time.time()
        async for event in app.astream(objective, config=config):
            for k, v in event.items():
                if k != "__end__":
                    print(f"{self.username}: {v}")
                    # 记录信息到文件
                    # log_filename = f"agent_{self.userid}.log"
                    # with open(log_filename, "a") as log_file:
                    #     log_file.write(f"{self.username}: {v}\n")
                    # if k == "meta_action_sequence":
                    #     """
                    #     k:v
                    #     meta_action_sequence: {'meta_seq': ['get_inventory()', 'talk(traders)', 'trade(item, price)', 'eat()', 'sleep(8)']}
                    #     """
                    if k == "adjust_meta_action_sequence":
                        # print time consumed
                        time_consumed = time.time() - start_time
                        logger.info(f"Time consumed: {time_consumed}")
                        for action in v["meta_seq"]:
                            logger.info(action)
                        logger.info("=================================")

            step_count += 1
            if step_count >= max_steps:
                print(f"{self.username}: 达到最大步骤数")
                # with open(log_filename, "a") as log_file:
                #     log_file.write(f"{self.username}: 达到最大步骤数\n")
                break
        # self.update_stats()

    

    def generate_profile(self):
        data = {
            "collection_name": "daily_objective",
            "user_id": self.userid,
            "k": 2,
            "item": "objectives",  # Assuming 'objectives' is the field you're interested in
        }
        # past_objectives_response = make_api_request_sync(
        #     "POST", "/latest_k_documents", data=data
        # )past
        # Extract the objectives from the response if necessary
        # _objectives = [doc.get("objectives") for doc in past_objectives_response]

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
            "tool_functions": tool_functions_easy,
            "locations": locations,
            "past_objectives": [],  # past_objectives("daily_objective", 2, self.userid),
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
            task="Live a successful life in the town.",
        )
    ),
    # Agent(
    #     AgentConfig(
    #         userid=2,
    #         username="Bob",
    #         gender="Male",
    #         slogan="Barter for mutual benefit",
    #         description="A shrewd trader, passionate about finding the best trading opportunities in the market.",
    #         role="Trader",
    #         task="Monitor the market daily, seeking the best trading opportunities to maximize profits",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=3,
    #         username="Charlie",
    #         gender="Male",
    #         slogan="Casual chat is the spice of life",
    #         description="A social butterfly who enjoys conversing with people from all walks of life",
    #         role="Socialite",
    #         task="Actively engage in conversations with 10 different people every day for entertainment and to increase knowledge",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=4,
    #         username="David",
    #         gender="Male",
    #         slogan="Labor is glorious",
    #         description="A hardworking laborer who believes that diligent work leads to a better life.",
    #         role="Worker",
    #         task="Work at least 8 hours a day, actively seeking part-time jobs to earn more money",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=5,
    #         username="Eva",
    #         gender="Female",
    #         slogan="Health is the greatest wealth",
    #         description="A retiree who enjoys exercising and maintaining good health",
    #         role="Retiree",
    #         task="Maintain a regular sleep schedule, ensure sufficient sleep, eat well, and stay healthy",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=6,
    #         username="Frank",
    #         gender="Male",
    #         slogan="Serve the people",
    #         description="Enthusiastic about community work, enjoys communicating with people and exploring different places",
    #         role="Ordinary Resident",
    #         task="Help complete community voting and election work, communicate with residents to understand their needs and ideas",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=7,
    #         username="Grace",
    #         gender="Female",
    #         slogan="Strive for a better life",
    #         description="Busy looking for a job, very occupied",
    #         role="Job Seeker",
    #         task="Submit resumes, attend interviews, and search for jobs every day",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=8,
    #         username="Henry",
    #         gender="Male",
    #         slogan="Wander everywhere",
    #         description="Restless, loves to travel around",
    #         role="Traveler",
    #         task="Visit at least three places every day, even if they are repeated",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=9,
    #         username="Ivy",
    #         gender="Female",
    #         slogan="Shopping makes me happy",
    #         description="A fashion blogger who enjoys purchasing various goods.",
    #         role="Shopping Enthusiast",
    #         task="Buy different things every day, acquire various items",
    #     )
    # ),
    # Agent(
    #     AgentConfig(
    #         userid=10,
    #         username="Jack",
    #         gender="Male",
    #         slogan="Sharing is the source of happiness",
    #         description="An internet celebrity who enjoys sharing life online.",
    #         role="Streamer",
    #         task="Communicate with different people every day and sell his own products to them",
    #     )
    # ),
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
    days = 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [
            asyncio.create_task(run_agent(agent, config, days)) for agent in agents[:1]
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
    pass
    # whole_day_planning_main()
