from agent_srv.node_model import CharacterStats, Decision, Meta, RunningState
from typing import Dict, Any, List
from typing_extensions import Annotated
import operator


def create_character_stats(
    name: str,
    gender: str,
    relationship: str,
    personality: str,
    long_term_goal: str,
    short_term_goal: str,
    language_style: str,
    biography: str,
    health: int,
    energy: int,
    hungry: int,
    inventory: Dict[str, Any],
) -> CharacterStats:
    return CharacterStats(
        name=name,
        gender=gender,
        relationship=relationship,
        personality=personality,
        long_term_goal=long_term_goal,
        short_term_goal=short_term_goal,
        language_style=language_style,
        biography=biography,
        health=health,
        energy=energy,
        hungry=hungry,
        inventory=inventory,
    )


def create_decision(
    need_replan: bool,
    action_description: Annotated[List[str], operator.add],
    new_plan: Annotated[List[str], operator.add],
    daily_objective: Annotated[List[str], operator.add],
    meta_seq: List[str],
    reflection: Annotated[str, operator.add],
) -> Decision:
    return Decision(
        need_replan=need_replan,
        action_description=action_description,
        new_plan=new_plan,
        daily_objective=daily_objective,
        meta_seq=meta_seq,
        reflection=reflection,
    )


def create_meta(tool_functions: str, day: str) -> Meta:
    return Meta(tool_functions=tool_functions, day=day)


def initialize_running_state(
    userid: int,
    character_params: Dict[str, Any],
    decision_params: Dict[str, Any],
    meta_params: Dict[str, Any],
) -> RunningState:
    """
    Initializes the RunningState with nested TypedDicts.

    :param userid: User ID.
    :param character_params: Parameters for CharacterStats.
    :param decision_params: Parameters for Decision.
    :param meta_params: Parameters for Meta.
    :return: Initialized RunningState.
    """
    character_stats = create_character_stats(**character_params)
    decision = create_decision(
        need_replan=decision_params.get("need_replan", False),
        action_description=decision_params.get("action_description", []),
        new_plan=decision_params.get("new_plan", []),
        daily_objective=decision_params.get("daily_objective", []),
        meta_seq=decision_params.get("meta_seq", []),
        reflection=decision_params.get("reflection", ""),
    )
    meta = create_meta(**meta_params)

    return RunningState(
        userid=userid, character_stats=character_stats, decision=decision, meta=meta
    )
