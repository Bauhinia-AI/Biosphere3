from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Union, List, Annotated, Tuple, TypedDict, Dict, Any
import operator
from langgraph.graph import StateGraph
import asyncio
#带有合并逻辑的鸡肋

def generic_reducer(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        result = a.copy()
        for key in b:
            if key in a:
                #递归调用
                result[key] = generic_reducer(a[key], b[key])
            else:
                result[key] = b[key]
        return result
    elif isinstance(a, list) and isinstance(b, list):
        return a + b
    else:
        return b

class CharacterStats(TypedDict):
    name: str
    gender: str
    slogan: str
    description: str
    role: str
    inventory: Dict[str, Any]
    health: int
    energy: int

class Decision(TypedDict):
    need_replan: bool
    action_description: List[str]
    action_result: List[str]
    new_plan: List[str]
    daily_objective: List[str]
    meta_seq: List[str]
    reflection: List[str]


class Meta(TypedDict):
    tool_functions: str
    day: str
    available_locations: List[str]

class RunningState(TypedDict):
    userid: int
    character_stats: Annotated[CharacterStats, generic_reducer]
    decision: Annotated[Decision, generic_reducer]
    meta: Annotated[Meta, generic_reducer]
    message_queue: asyncio.Queue
    event_queue: asyncio.Queue
    false_action_queue: asyncio.Queue
    websocket: Any
    current_pointer: str
    instance: Any




class DailyObjective(BaseModel):
    """Daily objective to follow in future"""

    objectives: List[str] = Field(description="daily objectives list")
    past_objectives: List[List[str]] = Field(description="past daily objectives list")


class DetailedPlan(BaseModel):
    """Detailed plan to follow in future"""

    detailed_plan: str = Field(description="detailed plan")


class MetaActionSequence(BaseModel):
    """Meta action sequence to follow in future"""

    meta_action_sequence: List[str] = Field(description="meta action sequence")

class Reflection(BaseModel):
    reflection: str

class Response(BaseModel):
    """Response to user."""

    response: str


if __name__ == "__main__":
    # 创建 StateGraph 实例
    graph = StateGraph(RunningState)

    # 定义一个更新 decision 的节点函数
    def update_decision(state: RunningState, config):
        # 从状态中获取当前的 decision
        decision = state['decision']
        # 创建新的 action_description 和 reflection
        new_action_description = ["I successfully picked an apple.","I successfully picked a banana.","I successfully picked a pear."]
        new_reflection = ["I feel happy about finding food."]
        # 返回对 decision 的更新
        return {
            'decision': {
                'action_description': new_action_description,
                'reflection': new_reflection
            }
        }

    def update_character_stats(state: RunningState, config):
        # 从状态中获取当前的 character_stats,fake data
        fake_new_character_stats = {
            "name": "Bobo",
            "gender": "male",
            "slogan": "Adventure awaits!",
            "description": "A brave explorer.",
            "role": "Explorer",
            "inventory": {},
            "health": 10000,
            "energy": 100,
        }
        return {
            'character_stats': fake_new_character_stats
        }
    
    def update_meta(state: RunningState, config):
        # 从状态中获取当前的 meta
        fake_new_meta = {
            "tool_functions": "I can use the following tools: ['apple_picker', 'banana_picker']",
            "day": "Monday",
            "available_locations": ["Forest", "Village"]
        }
        return {
            'meta': fake_new_meta
        }
    # 将节点添加到图中
    graph.add_node('UpdateDecision', update_decision)
    graph.add_node('UpdateCharacterStats', update_character_stats)
    graph.add_node('UpdateMeta', update_meta)

    # 设置入口和出口点
    graph.set_entry_point('UpdateDecision')
    graph.add_edge('UpdateDecision', 'UpdateCharacterStats')
    graph.add_edge('UpdateDecision', 'UpdateMeta')
    graph.set_finish_point('UpdateMeta')

    # 编译图
    compiled = graph.compile()

    # 准备初始状态
    initial_state = {
        'userid': 1,
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
            'tool_functions': '',
            'day': 'Monday',
            'available_locations': ['Forest', 'Village'],
        }
    }
    import pprint
    # 调用编译后的图
    result = compiled.invoke(initial_state)
    # 输出结果
    pprint.pprint(result)