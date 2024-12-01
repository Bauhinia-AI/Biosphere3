import functools
import requests
import os
import asyncio
from pprint import pprint
from dotenv import load_dotenv
from loguru import logger
load_dotenv()
GAME_BACKEND_URL = os.getenv("GAME_BACKEND_URL")
AMM_POOL_GET_AVG_PRICE = os.getenv("AMM_POOL_GET_AVG_PRICE")
GAME_BACKEND_TIMEOUT = os.getenv("GAME_BACKEND_TIMEOUT")

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


def get_inventory(userid) -> dict:
    # 从数据库中读取http://47.95.21.135:8082/ammPool/getAveragePrice
    response = requests.get(f"{GAME_BACKEND_URL}/bag/getByCharacterId/{userid}",timeout=GAME_BACKEND_TIMEOUT)
    # 只保留ore, apple, wheat, fish
    inventory_dict = {}
    for x in response.json()["data"]:
        if x["itemName"].lower() in ["apple", "wheat", "fish"]:
            inventory_dict[x["itemName"]] = x["itemQuantity"]
        if x["itemName"].lower() == "iron_ore":
            inventory_dict["ore"] = x["itemQuantity"]

    return inventory_dict


def get_initial_state_from_db(userid, websocket):
    pass


def generate_initial_state_hardcoded(userid, websocket):
    # 从数据库中读取http://47.95.21.135:8082/ammPool/getAveragePrice
    try:
        price_response = requests.get(AMM_POOL_GET_AVG_PRICE, timeout=GAME_BACKEND_TIMEOUT)
        market_data = price_response.json()["data"]
        market_data_dict = dict(
            {
                x["name"]: x["averagePrice"]
                for x in market_data
                if x["name"] in ["ore", "apple", "wheat", "fish"]
            }
        )
    except TimeoutError:
        logger.error(f"Failed to get market data from {AMM_POOL_GET_AVG_PRICE}")
        market_data_dict = {}
    
    initial_state = {
        "userid": userid,
        "character_stats": {
            "name": "Alice",
            "gender": "Female",
            "slogan": "Need to be rich!Need to be educated!",
            "description": "A risk lover. Always looking for the next big thing.",
            "role": "Investor",
            "inventory": get_inventory(userid),
            "health": 100,
            "energy": 100,
        },
        "decision": {
            "need_replan": False,
            "action_description": [],
            "action_result": [],
            "new_plan": [],
            "daily_objective": [],
            "meta_seq": [],
            "reflection": [],
        },
        "meta": {
            "tool_functions": tool_functions_easy,
            "day": "",
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
            "daily_goal": "",
            "refer_to_previous": False,
            "life_style": "Casual",
            "daily_objective_ar": "",
            "task_priority": [],
            "max_actions": 10,
            "meta_seq_ar": "",
            "replan_time_limit": 3,
            "meta_seq_adjuster_ar": "",
            "focus_topic": [],
            "depth_of_reflection": "Moderate",
            "reflection_ar": "",
            "level_of_detail": "Moderate",
            "tone_and_style": "",
        },
        "public_data": {
            "market_data": market_data_dict,
        },
        "message_queue": asyncio.Queue(),
        "event_queue": asyncio.Queue(),
        "false_action_queue": asyncio.Queue(),
        "websocket": websocket,
        "current_pointer": "Sensing_Route",
    }
    return initial_state


def update_dict(existing_dict, new_dict):
    for key, value in new_dict.items():
        if key in existing_dict:
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
"""
# 6. buy [itemType:string] [amount:int]: Purchase items, costing money.
# Constraints: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(ore,bread,apple,wheat,fish)\n

#     10. sleep [hours:int]: Sleep to recover energy and health.
# Constraints: Must be at home.\n

# 9. seedoctor [hours:int]: Visit a doctor, costing money.
# Constraints: Must have enough money and be in the hospital.\n

if __name__ == "__main__":
    print(get_inventory(36))
