import functools
import asyncio


# BETTER WAY？
def check_termination(coro):
    @functools.wraps(coro)
    async def wrapper(self, *args, **kwargs):
        # 检查 self.signal 是否为 TERMINATE
        if getattr(self, "signal", None) == "TERMINATE":
            # 可以选择直接返回，或者抛出异常
            print(f"⛔ Task {coro.__name__} terminated due to termination signal.")
            return  # 直接返回，终止协程
            # 或者抛出异常
            # raise asyncio.CancelledError("Task terminated due to termination signal.")
        # 否则，继续执行协程
        return await coro(self, *args, **kwargs)

    return wrapper


def generate_initial_state(userid, websocket):
    initial_state = {
        "userid": userid,
        "character_stats": {
            "name": "Alice",
            "gender": "Female",
            "slogan": "Need to be rich!",
            "description": "A risk lover. Always looking for the next big thing.",
            "role": "Investor",
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
        "prompts": {
            "obj_planner_prompt": {
                "daily_goal": "",
                "refer_to_previous": False,
                "life_style": "Casual",
                "addtional_requirements": "",
            },
            "meta_action_sequence_prompt": {
                "task_priority": {},
                "max_actions": 10,
                "additional_requirements": "",
            },
            "meta_seq_adjuster_prompt": {
                "replan_time_limit": 3,
                "additional_requirements": "",
            },
            "reflection_prompt": {
                "focus_topic": [],
                "depth_of_reflection": "Moderate",
                "additional_requirements": "",
            },
            "describe_action_result_prompt": {
                "level_of_detail": "Moderate",
                "tone_and_style": "",
            },
        },
        "message_queue": asyncio.Queue(),
        "event_queue": asyncio.Queue(),
        "false_action_queue": asyncio.Queue(),
        "websocket": websocket,
        "current_pointer": "Sensing_Route",
    }
    return initial_state


def update_nested_dict(existing_dict, new_dict):
    for key, value in new_dict.items():
        if key in existing_dict:
            if isinstance(value, dict) and isinstance(existing_dict[key], dict):
                update_nested_dict(existing_dict[key], value)
            else:
                existing_dict[key] = value


tool_functions_easy = """
    1. goto [placeName:string]: Go to a specified location.
Constraints: Must in (school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard).\n
    2. pickapple [number:int]: Pick an apple, costing energy.
Constraints: Must have enough energy and be in the orchard.\n
    3. gofishing [hours:int]: Fish for fish, costing energy.
Constraints: Must have enough energy and be in the fishing area.\n
    4. gomining [hours:int]: Mine for ore, costing energy.
Constraints: Must have enough energy and be in the mine.\n
    5. harvest [hours:int]: Harvest crops, costing energy.
Constraints: Must have enough energy and be in the harvest area.\n

    7. sell [itemType:string] [amount:int]: Sell items for money. The ONLY way to get money.
Constraints: Must have enough items in inventory. ItemType:(ore,bread,apple,wheat,fish)\n
    
    10. study [hours:int]: Study to achieve a higher degree, will cost money.
Constraints: Must be in school and have enough money.\n
    11. sleep [hours:int]: Sleep to recover energy and health only when your energy is low.
Constraints: Must be at home.\n
"""
# 6. buy [itemType:string] [amount:int]: Purchase items, costing money.
# Constraints: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(ore,bread,apple,wheat,fish)\n

#     10. sleep [hours:int]: Sleep to recover energy and health.
# Constraints: Must be at home.\n

# 9. seedoctor [hours:int]: Visit a doctor, costing money.
# Constraints: Must have enough money and be in the hospital.\n
