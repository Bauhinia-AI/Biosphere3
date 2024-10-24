import asyncio
from agent_srv.node_engines import *
from agent_srv.factories import initialize_running_state
from agent_srv.node_model import RunningState
from langgraph.graph import StateGraph, START, END
import os
import asyncio
import pprint


tool_functions_easy = """
    4.	pick_apple(): Pick an apple, costing energy.
Constraints: Must have enough energy and be in the orchard.\n
	5.	go_fishing(): Fish for resources, costing energy.
Constraints: Must have enough energy and be in the fishing area.\n
	6.	mine(): Mine for resources, costing energy.
Constraints: Must have enough energy and be in the mine.\n
	7.	harvest(): Harvest crops, costing energy.
Constraints: Must have enough energy and be in the harvest area.\n
	8.	buy(itemType: ItemType, amount: int): Purchase items, costing money.
Constraints: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	9.	sell(itemType: ItemType, amount: int): Sell items for money.
Constraints: Must have enough items in inventory.ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	10.	use_item(itemType: ItemType, amount: int): Use an item.
Constraints: Must have enough items in inventory.ItemType:(Ore,Bread,Apple,Wheat,Fish)\n
	11.	see_doctor(hours: int): Visit a doctor, costing money.
Constraints: Must have enough money and be in the hospital.\n
	12.	sleep(hours: int): Sleep to recover energy and health.
Constraints: Must be at home.\n
    13.	study(hours: int): Study to achieve a higher degree.
Constraints: Must be in school and have enough money.\n
    14.	nav(placeName: string): Navigate to a specified location.
Constraints: Must in (school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard).
"""


def generate_initial_state(websocket):
    initial_state = {
        "userid": 12,
        "character_stats": {
            "name": "Alice",
            "gender": "Female",
            "slogan": "Adventure awaits!",
            "description": "A brave explorer.",
            "role": "Explorer",
            "inventory": {},
            "health": 100,
            "energy": 100,
        },
        "decision": {
            "need_replan": False,
            "action_description": ["I successfully picked a banana."],
            "action_result": [],
            "new_plan": [],
            "daily_objective": [],
            "meta_seq": [],
            "reflection": ["Nice"],
        },
        "meta": {
            "tool_functions": tool_functions_easy,
            "day": "Monday",
            "available_locations": [
                "school",
                "workshop",
                "home",
                "farm",
                "mall",
                "square",
                "hospital",
                "fruit",
                "harvest",
                "fishing",
                "mine",
                "orchard",
            ],
        },
        "message_queue": asyncio.Queue(),
        "websocket": websocket,
    }
    return initial_state


class LangGraphInstance:
    def __init__(self, user_id, websocket=None):
        self.user_id = user_id
        self.websocket = websocket
        # 初始化 langgraph 实例
        # 根据user_id 检索数据库中的信息，更新stat
        self.state = RunningState(**generate_initial_state(self.websocket))
        self.graph = self._get_workflow_with_listener()
        self.listener_task = asyncio.create_task(self.listener())
        #self.schedule_task = asyncio.create_task(self.schedule_messages())

        # TODO We should get and init state from database
        # self.state: RunningState = initialize_running_state(user_id,character_params, decision_params, meta_params)
        logger.info(f"User {self.user_id} workflow initialized")
        self.task = asyncio.create_task(self.a_run())

    # 生产者listener，独立于graph运行
    async def listener(self):
        websocket = self.state["websocket"]
        message_queue = self.state["message_queue"]
        logger.info(f"👂 User {self.user_id}: LISTENER started...")

        try:
            async for message in websocket:
                data = json.loads(message)
                await message_queue.put(data)
                logger.info(
                    f"👂 User {self.user_id}: Received message: {data} and put into queue"
                )
        except websockets.ConnectionClosed:
            logger.error(f"User {self.user_id}: WebSocket connection closed.")

        except Exception as e:
            logger.error(f"User {self.user_id}: Error in listener: {e}")



    async def send_msg_to_game(self, message_name, data):
        message = {
            "messageName": message_name,
            "data": data,
            "characterId": self.user_id,
        }
        await self.websocket.send(json.dumps(message))

    async def a_run(self):
        try:
            await self.graph.ainvoke(self.state)
        except Exception as e:
            logger.error(f"User {self.user_id} Error in workflow: {e}")

    async def process_messages(self, state: RunningState):
        while True:
            message = await state["message_queue"].get()

            if message is None:
                logger.error(f"User {self.user_id}: WebSocket connection closed.")
                break
            logger.info(f"User {self.user_id}: Received message: {message}")

            message_name = message.get("messageName")
            if message_name == "action_result":
                # 处理动作结果
                self.state["decision"]["action_result"].append(message["data"])
                logger.info(
                f"🏃 User {self.user_id}: Received action result: {message['data']}"
            )
            elif message_name == "gameevent":
                pass

            elif message_name == "onestep":
                return "Objectives_planner"
            
            elif message_name == "check":
               pprint(self.state["decision"]["actionresult"])

            else:
                logger.error(f"User {self.user_id}: Unknown message: {message_name}")
            # await self.state['message_queue'].task_done()

    def _get_workflow_with_listener(self):
        workflow = StateGraph(RunningState)
        # workflow.add_node("Process_Messages", self.process_messages)
        workflow.add_node("")
        workflow.add_node("Objectives_planner", generate_daily_objective)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("adjust_meta_action_sequence", adjust_meta_action_sequence)

        workflow.set_conditional_entry_point(self.process_messages)

        # 定义工作流的路径
        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge(
            "meta_action_sequence", "adjust_meta_action_sequence"
        )  # 循环回消息处理
        workflow.add_edge("adjust_meta_action_sequence", "")

        return workflow.compile()

    def _get_workflow_without_listener(self):
        workflow = StateGraph(RunningState)
        workflow.add_node("Objectives_planner", generate_daily_objective)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("adjust_meta_action_sequence", adjust_meta_action_sequence)
        workflow.set_entry_point("Objectives_planner")
        workflow.set_finish_point("adjust_meta_action_sequence")
        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge("meta_action_sequence", "adjust_meta_action_sequence")
        # workflow.add_conditional_edges("replan", should_end)
        return workflow.compile()


if __name__ == "__main__":
    asyncio.run(main())
