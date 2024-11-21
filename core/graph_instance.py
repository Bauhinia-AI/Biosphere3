import sys

sys.path.append(".")

import asyncio
from core.agent_srv.node_engines import *
from core.agent_srv.node_model import RunningState
import time
from langgraph.graph import StateGraph
import asyncio
from pprint import pprint
from core.agent_srv.utils import generate_initial_state_hardcoded, update_dict
from core.agent_srv.node_engines import *
from datetime import datetime, timedelta
from core.agent_srv.node_engines import generate_accommodation_decision


class LangGraphInstance:
    def __init__(self, user_id, websocket=None):
        self.user_id = user_id
        self.websocket = websocket
        self.signal = None
        # 初始化 langgraph 实例
        #  TODO We should 根据user_id 检索数据库中的信息，更新stat
        self.state = RunningState(
            **generate_initial_state_hardcoded(self.user_id, self.websocket)
        )
        self.state["instance"] = self
        self.connection_stats = {}
        # 数据竞争时，锁住state
        self.state_lock = asyncio.Lock()
        self.websocket_lock = asyncio.Lock()
        self.graph = self._get_workflow_with_listener()
        self.graph_config = {"recursion_limit": 1e10}
        # 三个协程
        # self.listener_task = asyncio.create_task(self.listener())
        self.msg_processor_task = asyncio.create_task(self.msg_processor())
        self.event_scheduler_task = asyncio.create_task(self.event_scheduler())
        # self.queue_visualizer_task = asyncio.create_task(self.queue_visualizer())
        # self.schedule_task = asyncio.create_task(self.schedule_messages())
        self.state["event_queue"].put_nowait("PLAN")
        logger.info(f"User {self.user_id} workflow initialized")
        self.action_result = []
        self.task = asyncio.create_task(self.a_run())

    async def msg_processor(self):
        while True:

            msg = await self.state["message_queue"].get()
            message_name = msg.get("messageName")
            message_code = msg.get("messageCode")
            # logger.info(f"㊗️ 处理信息信息 User {self.user_id} message: {msg}")
            if message_name == "actionresult":
                # 处理动作结果
                self.state["decision"]["action_result"].append(msg["data"])

                if msg["data"]["result"] is False:
                    try:
                        # 如果失败，则往false_action_queue里放
                        logger.info(
                            f"❌❌❌❌❌ User {self.user_id}: Put REPLAN into event_queue"
                        )
                        self.state["false_action_queue"].put_nowait(msg["data"])
                        self.state["event_queue"].put_nowait("REPLAN")
                    except Exception as e:
                        logger.error(
                            f"User {self.user_id}: Error putting REPLAN into event_queue: {e}"
                        )

                logger.info(
                    f"🏃 User {self.user_id}: Received action result: {msg['data']}"
                )
                # 把action_result 和本地時間 记录下来
                self.action_result.append(
                    {"action_result": msg["data"], "timestamp": datetime.now()}
                )
            elif message_name == "prompt_modification":
                update_dict(self.state["prompts"], msg["data"])
                logger.info(
                    f"🏃 User {self.user_id}: Updated prompts: {self.state['prompts']}"
                )
            elif message_name == "new_day":
                self.state["event_queue"].put_nowait("JOB_HUNTING")
            elif message_name == "onestep":
                self.state["event_queue"].put_nowait("PLAN")
            elif message_name == "accommodation_event":
                self.state["event_queue"].put_nowait("ACCOMMODATION_EVENT")

            elif message_name == "check":
                pprint(self.state["decision"]["action_result"])
            elif message_code >= 100:
                pass  # 忽略掉对话系统的消息
            else:
                logger.error(f"User {self.user_id}: Unknown message: {message_name}")

    async def event_scheduler(self):
        # start timer
        try:
            start_time = time.time()
            while True:
                if self.signal == "TERMINATE":
                    logger.error(
                        f"⛔ Task event_scheduler terminated due to termination signal."
                    )
                    break
                await asyncio.sleep(1)
                # 如果action_result中最後一條信息不為sleep且和现在时间相差十秒，就往event_queue里放plan
                if self.action_result[-1]["action_result"][
                    "action_name"
                ] != "sleep" and datetime.now() - self.action_result[-1][
                    "timestamp"
                ] > timedelta(
                    seconds=5
                ):
                    self.state["event_queue"].put_nowait("PLAN")
                # 如果时间超过5分钟，则往队列里放[REFLECT
                if time.time() - start_time > 300:
                    # BUG REFLECT raise error
                    pass
                    # self.state["event_queue"].put_nowait("REFLECT")
                # self.state["event_queue"].put_nowait("PLAN")
                # logger.info(f"🆕 User {self.user_id}: Put PLAN into event_queue")
        except Exception as e:
            logger.error(f"User {self.user_id}: Error in event_scheduler: {e}")

    async def queue_visualizer(self):
        while True:
            await asyncio.sleep(10)
            if self.signal == "TERMINATE":
                logger.error(
                    f"⛔ Task queue_visualizer terminated due to termination signal."
                )
                break
            logger.info(
                f"🧾 User {self.user_id} event_queue: {self.state['event_queue']}"
            )
            # logger.info(
            #     f"🧾 User {self.user_id} message_queue: {self.state['message_queue']}"
            # )
            logger.info(
                f"❌ User {self.user_id} false_action_queue: {self.state['false_action_queue']}"
            )

    async def event_router(self, state: RunningState):
        while True:
            event = await state["event_queue"].get()
            logger.info(f"🚦 User {self.user_id}: Event: {event}")

            if event == "PLAN":
                return "Objectives_planner"

            elif event == "REFLECT":
                return "Reflect_And_Summarize"

            elif event == "JOB_HUNTING":
                return "Change_Job"

            elif event == "ACCOMMODATION_EVENT":
                return "Accommodation_Decision"

            elif event == "gameevent":
                pass

            elif event == "REPLAN":
                return "Replan_Action"

            elif event == "check":
                pprint(self.state["decision"]["action_result"])

            else:
                logger.error(f"User {self.user_id}: Unknown event: {event}")
            # await self.state['message_queue'].task_done()

    def _get_workflow_with_listener(self):
        workflow = StateGraph(RunningState)
        workflow.add_node("Sensing_Route", sensing_environment)
        workflow.add_node("Objectives_planner", generate_daily_objective)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("Change_Job", generate_change_job_cv)
        workflow.add_node("Mayor_Decision", generate_mayor_decision)
        workflow.add_node("Accommodation_Decision", generate_accommodation_decision)
        # workflow.add_node("adjust_meta_action_sequence", adjust_meta_action_sequence)

        workflow.add_node("Replan_Action", replan_action)
        # workflow.add_node("Reflect_And_Summarize", reflect_and_summarize)

        workflow.set_entry_point("Sensing_Route")
        workflow.add_conditional_edges("Sensing_Route", self.event_router)

        workflow.add_edge("Replan_Action", "Sensing_Route")

        # 定义工作流的路径
        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge("meta_action_sequence", "Sensing_Route")
        workflow.add_edge("Change_Job", "Mayor_Decision")
        workflow.add_edge("Mayor_Decision", "Sensing_Route")
        workflow.add_edge("Accommodation_Decision", "Sensing_Route")
        # workflow.add_edge("meta_action_sequence", "adjust_meta_action_sequence")
        # 循环回消息处理
        # workflow.add_edge("adjust_meta_action_sequence", "Sensing_Route")
        # workflow.add_edge("Reflect_And_Summarize", "Sensing_Route")

        # 每隔五次目标或3分钟反思一次
        # def should_reflect(state: RunningState) -> bool:
        #     objectives_count = len(state.get("decision", {}).get("daily_objective", []))
        #     last_reflection_time = (
        #         state.get("decision", {}).get("reflections", [{}])[-1].get("timestamp")
        #     )

        #     if last_reflection_time:
        #         time_since_last = datetime.now() - datetime.fromisoformat(
        #             last_reflection_time
        #         )
        #         return time_since_last.total_seconds() > 180  # 3分钟

        #     return objectives_count > 0 and objectives_count % 5 == 0

        # # workflow.add_conditional_edges(
        # #     "Process_Messages",
        # #     lambda x: "Reflect_And_Summarize" if should_reflect(x) else "Sensing_Route",
        # # )
        # # workflow.add_edge("Reflect_And_Summarize", "Sensing_Route")

        # # 每隔五次目标或3分钟反思一次
        # def should_reflect(state: RunningState) -> bool:
        #     objectives_count = len(state.get("decision", {}).get("daily_objective", []))
        #     last_reflection_time = (
        #         state.get("decision", {}).get("reflections", [{}])[-1].get("timestamp")
        #     )

        #     if last_reflection_time:
        #         time_since_last = datetime.now() - datetime.fromisoformat(
        #             last_reflection_time
        #         )
        #         return time_since_last.total_seconds() > 180  # 3分钟

        #     return objectives_count > 0 and objectives_count % 5 == 0

        # workflow.add_conditional_edges(
        #     "Process_Messages",
        #     lambda x: "Reflect_And_Summarize" if should_reflect(x) else "Sensing_Route",
        # )
        # workflow.add_edge("Reflect_And_Summarize", "Sensing_Route")

        return workflow.compile()

    async def a_run(self):
        try:
            await self.graph.ainvoke(self.state, config=self.graph_config)
        except Exception as e:
            self.signal = "TERMINATE"

            logger.error(f"User {self.user_id} Error in workflow: {e}")
            logger.error(f"⛔ Task a_run terminated due to termination signal.")
            self.task.cancel()

    async def send_message(self, message):
        async with self.websocket_lock:
            if self.websocket is None or self.websocket.closed:
                logger.error(f"⛔ User {self.user_id}: WebSocket is not connected.")
                self.signal = "TERMINATE"
                return
            try:
                await self.websocket.send(json.dumps(message))
                logger.info(f"📤 User {self.user_id}: Sent message: {message}")
            except websockets.ConnectionClosed:
                logger.warning(
                    f"User {self.user_id}: WebSocket connection closed during send."
                )
                # TODO 这里的逻辑之后再写
                self.signal = "TERMINATE"
                pass
            except Exception as e:
                logger.error(f"User {self.user_id}: Error sending message: {e}")
