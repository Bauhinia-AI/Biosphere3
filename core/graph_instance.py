import sys

sys.path.append(".")

import asyncio
import json
import time
from datetime import datetime

from pprint import pprint

from loguru import logger
import websockets
from langgraph.graph import StateGraph

from core.agent_srv.node_engines import (
    generate_daily_objective,
    generate_meta_action_sequence,
    replan_action,
    sensing_environment,
    generate_change_job_cv,
    generate_character_arc,
    generate_daily_reflection,
)
from core.agent_srv.node_model import RunningState
from core.agent_srv.utils import get_initial_state_from_db


class LangGraphInstance:
    """
    Manages the language graph instance for a specific user.

    Initializes the state, sets up asynchronous tasks for message processing,
    event scheduling, and runs the workflow graph.

    Args:
        user_id (str): The unique identifier for the user.
        websocket (WebSocket, optional): The WebSocket connection for communication.
    """

    def __init__(self, user_id, websocket=None):
        self.user_id = user_id
        self.websocket = websocket
        self.signal = None
        self.state = {}  # 初始化为空字典

        self.connection_stats = {}
        # 数据竞争时，锁住state
        self.websocket_lock = asyncio.Lock()
        self.graph = self._get_workflow_with_listener()
        self.graph_config = {"recursion_limit": 1e10}
        self.action_result = []
        self.logger = logger.bind(agent_instance=True)
        self.logger.info(f"LangGraphInstance for user {self.user_id} initialized.")

        # 初始化任务为 None，稍后在异步工厂方法中创建
        self.msg_processor_task = None
        self.event_scheduler_task = None
        self.queue_visualizer_task = None
        self.task = None

    @classmethod
    async def create(cls, user_id, websocket=None):
        """
        异步工厂方法，用于创建并初始化 LangGraphInstance 的实例。

        Args:
            user_id (str): 用户的唯一标识符。
            websocket (WebSocket, optional): 用于通信的 WebSocket 连接。

        Returns:
            LangGraphInstance: 初始化完成的类实例。
        """
        self = cls(user_id, websocket)
        # 异步获取初始状态
        initial_state = await get_initial_state_from_db(user_id, websocket)
        if not initial_state:
            initial_state = {}
        self.state = initial_state

        # logger.info(f"🔍 User {self.user_id} state: {self.state}")

        self.state["instance"] = self
        self.connection_stats = {}
        self.websocket_lock = asyncio.Lock()
        self.graph = self._get_workflow_with_listener()
        self.graph_config = {"recursion_limit": 1e10}
        self.action_result = []

        # 初始化异步任务
        self.msg_processor_task = asyncio.create_task(self.msg_processor())
        self.event_scheduler_task = asyncio.create_task(self.event_scheduler())
        # self.queue_visualizer_task = asyncio.create_task(self.queue_visualizer())
        self.state["event_queue"].put_nowait("PLAN")
        self.logger.info(f"User {self.user_id} workflow initialized")
        self.task = asyncio.create_task(self.a_run())

        return self

    async def msg_processor(self):
        """
        Continuously processes incoming messages from the message queue.

        Handles different types of messages such as action results, prompt modifications,
        one-step triggers, and checks. Updates the state accordingly and manages
        event scheduling based on message content.
        """
        while True:

            msg = await self.state["message_queue"].get()
            message_name = msg.get("messageName")
            message_code = msg.get("messageCode")
            # self.logger.info(f"㊗️ 处理信息信息 User {self.user_id} message: {msg}")
            if message_name == "actionresult":
                # 处理动作结果
                self.state["decision"]["action_result"].append(msg["data"])

                if msg["data"]["result"] is False:
                    try:
                        # 如果失败，则往false_action_queue里放
                        self.logger.info(
                            f"❌❌❌❌❌ User {self.user_id}: Put REPLAN into event_queue"
                        )
                        self.state["false_action_queue"].put_nowait(msg["data"])
                        self.state["event_queue"].put_nowait("REPLAN")
                    except Exception as e:
                        self.logger.error(
                            f"User {self.user_id}: Error putting REPLAN into event_queue: {e}"
                        )

                self.logger.info(
                    f"🏃 User {self.user_id}: Received action result: {msg['data']}"
                )
                # 把action_result 和本地時間 记录下来
                self.action_result.append(
                    {"action_result": msg["data"], "timestamp": datetime.now()}
                )
            elif message_name == "cv_submission":
                await generate_change_job_cv(self.state["instance"], msg)
            elif message_name == "onestep":
                self.state["event_queue"].put_nowait("PLAN")

            elif message_name == "check":
                pprint(self.state["decision"]["action_result"])
            elif message_code >= 100:
                pass  # 忽略掉对话系统的消息
            else:
                self.logger.error(
                    f"User {self.user_id}: Unknown message: {message_name}"
                )

    async def event_scheduler(self):
        """
        Schedules and manages events based on the state of action results and timings.

        Continuously checks the latest action result and the elapsed time to decide whether
        to enqueue new events such as "PLAN" or "REFLECT". It also monitors the total running
        time to perform periodic reflections.

        Raises:
            Exception: Logs and terminates if any unexpected error occurs during event scheduling.
        """
        # start timer
        try:
            start_time = time.time()
            while True:
                if self.signal == "TERMINATE":
                    self.logger.error(
                        "⛔ Task event_scheduler terminated due to termination signal."
                    )
                    break
                await asyncio.sleep(1)
                # if len(self.action_result) == 0:
                #     continue
                # # 如果action_result中最後一條信息不為sleep且和现在时间相差十秒，就往event_queue里放plan
                # if self.action_result[-1]["action_result"][
                #     "actionName"
                # ] != "sleep" and datetime.now() - self.action_result[-1][
                #     "timestamp"
                # ] > timedelta(
                #     seconds=5
                # ):
                #     self.state["event_queue"].put_nowait("PLAN")
                # PLAN
                if time.time() - start_time > 300:
                    # BUG REFLECT raise error
                    self.state["event_queue"].put_nowait("PLAN")
                elif time.time() - start_time > 600:
                    self.state["event_queue"].put_nowait("DAILY_REFLECTION")
                elif time.time() - start_time > 900:
                    self.state["event_queue"].put_nowait("CHARACTER_ARC")

                start_time = time.time()
                # self.state["event_queue"].put_nowait("REFLECT")
                # self.state["event_queue"].put_nowait("PLAN")
                # self.logger.info(f"🆕 User {self.user_id}: Put PLAN into event_queue")
        except Exception as e:
            self.logger.error(f"User {self.user_id}: Error in event_scheduler: {e}")

    async def queue_visualizer(self):
        """
        Periodically logs the state of various queues for monitoring purposes.
        """
        while True:
            await asyncio.sleep(10)
            if self.signal == "TERMINATE":
                self.logger.error(
                    "⛔ Task queue_visualizer terminated due to termination signal."
                )
                break
            self.logger.info(
                f"🧾 User {self.user_id} event_queue: {self.state['event_queue']}"
            )
            # self.logger.info(
            #     f"🧾 User {self.user_id} message_queue: {self.state['message_queue']}"
            # )
            self.logger.info(
                f"❌ User {self.user_id} false_action_queue: {self.state['false_action_queue']}"
            )

    async def event_router(self, state: RunningState):
        """
        Routes events from the event queue to the appropriate workflow nodes.

        This method continuously listens for events in the `event_queue` and determines
        the next workflow node to invoke based on the event type. It handles events
        such as "PLAN", "REFLECT", and "REPLAN" by mapping them to their corresponding
        workflow nodes.

        Args:
            state (RunningState): The current running state of the graph instance.

        Returns:
            str: The name of the next workflow node to invoke.
        """
        while True:
            event = await state["event_queue"].get()
            self.logger.info(f"🚦 User {self.user_id}: Event: {event}")

            if event == "PLAN":
                return "Objectives_planner"
            elif event == "CHARACTER_ARC":
                return "Character_Arc"
            elif event == "REPLAN":
                return "Replan_Action"
            elif event == "DAILY_REFLECTION":
                return "Daily_Reflection"
            else:
                self.logger.error(f"User {self.user_id}: Unknown event: {event}")
            # await self.state['message_queue'].task_done()

    def _get_workflow_with_listener(self):
        workflow = StateGraph(RunningState)
        workflow.add_node("Sensing_Route", sensing_environment)
        workflow.add_node("Objectives_planner", generate_daily_objective)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("Character_Arc", generate_character_arc)
        workflow.add_node("Daily_Reflection", generate_daily_reflection)

        workflow.add_node("Replan_Action", replan_action)

        workflow.set_entry_point("Sensing_Route")
        workflow.add_conditional_edges("Sensing_Route", self.event_router)

        workflow.add_edge("Replan_Action", "Sensing_Route")

        # 定义工作流的路径
        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge("meta_action_sequence", "Sensing_Route")
        workflow.add_edge("Character_Arc", "Sensing_Route")
        workflow.add_edge("Daily_Reflection", "Sensing_Route")

        return workflow.compile()

    async def a_run(self):
        """
        Executes the workflow graph asynchronously.

        Invokes the graph with the current state and configuration.
        Handles termination signals and logs any exceptions that occur during execution.
        """
        try:
            await self.graph.ainvoke(self.state, config=self.graph_config)
        except Exception as e:
            self.signal = "TERMINATE"

            self.logger.error(f"User {self.user_id} Error in workflow: {e}")
            self.logger.error("⛔ Task a_run terminated due to termination signal.")
            self.task.cancel()

    async def send_message(self, message):
        """
        Sends a message through the WebSocket connection.

        Args:
            message (dict): The message to send.
        """
        async with self.websocket_lock:
            if self.websocket is None or self.websocket.closed:
                self.logger.error(
                    f"⛔ User {self.user_id}: WebSocket is not connected."
                )
                self.signal = "TERMINATE"
                return
            try:
                await self.websocket.send(json.dumps(message))
                self.logger.info(f"📤 User {self.user_id}: Sent message: {message}")
            except websockets.ConnectionClosed:
                self.logger.warning(
                    f"User {self.user_id}: WebSocket connection closed during send."
                )
                # TODO 这里的逻辑之后再写
                self.signal = "TERMINATE"
                pass
            except Exception as e:
                self.logger.error(f"User {self.user_id}: Error sending message: {e}")