import sys

sys.path.append(".")

import asyncio
import json
import time

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
    generate_accommodation_decision,
)
from core.agent_srv.node_model import RunningState
from core.agent_srv.utils import get_initial_state_from_db


class LangGraphInstance:
    """
    Initializes the state, sets up asynchronous tasks for message processing, event scheduling, and runs the workflow graph.
    """

    def __init__(self, user_id, websocket=None):
        self.user_id = user_id
        self.websocket = websocket
        self.signal = None
        self.state = {}
        self.start_time = None

        # 数据竞争时，锁住state
        self.websocket_lock = None
        self.graph = None
        self.graph_config = {"recursion_limit": 1e10}
        self.logger = logger.bind(agent_instance=True)

        # Asynchronous tasks
        self.msg_processor_task = None
        self.event_scheduler_task = None
        self.task = None

    @classmethod
    async def create(cls, user_id, websocket=None):
        self = cls(user_id, websocket)
        initial_state = await get_initial_state_from_db(user_id, websocket)
        self.state = initial_state

        self.state["instance"] = self
        self.websocket_lock = asyncio.Lock()
        self.graph = self._get_workflow()
        self.graph_config = {"recursion_limit": 1e10}
        self.start_time = time.time()

        self.msg_processor_task = asyncio.create_task(self.msg_processor())
        self.event_scheduler_task = asyncio.create_task(self.event_scheduler())
        self.schedule_event("PLAN")
        self.logger.info(f"User {self.user_id} workflow initialized")
        self.task = asyncio.create_task(self.a_run())

        return self

    async def msg_processor(self):
        """
        Continuously processes incoming messages from the message queue.
        """
        while True:
            msg = await self.state["message_queue"].get()
            message_name = msg.get("messageName")
            message_code = msg.get("messageCode")
            message_data = msg.get("data")
            if message_code >= 100:  # Ignore Conversation Messages
                pass
            elif message_name == "actionresult":
                self.state["decision"]["action_result"].append(msg["data"])
                # If the action result is False, put REPLAN into event_queue
                if msg["data"]["result"] is False:
                    try:
                        self.logger.info(
                            f"❌ User {self.user_id}: Put REPLAN into event_queue"
                        )
                        self.state["false_action_queue"].put_nowait(msg["data"])
                        self.schedule_event("REPLAN")
                    except Exception as e:
                        self.logger.error(
                            f"User {self.user_id}: Error putting REPLAN into event_queue: {e}"
                        )

                self.logger.info(
                    f"🏃 User {self.user_id}: Received action result: {msg['data']}"
                )
            elif message_name == "cv_submission":
                await generate_change_job_cv(self.state["instance"], msg)
            elif message_name == "onestep":
                self.schedule_event("PLAN")
            elif message_name == "check":
                pprint(self.state["decision"]["action_result"])
            elif message_name == "queue_visualizer":
                pprint(self.state["event_queue"])
            elif (
                message_name == "eventInfo"
                and message_data.get("msg") == "ActionList Empty"
            ):
                self.schedule_event("PLAN")
            elif (
                message_name == "accommodation_event"
                or message_data.get("msg") == "House rent will expire tomorrow"
            ):
                self.schedule_event("ACCOMMODATION_EVENT")
            else:
                self.logger.error(
                    f"User {self.user_id}: Unknown message: {message_name}"
                )

    async def event_scheduler(self):
        """
        Schedules and manages events based on the state of action results and timings.
        """
        try:
            while True:
                await asyncio.sleep(100)
                elapsed_time = time.time() - self.start_time
                if self.signal == "TERMINATE":
                    self.logger.error(
                        "⛔ Task event_scheduler terminated due to termination signal."
                    )
                    break
                if elapsed_time >= 900:
                    self.schedule_event("CHARACTER_ARC")
                elif elapsed_time >= 600:
                    self.schedule_event("DAILY_REFLECTION")
                elif elapsed_time >= 300:
                    self.schedule_event("PLAN")
        except Exception as e:
            self.logger.error(f"User {self.user_id}: Error in event_scheduler: {e}")

    def schedule_event(self, event):
        self.state["event_queue"].put_nowait(event)
        self.logger.info(f"🚦 User {self.user_id}: Scheduled event: {event}")

    async def event_router(self, state: RunningState):
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
            elif event == "ACCOMMODATION_EVENT":
                return "Accommodation_Decision"
            else:
                self.logger.error(f"User {self.user_id}: Unknown event: {event}")

    def _get_workflow(self):
        workflow = StateGraph(RunningState)
        workflow.add_node("Sensing_Route", sensing_environment)
        workflow.add_node("Objectives_planner", generate_daily_objective)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("Character_Arc", generate_character_arc)
        workflow.add_node("Daily_Reflection", generate_daily_reflection)
        workflow.add_node("Replan_Action", replan_action)
        workflow.add_node("Accommodation_Decision", generate_accommodation_decision)

        workflow.set_entry_point("Sensing_Route")

        workflow.add_conditional_edges("Sensing_Route", self.event_router)
        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge("Replan_Action", "Sensing_Route")
        workflow.add_edge("meta_action_sequence", "Sensing_Route")
        workflow.add_edge("Character_Arc", "Sensing_Route")
        workflow.add_edge("Daily_Reflection", "Sensing_Route")
        workflow.add_edge("Accommodation_Decision", "Sensing_Route")

        return workflow.compile()

    async def a_run(self):
        try:
            await self.graph.ainvoke(self.state, config=self.graph_config)
        except Exception as e:
            self.signal = "TERMINATE"

            self.logger.error(f"User {self.user_id} Error in workflow: {e}")
            self.logger.error("⛔ Task a_run terminated due to termination signal.")
            self.task.cancel()

    async def send_message(self, message):
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
            except Exception as e:
                self.logger.error(f"User {self.user_id}: Error sending message: {e}")
