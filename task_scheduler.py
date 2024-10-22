import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum, auto
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import JobLookupError
from llm_tools.single_command_generator import CommandGenerator


class TaskStatus(Enum):
    PENDING = auto()  # 默认状态，等待时间到达
    RUNNING = auto()  # 任务执行中
    COMPLETED = auto()  # 任务已完成
    FAILED = auto()  # 任务执行失败
    BLOCKED = auto()  # 挂起状态，有前置任务待完成


class Task:
    def __init__(
        self, id, task_description, constraints, start_time, duration, priority
    ):
        self.id = id
        self.task_description = task_description
        self.constraints = constraints
        self.start_time = start_time
        self.duration = duration  # *
        self.priority = priority  # *
        self.status = TaskStatus.PENDING  # *

    async def execute(self, websocket, character_id):
        """执行任务
        发送任务描述到LLM，生成任务执行的websocket请求体，发送请求体到游戏端，等待响应
        根据constraint和当前游戏上下文总结出任务失败原因，将状态设置为BLOCKED，并重新规划任务列表
        """
        command_generator = CommandGenerator()
        request_body = command_generator.generate_single_command_body(
            self.task_description, character_id
        )
        response = await websocket.send(json.dumps(request_body))
        print(f"Task {self.id} executed with response: {response}")
        self.status = TaskStatus.COMPLETED

    def create_message(self, character_id, message_name, message_code, **kwargs):
        return {
            "characterId": character_id,
            "messageCode": message_code,
            "messageName": message_name,
            "data": kwargs,
        }


class TaskScheduler:
    def __init__(self, websocket, character_id):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.character_id = character_id
        self.websocket = websocket

    async def schedule_task(self, task):
        self.scheduler.add_job(
            self.execute_task,
            trigger=DateTrigger(run_date=task.start_time),
            args=[task],
            id=str(task.id),
            replace_existing=True,
        )
        print(f"Task {task.id} scheduled to start at {task.start_time}")

    async def execute_task(self, task):
        await task.execute(self.websocket, self.character_id)
        task.status = TaskStatus.COMPLETED

    async def update_task(self, task):
        current_time = datetime.now()
        # if task.start_time > current_time + timedelta(minutes=10):
        if task.start_time > current_time:
            await self.schedule_task(task)
            print(f"Task {task.id} updated or added.")
        else:
            print(f"Task {task.id} not added. Start time is in the past.")

    async def remove_task(self, task_id):
        try:
            self.scheduler.remove_job(str(task_id))
            print(f"Task {task_id} removed.")
        except JobLookupError:
            print(f"Task {task_id} not found.")

    def get_all_tasks(self):
        return [job.args[0] for job in self.scheduler.get_jobs()]

    def get_next_task(self):
        jobs = self.scheduler.get_jobs()
        return jobs[0].args[0] if jobs else None


# 示例使用
async def main():
    scheduler = TaskScheduler(None)

    # 添加一些示例任务
    task1 = Task(
        id=1,
        task_description="任务1",
        constraints=None,
        start_time=datetime.now() + timedelta(seconds=10),
        duration=5,
        priority=1,
    )
    await scheduler.update_task(task1)

    task2 = Task(
        id=2,
        task_description="任务2",
        constraints=None,
        start_time=datetime.now() + timedelta(seconds=20),
        duration=3,
        priority=2,
    )
    await scheduler.update_task(task2)

    task3 = Task(
        id=3,
        task_description="任务3",
        constraints=None,
        start_time=datetime.now() + timedelta(seconds=30),
        duration=4,
        priority=3,
    )
    await scheduler.update_task(task3)

    # 打印所有任务
    print("所有已安排的任务:")
    for task in scheduler.get_all_tasks():
        print(f"任务 {task.id}: 开始时间 {task.start_time}")

    # 获取并打印下一个任务
    next_task = scheduler.get_next_task()
    print(f"下一个任务: 任务 {next_task.id}, 开始时间 {next_task.start_time}")

    # 更新任务2的开始时间
    task2.start_time = datetime.now() + timedelta(seconds=40)
    await scheduler.update_task(task2)
    print(f"任务2已更新，新的开始时间: {task2.start_time}")

    # 再次打印所有任务
    print("更新后的所有任务:")
    for task in scheduler.get_all_tasks():
        print(f"任务 {task.id}: 开始时间 {task.start_time}")

    # 等待任务执行
    await asyncio.sleep(60)  # 运行60秒


if __name__ == "__main__":
    asyncio.run(main())
