import asyncio
from agent_srv.node_engines import *
from agent_srv.factories import initialize_running_state
from agent_srv.node_model import RunningState
from langgraph.graph import StateGraph, START, END
import os
import asyncio
import pprint
character_params = {
        "name": "Aria Windrunner",
        "gender": "Female",
        "slogan": "Seek and you shall find",
        "description": "A brave adventurer with a keen sense of direction.",
        "role": "Explorer",
        "inventory": {
            "map": "Ancient World Map",
            "compass": "Golden Compass",
            "backpack": "Leather Backpack",
            "tools": ["Torch", "Rope", "Knife"]
        },
        "health": 100,
        "energy": 75
    }

decision_params = {
    "need_replan": False,
    "action_description": [],
    "new_plan": [],
    "daily_objective": [],
    "meta_seq": [],
    "reflection": []
}
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
meta_params = {
    "tool_functions": tool_functions_easy,
    "day": "Monday",
    "available_locations": ["school", "workshop", "home", "farm", "mall", "square", "hospital", "fruit", "harvest", "fishing", "mine", "orchard"]
}


class LangGraphInstance:
    def __init__(self, user_id):
        self.user_id = user_id
        # 初始化 langgraph 实例
        # 根据user_id 检索数据库中的信息，更新stat

        self.graph = self._get_workflow_without_listener()
        self.state: RunningState = initialize_running_state(user_id,character_params, decision_params, meta_params)
        logger.info(f"User {self.user_id} workflow initialized")

        logger.info("🎭 character_stats: \n" + pprint.pformat(self.state["character_stats"]))

        logger.info("🧠 decision: \n" + pprint.pformat(self.state["decision"]))


    def init_character_stats(self):
        # 根据user_id 检索数据库中的信息，更新stats
        pass


    async def handle_action(self, action, data):
        # 根据 action 执行相应的处理
        if action == 'process_message':
            # 处理来自客户端的消息
            # 例如，执行工作流，生成响应
            response = await self.process_message(data)
            return response
        else:
            return {'error': 'Unknown action'}

    async def process_message(self, data):
        # 实现您的处理逻辑
        # 调用 langgraph 实例执行工作流
        # 返回处理结果
        return {'result': 'Message processed'}
    
    def _get_workflow_with_listener(self):
        workflow = StateGraph(PlanExecute)
        workflow.add_node("Objectives_planner", generate_daily_objective)
        # workflow.add_node("detailed_planner", generate_detailed_plan)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("adjust_meta_action_sequence", adjust_meta_action_sequence)
        workflow.add_node("Action_Result_Listener", listen_for_action_results)
        
        


        # workflow.add_node("reflector", generate_reflection)

        workflow.add_edge(START, "Objectives_planner")
        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge("meta_action_sequence", "adjust_meta_action_sequence")
        workflow.add_edge("adjust_meta_action_sequence", "Action_Result_Listener")
        workflow.add_edge("Action_Result_Listener", END)
        return workflow.compile()
    def _get_workflow_without_listener(self):
        workflow = StateGraph(PlanExecute)
        workflow.add_node("Objectives_planner", generate_daily_objective)
        # workflow.add_node("detailed_planner", generate_detailed_plan)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("adjust_meta_action_sequence", adjust_meta_action_sequence)
        workflow.set_entry_point("Objectives_planner")
        workflow.set_finish_point("adjust_meta_action_sequence")
        #workflow.add_edge(START, "Objectives_planner")
        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge("meta_action_sequence", "adjust_meta_action_sequence")
        #workflow.add_edge("adjust_meta_action_sequence", END)


        # workflow.add_conditional_edges("replan", should_end)
        return workflow.compile()
    
    async def ainvoke(self):
        state = {
            "userid": "12345",
            "input": f"""userid=12345,
            username="JohnDoe",
            gender="male",
            slogan="Innovate and Inspire",
            description="A passionate developer with a knack for problem-solving.",
            role="developer",
            task="Build a scalable web application",
            """,
            "tool_functions": tool_functions_easy,
            "locations": ["New York", "San Francisco"],
            "past_objectives": ["Complete project hahahahahahahahahaha", "Improve system performance"],

        }
        return await self.graph.ainvoke(state,stream_mode="values")


if __name__ == "__main__":
    instance = LangGraphInstance(12345)
    #res = asyncio.run(instance.ainvoke())
    #print(res)
    #res 
    