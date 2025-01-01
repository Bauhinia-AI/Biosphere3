# database_api_utils.py
import httpx
import asyncio
import os
import logging
import time

# 在项目根目录下创建 logs 文件夹
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "database_api_utils.log")),
        logging.StreamHandler(),
    ],
)

# BASE_URL = os.getenv("API_URL")
BASE_URL = os.getenv("BASE_URL")


# 异步函数
async def make_api_request_async(
    method: str,
    endpoint: str,
    params: dict = None,
    data: dict = None,
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, params=params)
            else:
                response = await client.request(method, url, json=data)

            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise Exception(f"API request to {url} failed: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"API request to {url} failed with status code {e.response.status_code}"
            )


# 同步函数
def make_api_request_sync(
    method: str,
    endpoint: str,
    params: dict = None,
    data: dict = None,
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    try:
        with httpx.Client() as client:
            if method == "GET":
                response = client.get(url, params=params)
            else:
                response = client.request(method, url, json=data)

        response.raise_for_status()  # 如果状态码不是 2xx，会抛出异常

        return response.json()  # 返回 JSON 响应
    except httpx.RequestError as e:
        raise Exception(f"API request to {url} failed: {e}")
    except httpx.HTTPStatusError as e:
        raise Exception(
            f"API request to {url} failed with status code {e.response.status_code}"
        )


async def get_all_characters():
    url = os.getenv("CHARACTERS_GETALL_URL")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)  # Make the GET request asynchronously
            response.raise_for_status()  # Check if the request was successful
            response_data = response.json()
            return response_data.get("data", [])
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logging.error(f"Error fetching characters from {url}: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return []


async def store_or_update_character(character_data):
    gender = "Male" if character_data["isMale"] == 1 else "Female"
    character_data_to_store = {
        "characterId": character_data["id"],
        "characterName": character_data["characterName"],
        "gender": gender,
        "spriteId": character_data["spriteId"],
    }

    store_response = await make_api_request_async(
        "POST", "/characters/store", data=character_data_to_store
    )
    print(store_response)

    if store_response.get("code") == 2:
        update_data = {
            "characterId": character_data["id"],
            "update_fields": {
                "characterName": character_data["characterName"],
                "gender": gender,
                "spriteId": character_data["spriteId"],
            },
        }
        update_response = await make_api_request_async(
            "PUT", "/characters", data=update_data
        )
        print(update_response)


async def process_characters():
    characters = await get_all_characters()
    tasks = [store_or_update_character(character) for character in characters]
    await asyncio.gather(*tasks)


async def create_agent_prompts_for_characters():
    characters = await get_all_characters()
    for character in characters:
        agent_prompt_data = {
            "characterId": character["id"],
            "daily_goal": None,
            "refer_to_previous": None,
            "life_style": None,
            "daily_objective_ar": None,
            "task_priority": None,
            "max_actions": None,
            "meta_seq_ar": None,
            "replan_time_limit": None,
            "meta_seq_adjuster_ar": None,
            "focus_topic": None,
            "depth_of_reflection": None,
            "reflection_ar": None,
            "level_of_detail": None,
            "tone_and_style": None,
        }
        response = await make_api_request_async(
            "POST", "/agent_prompt", data=agent_prompt_data
        )
        print(f"Agent prompt created for character ID {character['id']}: {response}")
