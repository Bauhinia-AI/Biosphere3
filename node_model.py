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


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )
