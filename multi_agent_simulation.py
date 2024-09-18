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
    Agent(AgentConfig(
        userid=1,
        username="Alice",
        gender="女",
        slogan="用代码改变世界",
        description="资深软件工程师，专注于人工智能和机器学习领域。喜欢在咖啡馆工作，业余时间热衷于参与开源项目。",
        role="软件工程师",
        task="接更多freelance工作，每天学习2小时新技术，在开源社区建立声誉"
    )),
    Agent(AgentConfig(
        userid=2,
        username="Bob",
        gender="男",
        slogan="健康所系，性命相托",
        description="心脏外科医生，在一家大综合医院工作。经常参与国际医疗援助，热爱阅读医学期刊和弹钢琴。",
        role="医生",
        task="保持良好睡眠习惯，每周阅读3篇医学研究论文，参与国际医疗援助项目"
    )),
    Agent(AgentConfig(
        userid=3,
        username="Charlie",
        gender="男",
        slogan="艺术即生活",
        description="新锐当代艺术家，擅长装置艺术和行为艺术。经常在世界各地举办展览，同时也是一位瑜伽爱好者。",
        role="艺术家",
        task="在三个不同城市举办个人艺术展，每天瑜伽1小时，拓展人际网络"
    )),
    Agent(AgentConfig(
        userid=4,
        username="David",
        gender="男",
        slogan="激发科学兴趣，点燃求知火花",
        description="高中物理教师，热衷于通过实验激发学生的科学兴趣。业余时间喜欢制作科普视频，拥有一个小型天文台。",
        role="教师",
        task="制作10个物理实验视频，增加私教收入，组织学生天文观测活动"
    )),
    Agent(AgentConfig(
        userid=5,
        username="Eva",
        gender="女",
        slogan="创新驱动未来",
        description="科技创业者，创立了一家专注于可持续能源的初创公司。经常参加创业论坛和投资峰会，热爱极限运动。",
        role="创业者",
        task="为公司筹集100万美元投资，每周进行极限运动，开发新的可持续能源技术"
    )),
    Agent(AgentConfig(
        userid=6,
        username="Frank",
        gender="男",
        slogan="美食是最好的语言",
        description="米其林星级主厨，擅长融合各国料理。经营着自己的餐厅，同时也是一个美食旅行节目的主持人。",
        role="厨师",
        task="研发5道创新菜品，提高餐厅营业额，每天摘花园里的苹果"
    )),
    Agent(AgentConfig(
        userid=7,
        username="Grace",
        gender="女",
        slogan="挑战极限，超越自我",
        description="职业网球运动员，多次获得大满贯冠军。非赛季期间致力于青少年体育教育，同时也是一位业余摄影师。",
        role="运动员",
        task="赢得下一个大满贯赛事，为青少年体育教育筹款，举办个人摄影展"
    )),
    Agent(AgentConfig(
        userid=8,
        username="Henry",
        gender="男",
        slogan="用文字构建世界",
        description="畅销小说作家，擅长科幻和悬疑题材。经常在大学进行创意写作讲座，同时也是一位业余历史学家。",
        role="作家",
        task="完成新小说创作并出版，在5所大学举办讲座，每天研究历史1小时"
    )),
    Agent(AgentConfig(
        userid=9,
        username="Ivy",
        gender="女",
        slogan="探索量子世界的奥秘",
        description="量子物理学家，在一所顶尖研究型大学工作。正在进行突破性的量子计算研究，业余时间喜欢弹古筝和园艺。",
        role="物理学家",
        task="发表量子计算研究论文，指导博士生，空闲时间钓鱼"
    )),
    Agent(AgentConfig(
        userid=10,
        username="Jack",
        gender="男",
        slogan="用音乐治愈世界",
        description="爵士乐钢琴家和作曲家，经常在国际音乐节演出。同时也是一位音乐治疗师，在医院志愿服务。",
        role="音乐家",
        task="创作新爵士乐专辑，参加国际音乐节演出，进行音乐治疗志愿服务"
    )),
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
