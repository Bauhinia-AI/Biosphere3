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

initial_state = {
        'userid': 12,
        'character_stats': {
            'name': 'Alice',
            'gender': 'Female',
            'slogan': 'Adventure awaits!',
            'description': 'A brave explorer.',
            'role': 'Explorer',
            'inventory': {},
            'health': 100,
            'energy': 100,
        },
        'decision': {
            'need_replan': False,
            'action_description': ["I successfully picked a banana."],
            'new_plan': [],
            'daily_objective': [],
            'meta_seq': [],
            'reflection': ["Nice"],
        },
        'meta': {
            'tool_functions': tool_functions_easy,
            'day': 'Monday',
            'available_locations': ['school', 'workshop', 'home', 'farm', 'mall', 'square', 'hospital', 'fruit', 'harvest', 'fishing', 'mine', 'orchard'],
        },
        'signal': '',
        'signal_queue': asyncio.Queue(),
    }

class LangGraphInstance:
    def __init__(self, user_id):
        self.user_id = user_id
        # 初始化 langgraph 实例
        # 根据user_id 检索数据库中的信息，更新stat
        self.state = RunningState(**initial_state)
        self.graph = self._get_workflow_with_signal()
        #TODO We should get and init state from database
        #self.state: RunningState = initialize_running_state(user_id,character_params, decision_params, meta_params)
        logger.info(f"User {self.user_id} workflow initialized")

        self.task = asyncio.create_task(self.a_run())

    async def send_signal(self, signal):
        await self.state['signal_queue'].put(signal)
    
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
    def signal_decision(self,state: RunningState):
        if state['signal'] == "SIGNAL_err":
            logger.info("❌ Received SIGNAL_err, starting planning...")
            return "Objectives_planner"
        elif state['signal'] == "SIGNAL_plan":
            logger.info("✅ Received SIGNAL_plan, starting planning...")
            return "Objectives_planner"
        else:
            # 未知信号，继续监听
            logger.info("🟡 Received unknown signal, continuing...")
            return "Listener"
        
    def _get_workflow_with_signal(self):
        workflow = StateGraph(RunningState)
        workflow.add_node("Listener", Listener)
        workflow.add_node("Objectives_planner", generate_daily_objective)
        workflow.add_node("meta_action_sequence", generate_meta_action_sequence)
        workflow.add_node("adjust_meta_action_sequence", adjust_meta_action_sequence)
        workflow.add_conditional_edges("Listener", self.signal_decision)

        workflow.set_entry_point("Listener")
        workflow.set_finish_point("Listener")

        workflow.add_edge("Objectives_planner", "meta_action_sequence")
        workflow.add_edge("meta_action_sequence", "adjust_meta_action_sequence")
        workflow.add_edge("adjust_meta_action_sequence", "Listener")
        return workflow.compile()
    async def a_run(self):
        return await self.graph.ainvoke(initial_state)

async def test_langgraph_instance():
        user_id = 'test_user'
        instance = LangGraphInstance(user_id)

        # 等待代理启动并进入监听状态
        await asyncio.sleep(1)
        
        # 现在实例已经在运行，并在等待信号

        #模拟发送 SIGNAL_plan 信号
        await instance.send_signal('SIGNAL_plan')

        # 等待代理处理信号
        await asyncio.sleep(10)

        # 模拟发送 SIGNAL_err 信号
        await instance.send_signal('SIGNAL_err')

        # 再次等待代理处理信号
        await asyncio.sleep(1)

        # 可以根据需要继续发送信号

        # 最后，取消代理任务（如果需要）
        instance.task.cancel()
        try:
            await instance.task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    

    # 运行测试
    asyncio.run(test_langgraph_instance())