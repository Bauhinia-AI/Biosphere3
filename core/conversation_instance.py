import asyncio
from conversation_srv.conversation_engines import *
from conversation_srv.conversation_model import *
from langgraph.graph import StateGraph, START, END
import os
import asyncio
from pprint import pprint


class ConversationInstance:
    def __init__(self, user_id, websocket=None):
        self.user_id = user_id
        self.websocket = websocket
        self.plan_signal = False
        self.is_initial = True
        self.state = initialize_conversation_state(self.user_id, self.websocket)
        self.graph = start_conversation_workflow()
        self.graph_config = {"recursion_limit": 1000}
        self.msg_processor_task = None
        self.reply_message_task = None
        self.clear_readonly_task = None
        self.plan_start_task = None
        self.logger = logger.bind(conversation_instance=True)

    @classmethod
    async def create(cls, user_id, websocket=None):
        self = cls(user_id, websocket)
        # 在这里如果有需要可以进行额外的异步初始化

        # 创建任务
        self.msg_processor_task = asyncio.create_task(self.msg_processor())
        self.reply_message_task = asyncio.create_task(self.reply_message())
        self.clear_readonly_task = asyncio.create_task(self.clear_readonly())
        self.plan_start_task = asyncio.create_task(self.run_workflow())
        # self.listener_task = asyncio.create_task(self.listener())

        self.logger.info(f"User {self.user_id} conversation client initialized")
        return self

    # listener，监听消息，收入message_queue队列等待处理
    async def listener(self, data):
        # print("Listener started!")
        if self.is_initial:
            # 进一步检查今天是否已经进行过对话，避免对话过多
            current_time = calculate_game_time(real_time=datetime.now())
            current_day = current_time[0]
            check_data = {"characterId": self.user_id, "day": current_day}
            check_response = make_api_request_sync(
                "GET", "/conversation_memory/", params=check_data
            )
            if not check_response["data"]:
                self.plan_signal = True
            elif len(check_response["data"][0]["started"]) < 3:
                self.plan_signal = True
            self.is_initial = False
        websocket = self.state["websocket"]
        message_queue = self.state["message_queue"]

        try:
            # data = json.loads(message)
            await message_queue.put(data)
            self.logger.info(
                f"👂 User {self.user_id}: Received conversation message: {data} and put into queue"
            )
            self.logger.info(
                f"🧾 User {self.user_id} conversation message queue: {self.state['message_queue']}"
            )
        except websockets.ConnectionClosed:
            self.logger.error(f"User {self.user_id}: WebSocket connection closed.")

        except Exception as e:
            self.logger.error(f"User {self.user_id}: Error in listener: {e}")

    # 任务分拣器，区分agent任务，只读任务和主动发起对话任务
    async def msg_processor(self):
        self.logger.info("💬 CONVERSATION_INSTANCE: msg_processor started!")
        while True:
            msg = await self.state["message_queue"].get()
            message_name = msg.get("messageName")
            message_code = msg.get("messageCode")
            self.logger.info(f"💬 CONVERSATION_INSTANCE: User {self.user_id}: received {message_name} message: {msg}")
            if message_name == "gameTime":
                data = msg.get("data")
                time_object = datetime.strptime(data["gameTime"], "%H:%M")
                # 获取小时和分钟
                hours = time_object.hour
                minutes = time_object.minute
                if (
                    hours == 0 and minutes <= 35
                ):  # 如果每隔现实5分钟发送一次时间，则0:35的时间是每天第一条时间消息
                    self.plan_signal = True
                    self.logger.info(f"🏃 User {self.user_id}: IT'S A NEW DAY!")
                # self.plan_start_task = asyncio.create_task(self.run_workflow())
                # await asyncio.sleep(5)  # 等待创建任务
                # await self.plan_start_task
            elif (
                message_name == "read_only"
            ):  # 当前user被玩家夺舍，只需要储存获得的消息，不需要触发回复流程
                self.logger.info(
                    f"User {self.user_id} receives a read-only message: {msg['data']}."
                )
                current_time = calculate_game_time(real_time=datetime.now())

                # 存储对话到数据库
                readonly_data = {
                    "from_id": msg["data"]["from_id"],
                    "to_id": msg["data"]["to_id"],
                    "message": list(msg["data"]["latest_message"].values())[0],
                    "start_day": current_time[0],
                    "start_time": msg["data"]["start_time"],
                    "send_gametime": msg["data"]["send_gametime"],
                    "send_realtime": msg["data"]["send_realtime"]
                }
                readonly_response = make_api_request_sync(
                    "POST", "/conversation/", data=readonly_data
                )
                self.logger.info(
                    f"A read-only conversation is saved to database: {readonly_response['message']}"
                )

                # 检查列表中是否有同一个对话条目，有则更新，没有则添加
                search_ids = [msg["data"]["from_id"], msg["data"]["to_id"]]
                search_ids_inverse = [msg["data"]["to_id"], msg["data"]["from_id"]]
                search_start_time = msg["data"]["start_time"]
                search_result = [
                    index
                    for index, item in enumerate(self.state["ongoing_task"])
                    if (
                        item["characterIds"] == search_ids
                        or item["characterIds"] == search_ids_inverse
                    )
                    and item["start_time"] == search_start_time
                ]
                if len(search_result) == 0:
                    self.state["ongoing_task"].append(
                        {
                            "characterIds": [
                                msg["data"]["from_id"],
                                msg["data"]["to_id"],
                            ],
                            "start_time": msg["data"]["start_time"],
                            "start_day": current_time[0],
                            "dialogue": [msg["data"]["latest_message"]],
                        }
                    )
                    self.logger.info(
                        f"User {self.user_id}: A new conversation event just happened."
                    )
                else:
                    self.state["ongoing_task"][search_result[0]]["dialogue"].append(msg["data"]["latest_message"])
                    self.logger.info(
                        f"User {self.user_id}: An existing conversation event continues."
                    )
                self.logger.info(
                    f"User {self.user_id}: the conversation is recorded in the instance and is waited to be handled."
                )
            elif message_name == "to_agent":  # 当前玩家由agent接管，需要回复的消息
                self.logger.info(
                    f"User {self.user_id} receives a message and is waiting for agent response: {msg['data']}."
                )
                await check_conversation_state(
                    self.state, msg["data"]
                )  # 判断对话是否结束，分别处理
            elif message_name == "prompt_modification":  # 改prompt
                new_prompt_data = msg.get("data")
                self.logger.info(f"User {self.user_id}: new prompts received.")
                if "topic_planner_prompt" in new_prompt_data:
                    new_topic_prompt = new_prompt_data["topic_planner_prompt"]
                    self.state["prompt"]["topic_requirements"] = new_topic_prompt
                if "responser_prompt" in new_prompt_data:
                    new_impression_prompt = new_prompt_data["responser_prompt"]
                    self.state["prompt"]["impression_impact"].update(
                        new_impression_prompt
                    )
                self.logger.info(
                    f"User {self.user_id}'s new prompts are: {self.state['prompt']}"
                )
            elif message_code < 100:
                pass  # 忽略agent_instance的消息
            else:
                self.logger.error(f"User {self.user_id}: Unknown message: {message_name}")

    # 回复消息任务队列
    async def reply_message(self):
        while True:
            if self.state["waiting_response"].qsize() == 0:
                await asyncio.sleep(
                    10
                )  # 如果当前没有等待回复的消息，10秒后重新检查队列
                continue
            await generate_response(self.state)

    # 定时对read only的消息列表进行数据库存储及生成印象工作
    async def clear_readonly(self):
        while True:
            if len(self.state["ongoing_task"]) != 0:
                self.logger.info(f"🏃 User {self.user_id}: handling read-only messages...")
                await handling_readonly_conversation(self.state)
            await asyncio.sleep(300)  # 每隔5分钟处理一次

    # 唤醒规划和主动对话模块
    async def run_workflow(self):
        while True:
            if self.plan_signal:
                try:
                    self.logger.info(
                        f"🏃 User {self.user_id}: Begin planning for today's conversations..."
                    )
                    await self.graph.ainvoke(self.state, config=self.graph_config)
                    self.plan_signal = False
                    # self.plan_start_task.cancel()
                    # try:
                    #     await self.plan_start_task
                    # except asyncio.CancelledError:
                    #     self.logger.info(f"User {self.user_id}: today's plan-and-start task is finished.")
                except Exception as e:
                    self.logger.error(
                        f"User {self.user_id} Error in conversation planning and starting workflow: {e}"
                    )
                    self.plan_signal = False
            else:
                await asyncio.sleep(10)
            # current_time = calculate_game_time()
            # time_sleep = ((24-current_time[1])*60*60+(0-current_time[2])*60)//7+100
            # hour = time_sleep//3600
            # minute = (time_sleep-hour*3600)//60
            # second = time_sleep-hour*3600-minute*60
            # self.logger.info(f"User {self.user_id}: time before next plan task is {hour} hours {minute} minutes and {second} seconds.")
            # await asyncio.sleep(time_sleep)  # 设置规划间隔时长


"""
async def main():
    a_instance = ConversationInstance(user_id=1, websocket=None)

if __name__ == "__main__":
    asyncio.run(main())
"""
