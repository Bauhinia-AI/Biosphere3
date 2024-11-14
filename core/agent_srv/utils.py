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
        "event_queue": asyncio.Queue(),
        "false_action_queue": asyncio.Queue(),
        "websocket": websocket,
        "current_pointer": "Sensing_Route",
    }
    return initial_state


tool_functions_easy = """
    1. goto [placeName:string]: Go to a specified location.
Constraints: Must in (school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard).\n
    2. pickapple [number:int]: Pick an apple, costing energy.
Constraints: Must have enough energy and be in the orchard.\n
    3. gofishing [hours:int]: Fish for resources, costing energy.
Constraints: Must have enough energy and be in the fishing area.\n
    4. gomining [hours:int]: Mine for resources, costing energy.
Constraints: Must have enough energy and be in the mine.\n
    5. harvest [hours:int]: Harvest crops, costing energy.
Constraints: Must have enough energy and be in the harvest area.\n
    6. buy [itemType:string] [amount:int]: Purchase items, costing money.
Constraints: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(ore,bread,apple,wheat,fish)\n
    7. sell [itemType:string] [amount:int]: Sell items for money.
Constraints: Must have enough items in inventory. ItemType:(ore,bread,apple,wheat,fish)\n
    9. seedoctor [hours:int]: Visit a doctor, costing money.
Constraints: Must have enough money and be in the hospital.\n
    10. study [hours:int]: Study to achieve a higher degree.
Constraints: Must be in school and have enough money.\n
"""


#     10. sleep [hours:int]: Sleep to recover energy and health.
# Constraints: Must be at home.\n
