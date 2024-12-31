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
        
        # create tasks for conversation agent
        self.msg_processor_task = asyncio.create_task(self.msg_processor())
        self.reply_message_task = asyncio.create_task(self.reply_message())
        self.clear_readonly_task = asyncio.create_task(self.clear_readonly())
        self.plan_start_task = asyncio.create_task(self.run_workflow())

        self.logger.info(f"User {self.user_id} conversation client initialized")
        return self

    # listener
    async def listener(self, data):
        if self.is_initial:
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

        message_code = data.get("messageCode")
        if not message_code:
            self.logger.error(f"User {self.user_id}: Unknown message: {data}")
        elif message_code < 100:
            pass  # ignore messages for agent_instance
        else:
            try:
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

    # distinguishes between agent tasks, read-only tasks, and to-agent tasks
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
                # get current time
                hours = time_object.hour
                minutes = time_object.minute
                if (
                    hours == 0 and minutes <= 35
                ):  
                    self.plan_signal = True
                    self.logger.info(f"🏃 User {self.user_id}: IT'S A NEW DAY!")
            elif (
                message_name == "read_only"
            ): 
                self.logger.info(
                    f"User {self.user_id} receives a read-only message: {msg['data']}."
                )
                current_time = calculate_game_time(real_time=datetime.now())

                # store the message to database
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

                # check whether the same conversation is recorded in local server
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
            elif message_name == "to_agent":  
                self.logger.info(
                    f"User {self.user_id} receives a message and is waiting for agent response: {msg['data']}."
                )
                await check_conversation_state(
                    self.state, msg["data"]
                )  
            elif message_name == "prompt_modification":  
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

    # reply task
    async def reply_message(self):
        while True:
            if self.state["waiting_response"].qsize() == 0:
                await asyncio.sleep(
                    10
                )  
                continue
            await generate_response(self.state)

    # Schedule the storage of the read-only message list and generate impression
    async def clear_readonly(self):
        while True:
            if len(self.state["ongoing_task"]) != 0:
                self.logger.info(f"🏃 User {self.user_id}: handling read-only messages...")
                await handling_readonly_conversation(self.state)
            await asyncio.sleep(300)  # set the schedule

    # plan-and-start workflow
    async def run_workflow(self):
        while True:
            if self.plan_signal:
                try:
                    self.logger.info(
                        f"🏃 User {self.user_id}: Begin planning for today's conversations..."
                    )
                    await self.graph.ainvoke(self.state, config=self.graph_config)
                    self.plan_signal = False
                    day, hour, minute = calculate_game_time(real_time=datetime.now())
                    time_gap = (24-hour)*60*60+(0-minute)*60+100
                    self.logger.info(
                        f"Next planning workflow will start in {time_gap} seconds."
                    )
                    await asyncio.sleep(time_gap)
                    self.logger.info(f"🏃 User {self.user_id}: IT'S A NEW DAY!")
                    self.plan_signal = True
                except Exception as e:
                    self.logger.error(
                        f"User {self.user_id} Error in conversation planning and starting workflow: {e}"
                    )
                    self.plan_signal = False
            else:
                await asyncio.sleep(10)

