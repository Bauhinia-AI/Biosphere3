from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Union, List, Annotated, Tuple, TypedDict, Dict, Any
import operator
from langgraph.graph import StateGraph
import asyncio


# daily topic plan
class ConversationTopics(TypedDict):
    topics: List[str]


class PreConversationTask(TypedDict):
    # start_time: str
    first_sentence: str


class CheckResult(TypedDict):
    Need: bool


# every converation task in the daily plan list
class ConversationTask(TypedDict):
    from_id: int
    to_id: int
    start_time: str
    topic: str
    Finish: List[bool]


class ConversationState(TypedDict):
    userid: int
    character_stats: Dict[str, Any]
    ongoing_task: List[dict]  # Temporarily store read-only message, which contains npc_ids, start_time, and diaologue
    daily_task: List[dict]  # Daily conversation plan, the format is DailyConversationPlan
    message_queue: asyncio.Queue  
    waiting_response: asyncio.Queue  # Conversations that need reply, the format is RunningConversation
    websocket: Any
    prompt: Dict[str, Any]   # initial prompt setting, including "topic_requirements", "impression_impact"


# ongoing conversation
class RunningConversation(TypedDict):
    from_id: int
    to_id: int
    start_time: str
    latest_message: Dict[str, str]  
    send_gametime: list
    send_realtime: str
    Finish: List[bool]


class PreResponse(TypedDict):
    response: str
    Finish: bool


# completed conversation
class EndConversation(TypedDict):
    npc_ids: List[int]
    dialogue: List[dict]
    start_time: str


# Update the impressions after the conversation is completed, generating two impressions simultaneously
class ImpressionUpdate(BaseModel):
    impression1: str = Field(description="new impression from player1 to player2")
    impression2: str = Field(description="new impression from player2 to player1")


class Knowledge(BaseModel):
    time: str = Field(description="The day before the knowledge is generated")
    environment_information: str = Field(description="Short-term memory related to environment")
    personal_information: str = Field(description="Long-term memory related to personal profile")


class DailyConversationPlan(BaseModel):
    """Plan to follow for a certain day"""

    conversations: List[ConversationTask] = Field(
        description="Conversations to be launched, should be in time order and is valid within one day."
    )


class IntimacyMark(BaseModel):
    mark1: int = Field(description="The intimacy mark of player 1 towards the given conversation.")
    mark2: int = Field(description="The intimacy mark of player 2 towards the given conversation.")

