import functools
import asyncio
from core.db.database_api_utils import make_api_request_sync
import requests
from loguru import logger
from pprint import pprint


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
    response = requests.get(f"http://47.95.21.135:8082/bag/getByCharacterId/{userid}")
    # 只保留ore, apple, wheat, fish
    inventory_dict = {}
    for x in response.json()["data"]:
        if x["itemName"].lower() in ["apple", "wheat", "fish"]:
            inventory_dict[x["itemName"]] = x["itemQuantity"]
        if x["itemName"].lower() == "iron_ore":
            inventory_dict["ore"] = x["itemQuantity"]

    return inventory_dict


def generate_initial_state_hardcoded(userid, websocket):
    # 从数据库中读取http://47.95.21.135:8082/ammPool/getAveragePrice
    price_response = requests.get("http://47.95.21.135:8082/ammPool/getAveragePrice")
    market_data = price_response.json()["data"]
    market_data_dict = dict(
        {
            x["name"]: x["averagePrice"]
            for x in market_data
            if x["name"] in ["ore", "apple", "wheat", "fish"]
        }
    )
    initial_state = {
        "userid": userid,
        "character_stats": {
            "name": "Alice",
            "gender": "Female",
            "relationship": "Friend",
            "personality": "Adventurous",
            "long_term_goal": "Explore the unknown",
            "short_term_goal": "Find a hidden path",
            "language_style": "Enthusiastic and bold",
            "biography": "A brave explorer with a thirst for adventure.",
            "health": 100,
            "energy": 100,
            "hungry": 100,
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
    character_data = {"characterId": userid}
    response_txt = make_api_request_sync("POST", "/characters/get", data=character_data)
    response_num = requests.get(
        f"http://47.95.21.135:8082/characters/getById/{userid}"
    ).json()
    if response_txt["code"] == 1:
        data_text = response_txt["data"][0]  # Assuming first NPC entry is used
        initial_state["character_stats"].update(
            {
                "name": data_text.get(
                    "characterName", initial_state["character_stats"]["name"]
                ),
                "gender": data_text.get(
                    "gender", initial_state["character_stats"]["gender"]
                ),
                "relationship": data_text.get(
                    "relationship", initial_state["character_stats"]["relationship"]
                ),
                "personality": data_text.get(
                    "personality", initial_state["character_stats"]["personality"]
                ),
                "long_term_goal": data_text.get(
                    "long_term_goal", initial_state["character_stats"]["long_term_goal"]
                ),
                "short_term_goal": data_text.get(
                    "short_term_goal",
                    initial_state["character_stats"]["short_term_goal"],
                ),
                "language_style": data_text.get(
                    "language_style", initial_state["character_stats"]["language_style"]
                ),
                "biography": data_text.get(
                    "biography", initial_state["character_stats"]["biography"]
                ),
            }
        )
    elif response_txt["code"] == 0:
        # 如果 code 为 0，存储角色信息
        character_data = {
            "characterId": userid,
            "characterName": initial_state["character_stats"]["name"],
            "gender": initial_state["character_stats"]["gender"],
            "relationship": initial_state["character_stats"]["relationship"],
            "personality": initial_state["character_stats"]["personality"],
            "long_term_goal": initial_state["character_stats"]["long_term_goal"],
            "short_term_goal": initial_state["character_stats"]["short_term_goal"],
            "language_style": initial_state["character_stats"]["language_style"],
            "biography": initial_state["character_stats"]["biography"],
        }
        make_api_request_sync("POST", "/characters/store", character_data)
        logger.info(f"Storing character: {userid}")
    else:
        logger.error(f"Unexpected response: {response_txt}")

    if response_num.get("code") == 1:
        data_num = response_num["data"]  # Assuming first NPC entry is used
        print(data_num)
        initial_state["character_stats"].update(
            {
                "health": data_num.get("health"),
                "energy": data_num.get("energy"),
                "hungry": data_num.get("hungry"),
            }
        )
    else:
        logger.error(f"Unexpected response: {response_num}")

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
