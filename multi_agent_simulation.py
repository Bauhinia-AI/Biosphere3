import asyncio
import random
from agent_workflow import app

# 定义Agent类
import random


class Agent:
    def __init__(self, name: str, background: str):
        self.name = name
        self.background = background
        self.stats = {
            "energy": random.randint(0, 100),
            "health": random.randint(0, 100),
            "knowledge": random.randint(0, 100),
            "money": random.randint(500, 10000),
        }
        self.location = random.choice(
            [
                "home",
                "office",
                "park",
                "cafe",
                "library",
                "gym",
                "restaurant",
                "hospital",
                "school",
                "shopping mall",
            ]
        )
        self.inventory = self.generate_initial_inventory()

    def generate_initial_inventory(self):
        possible_items = [
            "笔记本电脑",
            "智能手机",
            "书",
            "水瓶",
            "钱包",
            "钥匙",
            "背包",
            "耳机",
            "手表",
            "太阳镜",
            "雨伞",
            "笔记本",
            "相机",
            "药品",
            "运动鞋",
            "健身卡",
            "信用卡",
            "公交卡",
            "午餐盒",
            "咖啡杯",
        ]
        num_items = random.randint(3, 7)  # 随机选择3到7个物品
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
名字: {self.name}
背景: {self.background}
位置: {self.location}
状态: {stats_str}
物品: {inventory_str}
"""


# 创建10个代理
agents = [
    Agent("Alice", "资深软件工程师，专注于人工智能和机器学习领域。喜欢在咖啡馆工作，业余时间热衷于参与开源项目。经常接freelance工作，同时也在寻找新的职业机会。擅长管理个人时间，经常进行自学以提升技能。目标：1. 通过接更多freelance工作增加收入 2. 每天至少学习2小时新技术 3. 在开源社区建立良好声誉"),
    
    Agent("Bob", "心脏外科医生，在一家大综合医院工作。经常参与国际医疗援助，热爱阅读医学期刊和弹钢琴。工作繁忙，需要合理安排睡眠时间。偶尔会接诊私人病患，增加额外收入。目标：1. 保持良好的睡眠习惯，每天至少睡7小时 2. 每周阅读至少3篇最新医学研究论文 3. 参与一次国际医疗援助项目"),
    
    Agent("Charlie", "新锐当代艺术家，擅长装置艺术和行为艺术。经常在世界各地举办展览，同时也是一位瑜伽爱好者。喜欢在不同地点寻找灵感，经常需要计算旅行距离。参与各种艺术活动，结识各行各业的人。目标：1. 在三个不同的城市举办个人艺术展 2. 每天进行1小时瑜伽练习 3. 拓展人际网络，认识20位不同领域的专业人士"),
    
    Agent("David", "高中物理教师，热衷于通过实验激发学生的科学兴趣。业余时间喜欢制作科普视频，拥有一个小型天文台。经常参与公共教育项目，同时也接私教来补贴收入。积极参与教师投票活动，关心教育政策。目标：1. 制作并上传10个高质量的物理实验视频 2. 通过私教增加20%的收入 3. 组织一次学生天文观测活动"),
    
    Agent("Eva", "科技创业者，创立了一家专注于可持续能源的初创公司。经常参加创业论坛和投资峰会，热爱极限运动。需要平衡工作和个人生活，经常进行市场调研和商品交易。积极寻找合作伙伴，经常与各界人士交流。目标：1. 为公司筹集100万美元的投资 2. 每周至少进行一次极限运动 3. 开发一项新的可持续能源技术"),
    
    Agent("Frank", "米其林星级主厨，擅长融合各国料理。经营着自己的餐厅，同时也是一个美食旅行节目的主持人。经常需要采购各种食材，研究新的菜品。参与各种烹饪比赛和美食活动，扩展人际网络。目标：1. 研发5道创新菜品 2. 将餐厅营业额提高15% 3. 每天花1小时摘花园里的苹果"),
    
    Agent("Grace", "职业网球运动员，多次获得大满贯冠军。非赛季期间致力于青少年体育教育，同时也是一位业余摄影师。需要严格管理训练和休息时间，经常参与公益活动。在不同城市参加比赛，需要规划行程。目标：1. 赢得下一个大满贯赛事 2. 为青少年体育教育项目筹集50万美元 3. 举办一次个人摄影展"),
    
    Agent("Henry", "畅销小说作家，擅长科幻和悬疑题材。经常在大学进行创意写作讲座，同时也是一位业余历史学家。需要大量阅读和研究来获取灵感，经常在不同地点进行写作。参与各种文学活动和读者见面会。目标：1. 完成新小说的创作并出版 2. 在5所大学举办创意写作讲座 3. 每天花1小时研究历史"),
    
    Agent("Ivy", "量子物理学家，在一所顶尖研究型大学工作。正在进行突破性的量子计算研究，业余时间喜欢弹古筝和园艺。需要平衡教学、研究和个人生活。经常参加学术会议，与同行交流。目标：1. 发表2篇高影响力的量子计算研究论文 2. 指导3名博士生完成论文 3. 有空闲时间就去钓鱼"),
    
    Agent("Jack", "爵士乐钢琴家和作曲家，经常在国际音乐节演出。同时也是一位音乐治疗师，在医院志愿服务。需要管理演出日程和练习时间，经常在不同城市巡演。参与各种音乐活动，结识各界音乐爱好者。目标：1. 创作一张新的爵士乐专辑 2. 在5个国际音乐节演出 3. 每周在医院进行2次音乐治疗志愿服务")
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
