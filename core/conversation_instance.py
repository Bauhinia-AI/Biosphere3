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
        self.plan_signal = False  # 对话规划的信号
        self.is_initial = (
            True  # 控制对话规划的发生时间，设定为收到第一条消息，而不是加载实例的时候
        )

        # 初始化对话实例
        self.state = initialize_conversation_state(self.user_id, self.websocket)

        # 数据竞争时，锁住state
        # self.state_lock = asyncio.Lock()
        # self.websocket_lock = asyncio.Lock()

        self.graph = start_conversation_workflow()
        self.graph_config = {"recursion_limit": 1000}

        # 三个协程
        # self.listener_task = asyncio.create_task(self.listener())
        self.msg_processor_task = asyncio.create_task(self.msg_processor())
        self.reply_message_task = asyncio.create_task(self.reply_message())
        self.clear_readonly_task = asyncio.create_task(self.clear_readonly())
        self.plan_start_task = asyncio.create_task(self.run_workflow())
        # self.plan_start_task = None
        logger.info(f"User {self.user_id} conversation client initialized")

    # listener，监听消息，收入message_queue队列等待处理
    async def listener(self, message):
        # print("Listener started!")
        if self.is_initial:
            self.plan_signal = True
            self.is_initial = False
        websocket = self.state["websocket"]
        message_queue = self.state["message_queue"]

        try:
            data = json.loads(message)
            await message_queue.put(data)
            logger.info(
                f"👂 User {self.user_id}: Received conversation message: {data} and put into queue"
            )
            logger.info(
                f"🧾 User {self.user_id} conversation message queue: {self.state['message_queue']}"
            )
        except websockets.ConnectionClosed:
            logger.error(f"User {self.user_id}: WebSocket connection closed.")

        except Exception as e:
            logger.error(f"User {self.user_id}: Error in listener: {e}")

    # 任务分拣器，区分agent任务，只读任务和主动发起对话任务
    async def msg_processor(self):
        # print("msg_processor started!")
        while True:
            msg = await self.state["message_queue"].get()
            message_name = msg.get("messageName")
            message_code = msg.get("messageCode")

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
                    logger.info(f"🏃 User {self.user_id}: IT'S A NEW DAY!")
                # self.plan_start_task = asyncio.create_task(self.run_workflow())
                # await asyncio.sleep(5)  # 等待创建任务
                # await self.plan_start_task
            elif (
                message_name == "read_only"
            ):  # 当前user被玩家夺舍，只需要储存获得的消息，不需要触发回复流程
                logger.info(
                    f"User {self.user_id} receives a read-only message: {msg['data']}."
                )
                current_time = calculate_game_time()

                # 存储对话到数据库，先查询是否有同一条
                readonly_data = {
                    "characterIds": [msg["data"]["from_id"], msg["data"]["to_id"]],
                    "dialogue": msg["data"]["dialogue"],
                    "start_day": current_time[0],
                    "start_time": msg["data"]["start_time"],
                }
                readonly_response = make_api_request_sync(
                    "POST", "/conversations/store", data=readonly_data
                )
                logger.info(
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
                            "dialogue": msg["data"]["dialogue"],
                        }
                    )
                    logger.info(
                        f"User {self.user_id}: A new conversation event just happened."
                    )
                else:
                    self.state["ongoing_task"][search_result[0]] = {
                        "characterIds": [msg["data"]["from_id"], msg["data"]["to_id"]],
                        "start_time": msg["data"]["start_time"],
                        "start_day": current_time[0],
                        "dialogue": msg["data"]["dialogue"],
                    }
                    logger.info(
                        f"User {self.user_id}: An existing conversation event continues."
                    )
                logger.info(
                    f"User {self.user_id}: the conversation is recorded in the instance and is waited to be handled."
                )
            elif message_name == "to_agent":  # 当前玩家由agent接管，需要回复的消息
                logger.info(
                    f"User {self.user_id} receives a message and is waiting for agent response: {msg['data']}."
                )
                await check_conversation_state(
                    self.state, msg["data"]
                )  # 判断对话是否结束，分别处理
            elif message_name == "prompt_modification":  # 改prompt
                new_prompt_data = msg.get("data")
                logger.info(f"User {self.user_id}: new prompts received.")
                new_topic_prompt = new_prompt_data["topic_planner_prompt"]
                new_impression_prompt = new_prompt_data["responser_prompt"]
                self.state["prompt"]["topic_requirements"] = new_topic_prompt
                self.state["prompt"]["impression_impact"].update(new_impression_prompt)
                logger.info(
                    f"User {self.user_id}'s new prompts are: {self.state['prompt']}"
                )
            elif message_code < 100:
                pass  # 忽略agent_instance的消息
            else:
                logger.error(f"User {self.user_id}: Unknown message: {message_name}")

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
                logger.info(f"🏃 User {self.user_id}: handling read-only messages...")
                await handling_readonly_conversation(self.state)
            await asyncio.sleep(120)  # 每隔2分钟处理一次

    # 唤醒规划和主动对话模块
    async def run_workflow(self):
        while True:
            if self.plan_signal:
                try:
                    logger.info(
                        f"🏃 User {self.user_id}: Begin planning for today's conversations..."
                    )
                    await self.graph.ainvoke(self.state, config=self.graph_config)
                    self.plan_signal = False
                    # self.plan_start_task.cancel()
                    # try:
                    #     await self.plan_start_task
                    # except asyncio.CancelledError:
                    #     logger.info(f"User {self.user_id}: today's plan-and-start task is finished.")
                except Exception as e:
                    logger.error(
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
            # logger.info(f"User {self.user_id}: time before next plan task is {hour} hours {minute} minutes and {second} seconds.")
            # await asyncio.sleep(time_sleep)  # 设置规划间隔时长


"""
async def main():
    a_instance = ConversationInstance(user_id=1, websocket=None)

if __name__ == "__main__":
    asyncio.run(main())
"""
