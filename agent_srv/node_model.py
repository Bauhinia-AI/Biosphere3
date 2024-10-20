from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Union, List, Annotated, Tuple, TypedDict, Dict, Any
import operator


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )



class PlanExecute(TypedDict):
    userid: int
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
    daily_objective: List[str]
    meta_seq: List[str]
    tool_functions: str
    locations: str
    past_objectives: List[List[str]]
    execution_results: List[Dict[str, Any]]
    reflection: str
    messages: List[str]
    need_replan: bool


class CharacterStats(TypedDict):
    #static stats
    name: str
    gender: str
    slogan: str
    description: str
    role: str
    #dynamic stats
    inventory: Dict[str, Any]
    health: int
    energy: int


class Decision(TypedDict):
    need_replan: bool
    #action_description: ["I successfully pick an apple", "I failed to navigate home",...]
    action_description: Annotated[List[str], operator.add]
    #new_plan: ["I should rest first, then I should go home",...]
    new_plan: Annotated[List[str], operator.add]
    #daily_objective: ["I should learn how to navigate home",...]
    daily_objective: Annotated[List[str], operator.add]

    meta_seq: List[str]
    reflection: Annotated[List[str], operator.add]

class Meta(TypedDict):
    tool_functions: str
    day:str

class RunningState(TypedDict):
    userid: int
    character_stats: CharacterStats
    decision: Decision
    meta: Meta





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

