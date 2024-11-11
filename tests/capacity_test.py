# tests/capacity_test.py

import asyncio
import aiohttp
import time
import random
import matplotlib.pyplot as plt
import sys
import os

# 确保父目录在 sys.path 中，以便导入主项目中的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.create_database import DatabaseSetupApp  # 导入 DatabaseSetupApp

API_BASE_URL = "http://localhost:8085"

# 常量定义
DATA_VOLUMES = list(range(100, 10001, 100))  # 从 100 到 10,000，步长为 100
REQUESTS_PER_USER = 1  # 每个用户发送的插入请求数量
QUERY_COUNT = 100  # 每次测试后执行的查询次数


async def send_store_action(session, characterId, action_id):
    """
    发送单个 /store_action 请求，并返回响应时间。
    """
    url = f"{API_BASE_URL}/store_action"
    data = {
        "characterId": characterId,
        "meta_action": "Test Action",
        "description": "This is a test action",
        "response": True,
        "action_id": action_id,
        "prev_action": action_id - 1 if action_id > 1 else None,
    }
    start_time = time.perf_counter()
    try:
        async with session.post(url, json=data) as response:
            await response.json()
    except Exception as e:
        print(f"请求失败，characterId={characterId}, action_id={action_id}: {e}")
        return None  # 返回 None 表示请求失败
    end_time = time.perf_counter()
    return end_time - start_time


async def send_get_action(session, characterId, action_id):
    """
    发送单个 /get_action 请求，并返回响应时间。
    """
    url = f"{API_BASE_URL}/get_action"
    data = {"characterId": characterId, "action_id": action_id}
    start_time = time.perf_counter()
    try:
        async with session.post(url, json=data) as response:
            await response.json()
    except Exception as e:
        print(f"查询失败，characterId={characterId}, action_id={action_id}: {e}")
        return None  # 返回 None 表示查询失败
    end_time = time.perf_counter()
    return end_time - start_time


async def run_load_test(concurrent_users, requests_per_user=1):
    """
    运行负载测试，模拟指定数量的并发用户，每个用户发送一定数量的插入请求。
    返回插入操作的响应时间列表。
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(concurrent_users):
            characterId = random.randint(1, 1000000)
            for _ in range(requests_per_user):
                # 这里不再随机生成 action_id，而是由调用方传入
                action_id = None  # 由外部控制
                task = asyncio.create_task(
                    send_store_action(session, characterId, action_id)
                )
                tasks.append(task)
        response_times = await asyncio.gather(*tasks)
    return response_times


async def run_insert_test(session, data_volume):
    """
    运行插入测试，插入指定数量的数据，action_id 线性增长。
    返回插入操作的响应时间列表和插入的 (characterId, action_id) 对。
    """
    tasks = []
    inserted_pairs = []
    for i in range(1, data_volume + 1):
        characterId = random.randint(1, 1000000)
        action_id = i  # 线性增长的 action_id
        task = asyncio.create_task(send_store_action(session, characterId, action_id))
        tasks.append(task)
        inserted_pairs.append((characterId, action_id))
    response_times = await asyncio.gather(*tasks)
    return response_times, inserted_pairs


async def run_query_test(session, query_pairs):
    """
    运行查询测试，发送指定数量的查询请求。
    `query_pairs` 是包含 (characterId, action_id) 元组的列表。
    返回查询操作的响应时间列表。
    """
    tasks = []
    for characterId, action_id in query_pairs:
        task = asyncio.create_task(send_get_action(session, characterId, action_id))
        tasks.append(task)
    response_times = await asyncio.gather(*tasks)
    return response_times


def reset_database():
    """
    重置数据库中的 action 集合，通过删除并重新创建。
    """
    app = DatabaseSetupApp()
    app.setup_action_database()


def main():
    """
    主函数，执行容量测试。
    """
    insert_times = []
    query_times = []
    insert_success_rates = []
    query_success_rates = []

    for data_volume in DATA_VOLUMES:
        print(f"\n正在测试 {data_volume} 条文档")

        # 在每次测试前重置数据库
        reset_database()

        # 开始插入测试
        loop = asyncio.get_event_loop()

        async def insert_and_collect():
            async with aiohttp.ClientSession() as session:
                insert_response_times, inserted_pairs = await run_insert_test(
                    session, data_volume
                )
                return insert_response_times, inserted_pairs

        start_insert = time.perf_counter()
        insert_response_times, inserted_pairs = loop.run_until_complete(
            insert_and_collect()
        )
        end_insert = time.perf_counter()

        # 计算总插入时间
        total_insert_time = end_insert - start_insert
        insert_times.append(total_insert_time)

        # 计算插入成功率
        successful_inserts = sum(1 for rt in insert_response_times if rt is not None)
        insert_success_rate = (
            (successful_inserts / len(insert_response_times)) * 100
            if len(insert_response_times) > 0
            else 0
        )
        insert_success_rates.append(insert_success_rate)

        print(f"成功插入 {successful_inserts}/{data_volume} 条文档。")
        print(
            f"总插入时间: {total_insert_time:.4f} 秒 | 插入成功率: {insert_success_rate:.2f}%"
        )

        # 准备查询测试
        # 从已插入的文档中随机选取 QUERY_COUNT 条进行查询
        if len(inserted_pairs) < QUERY_COUNT:
            query_pairs = inserted_pairs
        else:
            query_pairs = random.sample(inserted_pairs, QUERY_COUNT)

        # 开始查询测试
        async def query_and_collect():
            async with aiohttp.ClientSession() as session:
                query_response_times = await run_query_test(session, query_pairs)
                return query_response_times

        start_query = time.perf_counter()
        query_response_times = loop.run_until_complete(query_and_collect())
        end_query = time.perf_counter()

        # 计算总查询时间和平均查询时间
        total_query_time = end_query - start_query
        successful_queries = sum(1 for qt in query_response_times if qt is not None)
        query_success_rate = (
            (successful_queries / len(query_response_times)) * 100
            if len(query_response_times) > 0
            else 0
        )
        avg_query_time = (
            (total_query_time / successful_queries)
            if successful_queries > 0
            else float("inf")
        )
        query_times.append(avg_query_time)
        query_success_rates.append(query_success_rate)

        print(f"成功执行 {successful_queries}/{len(query_response_times)} 次查询。")
        print(
            f"总查询时间: {total_query_time:.4f} 秒 | 平均查询时间: {avg_query_time:.4f} 秒 | 查询成功率: {query_success_rate:.2f}%"
        )

    # 绘制插入时间与文档数量的关系图
    plt.figure(figsize=(12, 6))
    plt.plot(DATA_VOLUMES, insert_times, marker="o", label="总插入时间")
    plt.xlabel("文档数量")
    plt.ylabel("总插入时间 (秒)")
    plt.title("容量测试：插入时间与文档数量关系")
    plt.grid(True)
    plt.legend()
    plt.savefig("capacity_test_insert_time.png")
    plt.show()

    # 绘制平均查询时间与文档数量的关系图
    plt.figure(figsize=(12, 6))
    plt.plot(DATA_VOLUMES, query_times, marker="o", color="green", label="平均查询时间")
    plt.xlabel("文档数量")
    plt.ylabel("平均查询时间 (秒)")
    plt.title("容量测试：平均查询时间与文档数量关系")
    plt.grid(True)
    plt.legend()
    plt.savefig("capacity_test_query_time.png")
    plt.show()

    # 绘制插入成功率与文档数量的关系图
    plt.figure(figsize=(12, 6))
    plt.plot(
        DATA_VOLUMES,
        insert_success_rates,
        marker="x",
        color="red",
        label="插入成功率 (%)",
    )
    plt.xlabel("文档数量")
    plt.ylabel("插入成功率 (%)")
    plt.title("容量测试：插入成功率与文档数量关系")
    plt.grid(True)
    plt.legend()
    plt.savefig("capacity_test_insert_success_rate.png")
    plt.show()

    # 绘制查询成功率与文档数量的关系图
    plt.figure(figsize=(12, 6))
    plt.plot(
        DATA_VOLUMES,
        query_success_rates,
        marker="x",
        color="orange",
        label="查询成功率 (%)",
    )
    plt.xlabel("文档数量")
    plt.ylabel("查询成功率 (%)")
    plt.title("容量测试：查询成功率与文档数量关系")
    plt.grid(True)
    plt.legend()
    plt.savefig("capacity_test_query_success_rate.png")
    plt.show()

    print("\n容量测试完成。相关图表已保存为 PNG 文件。")


if __name__ == "__main__":
    main()
