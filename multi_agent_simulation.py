import asyncio
import random
from datetime import datetime
from agent_workflow import app
from dataclasses import dataclass


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
        objective = self.generate_objective()
        async for event in app.astream({"input": objective}, config=config):
            for k, v in event.items():
                if k != "__end__":
                    print(f"{self.name}: {v}")
        self.update_stats()

    def generate_objective(self) -> str:
        if self.stats["energy"] < 30:
            return "go home and sleep for 8 hours"
        elif self.stats["health"] < 30:
            return "go to see a doctor"
        elif self.stats["knowledge"] < 30:
            return "study for 4 hours"
        else:
            actions = [
                "do a freelance job",
                "do a public job",
                "study",
                "talk to someone",
            ]
            return random.choice(actions)

    def update_stats(self):
        self.stats["energy"] -= random.randint(5, 15)
        self.stats["health"] -= random.randint(1, 5)
        self.stats["knowledge"] -= random.randint(1, 3)
        self.stats["money"] -= random.randint(50, 100)

    def __str__(self):
        inventory_str = ", ".join(self.inventory)
        stats_str = ", ".join(f"{k}: {v}" for k, v in self.stats.items())
        return f"""
名字: {self.username}
性别: {self.gender}
口号: {self.slogan}
描述: {self.description}
角色: {self.role}
任务: {self.task}
位置: {self.location}
状态: {stats_str}
物品: {inventory_str}
"""


# 创建10个代理
agents = [
    Agent(
        AgentConfig(
            userid=1,
            username="Alice",
            gender="女",
            slogan="知识就是力量",
            description="热爱学习的大学生，总是渴望获取新知识。",
            role="学生",
            task="每天坚持学习8小时，争取期末考试取得好成绩",
        )
    ),
    Agent(
        AgentConfig(
            userid=2,
            username="Bob",
            gender="男",
            slogan="以物易物，互利共赢",
            description="精明的交易员，热衷于在市场上寻找最佳交易机会。",
            role="交易员",
            task="每天监控市场，寻找最佳交易机会，以赚更多钱为目标",
        )
    ),
    Agent(
        AgentConfig(
            userid=3,
            username="Charlie",
            gender="男",
            slogan="闲聊是人生的调味剂",
            description="社交达人，喜欢与各行各业的人交流。",
            role="社交家",
            task="每天都主动与10个人交流，以此来娱乐自己，并提高知识水平",
        )
    ),
    Agent(
        AgentConfig(
            userid=4,
            username="David",
            gender="男",
            slogan="劳动最光荣",
            description="勤劳的工人，相信努力工作能带来美好生活。",
            role="工人",
            task="每天至少工作8小时，喜欢主动去找一些兼职工作，以赚更多钱为目标",
        )
    ),
    Agent(
        AgentConfig(
            userid=5,
            username="Eva",
            gender="女",
            slogan="健康是最大的财富",
            description="退休老人，喜欢锻炼身体，保持健康",
            role="退休老人",
            task="早睡早起，保证睡眠充足，吃得好，保持健康",
        )
    ),
    Agent(
        AgentConfig(
            userid=6,
            username="Frank",
            gender="男",
            slogan="为人民服务",
            description="热心街道工作，喜欢和人交流，喜欢到处逛",
            role="普通居民",
            task="帮助社区完成投票选举工作，并和社区居民交流，了解他们的需求和想法",
        )
    ),
    Agent(
        AgentConfig(
            userid=7,
            username="Grace",
            gender="女",
            slogan="努力生活",
            description="正在努力找工作，非常忙碌",
            role="无业人员",
            task="每天投递简历，面试，找工作",
        )
    ),
    Agent(
        AgentConfig(
            userid=8,
            username="Henry",
            gender="男",
            slogan="到处走走",
            description="闲不住，喜欢到处旅行",
            role="旅行家",
            task="每天至少去三个地方，即使重复了也要去",
        )
    ),
    Agent(
        AgentConfig(
            userid=9,
            username="Ivy",
            gender="女",
            slogan="购物使我快乐",
            description="时尚博主，喜欢购买各种商品。",
            role="购物达人",
            task="每天买不一样的东西，获得各种物品",
        )
    ),
    Agent(
        AgentConfig(
            userid=10,
            username="Jack",
            gender="男",
            slogan="分享是快乐的源泉",
            description="网红主播，喜欢在网上分享生活。",
            role="主播",
            task="他的工作是每天和不同的人交流，把自家货卖给他们",
        )
    ),
]


# 主函数
async def main():
    config = {"recursion_limit": 10}
    days = 10

    for day in range(1, days + 1):
        print(f"\n--- 第 {day} 天 ---")
        for agent in agents:
            print(f"\n{agent.name} 的行动:")
            await agent.take_action(app, config)

    print("\n--- 10天后的状态 ---")
    for agent in agents:
        print(f"{agent.name} ({agent.background}):")
        print(f"  位置: {agent.location}")
        print(f"  状态: {agent.stats}")
        print(f"  物品: {agent.inventory}")


# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
