import requests
import os
from json import JSONDecodeError
import asyncio
from dotenv import load_dotenv
import aiohttp
from loguru import logger

load_dotenv()
GAME_BACKEND_URL = os.getenv("GAME_BACKEND_URL")
GAME_BACKEND_TIMEOUT = int(os.getenv("GAME_BACKEND_TIMEOUT"))
AGENT_BACKEND_URL = os.getenv("AGENT_BACKEND_URL")


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
        if method == "GET":
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params={"characterId": userid}, timeout=timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        else:
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
        url=f"{GAME_BACKEND_URL}/ammPool/getAveragePrice",
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
        "GET",
        endpoint="/characters/",
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
    market_data = get_market_data_from_db()
    # 获取角色数据
    character_data = await get_character_data_async(userid)
    state = {
        "userid": userid,
        "character_stats": character_data,
        "public_data": {"market_data": market_data},
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


def generate_initial_state_hardcoded(userid, websocket):
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
            "market_data": get_market_data_from_db(),
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
    3. gofishing [hours:int]: Fish for fish, costing energy.
Constraints: Must have enough energy and be in the fishing area.\n
    4. harvest [hours:int]: Harvest crops, costing energy.
Constraints: Must have enough energy and be in the harvest area.\n
    5. sleep [hours:int]: Sleep to recover energy and health.
Constraints: Must be at home.\n
    6. study [hours:int]: Study to achieve a higher degree, will cost money.
Constraints: Must be in school and have enough money.\n
    8. gomining [hours:int]: Mine for ore, costing energy.
Constraints: Must have enough energy and be in the mine.\n
    17. buy [itemType:string] [amount:int]: Purchase items, costing money.
Constraints: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(ore,bread,apple,wheat,fish)\n
    18. sell [itemType:string] [amount:int]: Sell items for money. The ONLY way to get money.
Constraints: Must have enough items in inventory. ItemType:(ore,bread,apple,wheat,fish)\n
    20. showallitem: Show all items in inventory.
Constraints: None
    21. getprice [itemType:string]: Get the price of an item.
Constraints: None
"""


if __name__ == "__main__":
    print(asyncio.run(get_initial_state_from_db(29, "websocket")))
    # print(generate_initial_state_hardcoded(29, "websocket"))
