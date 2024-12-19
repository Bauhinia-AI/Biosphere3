from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Union, List, Annotated, Tuple, TypedDict, Dict, Any
import operator
from langgraph.graph import StateGraph
import asyncio


# 每日对话的topic列表
class ConversationTopics(TypedDict):
    topics: List[str]


class PreConversationTask(TypedDict):
    # start_time: str
    first_sentence: str


class CheckResult(TypedDict):
    Need: bool


# 计划列表中具体的每一条对话任务
class ConversationTask(TypedDict):
    from_id: int
    to_id: int
    start_time: str
    topic: str
    Finish: List[bool]


# 类比于runningstate
class ConversationState(TypedDict):
    userid: int
    character_stats: Dict[str, Any]
    ongoing_task: List[dict]  # 用于储存只读对话任务， 格式npc_ids,start_time,diaologue
    daily_task: List[dict]  # 还未开始的对话任务，格式DailyConversationPlan
    # finished_task: List[dict]  # 已经结束的对话任务， 格式npc_ids,start_time
    message_queue: asyncio.Queue  # 接收消息的队列，需要包含用于判断只读或回复模式的字段
    waiting_response: asyncio.Queue  # 储存等待生成回复的消息， 每个条目格式为RunningConversation
    websocket: Any
    prompt: Dict[str, Any]   # 用于存放prompt,"topic_requirements", "impression_impact"两个字段


# 正在进行中的对话
class RunningConversation(TypedDict):
    from_id: int
    to_id: int
    start_time: str
    latest_message: Dict[str, str]  # 回复的消息，如果真人接管，为空
    send_gametime: list
    send_realtime: str
    Finish: List[bool]


class PreResponse(TypedDict):
    response: str
    Finish: bool


# 已经被判定为结束的对话，储存到DB按此格式
class EndConversation(TypedDict):
    npc_ids: List[int]
    dialogue: List[dict]
    start_time: str


# 对话完成后更新的印象，同时产生两个印象
class ImpressionUpdate(BaseModel):
    impression1: str = Field(description="new impression from player1 to player2")
    impression2: str = Field(description="new impression from player2 to player1")


# 每日总结反思
class Knowledge(BaseModel):
    time: str = Field(description="The day before the knowledge is generated")
    environment_information: str = Field(description="Short-term memory related to environment")
    personal_information: str = Field(description="Long-term memory related to personal profile")


# 每天的对话计划
class DailyConversationPlan(BaseModel):
    """Plan to follow for a certain day"""

    conversations: List[ConversationTask] = Field(
        description="Conversations to be launched, should be in time order and is valid within one day."
    )


class IntimacyMark(BaseModel):
    mark1: int = Field(description="The intimacy mark of player 1 towards the given conversation.")
    mark2: int = Field(description="The intimacy mark of player 2 towards the given conversation.")

