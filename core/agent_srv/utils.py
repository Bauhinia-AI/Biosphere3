import functools
import requests
import os
from json import JSONDecodeError
import asyncio
from pprint import pprint
from dotenv import load_dotenv
import aiohttp
from loguru import logger
from core.db.database_api_utils import make_api_request_sync

load_dotenv()
GAME_BACKEND_URL = os.getenv("GAME_BACKEND_URL")
AMM_POOL_GET_AVG_PRICE = os.getenv("AMM_POOL_GET_AVG_PRICE")
GAME_BACKEND_TIMEOUT = int(os.getenv("GAME_BACKEND_TIMEOUT"))
AGENT_BACKEND_URL = os.getenv("AGENT_BACKEND_URL")


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


def fetch_api_data(
    method: str,
    endpoint: str,
    userid: int,
    _logger,
    timeout: int = GAME_BACKEND_TIMEOUT,
) -> dict:
    """
    Make an API request with error handling.

    Args:
        method (str): HTTP method (e.g., 'POST').
        endpoint (str): API endpoint.
        data (dict): Data to send in the request.
        logger: The logger instance for logging errors.
        timeout (int): The timeout for the request.

    Returns:
        dict: The API response data if successful, otherwise an empty dict.
    """
    try:
        return make_api_request_sync(
            method, endpoint, data={"characterId": userid}, timeout=timeout
        )
    except TimeoutError:
        _logger.error(f"Failed to get data from {endpoint}")
    except JSONDecodeError:
        _logger.error(f"Failed to decode JSON from {endpoint}")
    return {}


async def fetch_api_data_async(
    method: str,
    endpoint: str,
    userid: int,
    _logger,
    timeout: int = GAME_BACKEND_TIMEOUT,
) -> dict:
    """
    Make an asynchronous API request with error handling.

    Args:
        method (str): HTTP method (e.g., 'POST').
        endpoint (str): API endpoint.
        userid (int): User ID.
        _logger: The logger instance for logging errors.
        timeout (int): The timeout for the request.

    Returns:
        dict: The API response data if successful, otherwise an empty dict.
    """
    url = f"{AGENT_BACKEND_URL}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, json={"characterId": userid}, timeout=timeout
            ) as response:
                response.raise_for_status()
                return await response.json()
    except asyncio.TimeoutError:
        _logger.error(f"Timeout while accessing {endpoint}")
    except aiohttp.ClientError as e:
        _logger.error(f"HTTP error while accessing {endpoint}: {e}")
    except JSONDecodeError:
        _logger.error(f"Failed to decode JSON from {endpoint}")
    return {}


def fetch_json(url: str, timeout: int, _logger, error_message: str = "") -> dict:
    """
    Fetch JSON data from a given URL with error handling.

    Args:
        url (str): The URL to send the GET request to.
        timeout (int): The timeout for the request.
        _logger: The logger instance for logging errors.
        error_message (str): Custom error message for timeout.

    Returns:
        dict: The JSON data if successful, otherwise an empty dict.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response_data = response.json().get("data", {})
        if response_data == None:
            return {"code": 0, "data": None, "message": "Resource not found at GAMEDB"}
        return response_data
    except TimeoutError:
        _logger.error(error_message)
    except JSONDecodeError:
        _logger.error(f"Failed to decode JSON from {url}")
    return {"code": 0, "data": {}, "message": "Resource not found at GAMEDB"}


async def fetch_json_async(
    url: str, timeout: int, _logger, error_message: str = ""
) -> dict:
    """
    Fetch JSON data from a given URL asynchronously with error handling.

    Args:
        url (str): The URL to send the GET request to.
        timeout (int): The timeout for the request.
        _logger: The logger instance for logging errors.
        error_message (str): Custom error message for timeout.

    Returns:
        dict: The JSON data if successful, otherwise an empty dict.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                response_data = await response.json()
                return response_data.get("data", {}) if response_data else {}
    except asyncio.TimeoutError:
        _logger.error(error_message)
    except aiohttp.ClientError as e:
        _logger.error(f"HTTP error while accessing {url}: {e}")
    except JSONDecodeError:
        _logger.error(f"Failed to decode JSON from {url}")
    return {"code": 0, "data": {}, "message": "Resource not found at GAMEDB"}


def get_inventory(
    userid, filter_fields: list = ["ore", "apple", "wheat", "fish"]
) -> dict:
    # 从数据库中读取http://47.95.21.135:8082/ammPool/getAveragePrice
    response = fetch_json(
        f"{GAME_BACKEND_URL}/bag/getByCharacterId/{userid}",
        timeout=GAME_BACKEND_TIMEOUT,
        _logger=logger,
        error_message="Failed to get inventory from game backend",
    )

    # 只保留ore, apple, wheat, fish
    inventory_dict = {}
    try:
        for x in response:
            if x["itemName"].lower() in filter_fields:
                inventory_dict[x["itemName"]] = x["itemQuantity"]
            if x["itemName"].lower() == "iron_ore":
                inventory_dict["ore"] = x["itemQuantity"]
    except KeyError:
        logger.error("Failed to get inventory from game backend")
    return inventory_dict


async def get_inventory_async(
    userid: int, filter_fields: list = ["ore", "apple", "wheat", "fish"]
) -> dict:
    """
    Asynchronously retrieves the user's inventory from the game backend.

    Args:
        userid (int): The ID of the user.
        filter_fields (list): The list of fields to filter the inventory items.

    Returns:
        dict: Filtered inventory data.
    """
    response = await fetch_json_async(
        f"{GAME_BACKEND_URL}/bag/getByCharacterId/{userid}",
        timeout=GAME_BACKEND_TIMEOUT,
        _logger=logger,
        error_message="Failed to get inventory from game backend",
    )

    # Only keep specified fields
    inventory_dict = {}
    try:
        for x in response:
            item_name = x.get("itemName", "").lower()
            if item_name in filter_fields:
                inventory_dict[x["itemName"]] = x.get("itemQuantity", 0)
            if item_name == "iron_ore":
                inventory_dict["ore"] = x.get("itemQuantity", 0)
    except (KeyError, TypeError):
        logger.error("Failed to parse inventory data from game backend")
    return inventory_dict


def get_market_data_from_db(fields: list = ["ore", "apple", "wheat", "fish"]):
    # Market data
    price_response = fetch_json(
        AMM_POOL_GET_AVG_PRICE,
        timeout=GAME_BACKEND_TIMEOUT,
        _logger=logger,
        error_message="Failed to get market data from AMM pool",
    )
    market_data_dict = dict(
        {x["name"]: x["averagePrice"] for x in price_response if x["name"] in fields}
    )
    return market_data_dict


async def fetch_game_db_character_response_async(userid: int) -> dict:
    """
    Asynchronously fetches character data from the game database.

    Args:
        userid (int): The ID of the user.

    Returns:
        dict: The game database character response.
    """
    response = await fetch_json_async(
        f"{GAME_BACKEND_URL}/characters/getById/{userid}",
        timeout=GAME_BACKEND_TIMEOUT,
        _logger=logger,
        error_message="Failed to get character data from game backend",
    )
    return response


async def fetch_agent_db_response_async(userid: int) -> dict:
    """
    Asynchronously fetches character data from the agent database.

    Args:
        userid (int): The ID of the user.

    Returns:
        dict: The agent database response.
    """
    response = await fetch_api_data_async(
        "POST",
        endpoint="/characters/get",
        userid=userid,
        _logger=logger,
        timeout=GAME_BACKEND_TIMEOUT,
    )
    if response.get("code") == 0:
        logger.info(
            "🆕 No character data found in agent database, creating new character"
        )
        return {}
    return response


async def get_character_data_async(userid: int) -> dict:
    """
    Asynchronously constructs the character_data dictionary for a user.

    Args:
        userid (int): The ID of the user.

    Returns:
        dict: The character data dictionary.
    """
    # Fetch data concurrently using asyncio.gather
    game_db_task = asyncio.create_task(fetch_game_db_character_response_async(userid))
    agent_db_task = asyncio.create_task(fetch_agent_db_response_async(userid))

    game_db_character_response, agent_db_response = await asyncio.gather(
        game_db_task, agent_db_task
    )

    # Fetch inventory asynchronously
    inventory = await get_inventory_async(
        userid, filter_fields=["ore", "apple", "wheat", "fish"]
    )

    # Construct character_data
    try:
        character_data = {
            "health": game_db_character_response.get("health"),
            "energy": game_db_character_response.get("energy"),
            "education": game_db_character_response.get("education"),
            "inventory": inventory,
            "characterName": game_db_character_response.get("characterName"),
            "gender": (
                "Male" if game_db_character_response.get("isMale") == 1 else "Female"
            ),
            # agent_db_response
            "relationship": agent_db_response.get("relationship"),
            "personality": agent_db_response.get("personality"),
            "long_term_goal": agent_db_response.get("long_term_goal"),
            "short_term_goal": agent_db_response.get("short_term_goal"),
            "language_style": agent_db_response.get("language_style"),
            "biography": agent_db_response.get("biography"),
        }
    except AttributeError:
        logger.error(f"Failed to get character data")
        return {}

    return character_data


async def get_initial_state_from_db(userid, websocket):
    # 获取市场数据
    # 获取角色数据
    character_data = await get_character_data_async(userid)
    if not character_data:
        return {}
    state = {
        "userid": userid,
        "character_stats": character_data,
        "public_data": {"market_data": get_market_data_from_db()},
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
        "message_queue": asyncio.Queue(),
        "event_queue": asyncio.Queue(),
        "false_action_queue": asyncio.Queue(),
        "websocket": websocket,
        "current_pointer": "Sensing_Route",
    }
    return state
    # initial_state = {
    #     "userid": userid,
    #     "character_stats": {
    #         "name": "Alice",
    #         "gender": "Female",
    #         "slogan": "Need to be rich!Need to be educated!",
    #         "description": "A risk lover. Always looking for the next big thing.",
    #         "role": "Investor",
    #         "inventory": get_inventory(userid),
    #         "health": 100,
    #         "energy": 100,
    #     },
    # "decision": {
    #     "need_replan": False,
    #     "action_description": [],
    #     "action_result": [],
    #     "new_plan": [],
    #     "daily_objective": [],
    #     "meta_seq": [],
    #     "reflection": [],
    # },
    # "meta": {
    #     "tool_functions": tool_functions_easy,
    #     "day": "",
    #     "available_locations": [
    #         "school",
    #         "workshop",
    #         "home",
    #         "farm",
    #         "mall",
    #         "square",
    #         "hospital",
    #         "fruit",
    #         "harvest",
    #         "fishing",
    #         "mine",
    #         "orchard",
    #     ],
    # },
    # "prompts": {
    #     "daily_goal": "",
    #     "refer_to_previous": False,
    #     "life_style": "Casual",
    #     "daily_objective_ar": "",
    #     "task_priority": [],
    #     "max_actions": 10,
    #     "meta_seq_ar": "",
    #     "replan_time_limit": 3,
    #     "meta_seq_adjuster_ar": "",
    #     "focus_topic": [],
    #     "depth_of_reflection": "Moderate",
    #     "reflection_ar": "",
    #     "level_of_detail": "Moderate",
    #     "tone_and_style": "",
    # },
    # "public_data": {
    #     "market_data": market_data_dict,
    # },
    # "message_queue": asyncio.Queue(),
    # "event_queue": asyncio.Queue(),
    # "false_action_queue": asyncio.Queue(),
    # "websocket": websocket,
    # "current_pointer": "Sensing_Route",
    # }


def generate_initial_state_hardcoded(userid, websocket):
    # 从数据库中读取http://47.95.21.135:8082/ammPool/getAveragePrice
    try:
        price_response = requests.get(
            AMM_POOL_GET_AVG_PRICE, timeout=GAME_BACKEND_TIMEOUT
        )
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

    # =======
    # def get_inventory(userid) -> dict:
    #     # 从数据库中读取http://47.95.21.135:8082/ammPool/getAveragePrice
    #     response = requests.get(f"http://47.95.21.135:8082/bag/getByCharacterId/{userid}")
    #     # 只保留ore, apple, wheat, fish
    #     inventory_dict = {}
    #     for x in response.json()["data"]:
    #         if x["itemName"].lower() in ["apple", "wheat", "fish"]:
    #             inventory_dict[x["itemName"]] = x["itemQuantity"]
    #         if x["itemName"].lower() == "iron_ore":
    #             inventory_dict["ore"] = x["itemQuantity"]

    #     return inventory_dict

    # def generate_initial_state_hardcoded(userid, websocket):
    #     # 从数据库中读取http://47.95.21.135:8082/ammPool/getAveragePrice
    #     price_response = requests.get("http://47.95.21.135:8082/ammPool/getAveragePrice")
    #     market_data = price_response.json()["data"]
    #     market_data_dict = dict(
    #         {
    #             x["name"]: x["averagePrice"]
    #             for x in market_data
    #             if x["name"] in ["ore", "apple", "wheat", "fish"]
    #         }
    #     )
    # >>>>>>> dev
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
    print(asyncio.run(get_initial_state_from_db(43, None)))
