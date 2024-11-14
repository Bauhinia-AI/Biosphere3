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

# BASE_URL = "http://47.95.21.135:8085"
BASE_URL = "http://localhost:8085"


async def make_api_request_async(
    method: str, endpoint: str, data: dict = None, retries: int = 3, delay: int = 2
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    for attempt in range(retries):
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:  # Set timeout to 30 seconds
            try:
                if method == "GET":
                    response = await client.get(url, params=data)
                else:
                    response = await client.request(method, url, json=data)

                response.raise_for_status()
                response_data = response.json()

                # Check if `code` is not 1
                if response_data["code"] != 1:
                    logging.warning(
                        "Error detected in response from endpoint %s: %s",
                        endpoint,
                        response_data["message"],
                    )
                else:
                    logging.info(response_data["message"])

                return response_data

            except httpx.TimeoutException as e:
                logging.warning(
                    f"Attempt {attempt + 1}/{retries} failed: Request timed out"
                )
                logging.error(f"Error details: {str(e)}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(
                        f"API request to {url} failed after {retries} attempts due to timeout. Error details: {str(e)}"
                    )

            except httpx.RequestError as e:
                logging.warning(
                    f"Attempt {attempt + 1}/{retries} failed: Request error"
                )
                logging.error(f"Error details: {str(e)}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(
                        f"API request to {url} failed after {retries} attempts. Error details: {str(e)}"
                    )

            except httpx.HTTPStatusError as e:
                logging.warning(
                    f"Attempt {attempt + 1}/{retries} failed: HTTP status error"
                )
                logging.error(f"Status code: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise Exception(
                        f"API request to {url} failed after {retries} attempts, status code: {e.response.status_code}. Response content: {e.response.text}"
                    )


# Synchronous function
def make_api_request_sync(
    method: str, endpoint: str, data: dict = None, retries: int = 3, delay: int = 2
):
    url = f"{BASE_URL}{endpoint}"
    method = method.upper()

    for attempt in range(retries):
        try:
            with httpx.Client(timeout=30) as client:  # Set timeout
                if method == "GET":
                    response = client.get(url, params=data)
                else:
                    response = client.request(method, url, json=data)

            response.raise_for_status()
            response_data = response.json()

            # Check if `code` is not 1
            if response_data["code"] != 1:
                logging.warning(
                    "Error detected in response from endpoint %s: %s",
                    endpoint,
                    response_data["message"],
                )
            else:
                logging.info(response_data["message"])

            return response_data

        except httpx.RequestError as e:
            logging.warning(f"Attempt {attempt + 1}/{retries} failed: {e}")
            logging.error(f"Error type: {type(e).__name__}")
            logging.error(f"Error details: {str(e)}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise Exception(
                    f"API request to {url} failed after {retries} attempts. Error type: {type(e).__name__}, Error details: {str(e)}"
                )

        except httpx.HTTPStatusError as e:
            logging.warning(f"Attempt {attempt + 1}/{retries} failed: {e}")
            logging.error(f"Status code: {e.response.status_code}")
            logging.error(f"Response content: {e.response.text}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise Exception(
                    f"API request to {url} failed after {retries} attempts, status code: {e.response.status_code}. Response content: {e.response.text}"
                )


async def main():
    # Test storing and retrieving character
    character_data = {
        "characterId": 102,
        "characterName": "Diana",
        "gender": "Female",
        "slogan": "Swift and silent.",
        "description": "An agile ranger with unparalleled archery skills.",
        "role": "Ranger",
        "task": "Scout and protect the realm",
    }
    print(
        "Storing character:",
        await make_api_request_async("POST", "/characters/store", character_data),
    )

    # If characterId already exists
    print(
        "Storing character (duplicate):",
        await make_api_request_async("POST", "/characters/store", character_data),
    )

    print(
        "Retrieving character:",
        await make_api_request_async("POST", "/characters/get", {"characterId": 102}),
    )

    print(
        "Retrieving character RAG:",
        await make_api_request_async(
            "POST",
            "/characters/get_rag",
            {"characterId": 1, "topic": "探索森林", "k": 3},
        ),
    )

    # Test retrieving character RAG in list
    character_list = [2, 3, 4]  # Assuming these are the character IDs you want to query
    print(
        "Retrieving character RAG in list:",
        await make_api_request_async(
            "POST",
            "/characters/get_rag_in_list",
            {
                "characterId": 1,
                "characterList": character_list,
                "topic": "探索森林",
                "k": 2,
            },
        ),
    )

    # Test updating character
    character_update_data = {"slogan": "Silent but deadly."}
    print(
        "Updating character:",
        await make_api_request_async(
            "POST",
            "/characters/update",
            {"characterId": 102, "update_fields": character_update_data},
        ),
    )
    print(
        "Retrieving Updated character:",
        await make_api_request_async("POST", "/characters/get", {"characterId": 102}),
    )

    # Test storing and retrieving conversation
    conversation_data = {
        "characterIds": [2, 3],
        "dialogue": [
            {"Bob": "XXXX"},
            {"sdjf": "HJFHFDKSD"},
            {"Bob": "JFLKFJDL"},
        ],
        "start_day": 2,  # Updated field
        "start_time": "9:00:00",  # Updated field
    }
    print(
        "Storing Conversation:",
        await make_api_request_async("POST", "/conversations/store", conversation_data),
    )

    print(
        "Retrieving Conversation by ID, Day, and Time:",
        await make_api_request_async(
            "POST",
            "/conversations/get_by_id_day_time",
            {
                "characterIds_list": [2, 1],  # Updated to characterIds_list
                "day": 2,
                "time": "9:00:00",
            },
        ),
    )

    print(
        "Retrieving Conversations by ID and Day:",
        await make_api_request_async(
            "POST",
            "/conversations/get_by_id_and_day",
            {
                "characterId": 2,
                "day": 2,
            },
        ),
    )

    print(
        "Retrieving Conversation:",
        await make_api_request_async(
            "POST",
            "/conversations/get_with_characterIds",
            {"characterIds_list": [2, 1], "k": 1},
        ),
    )

    print(
        "Retrieving Conversation:",
        await make_api_request_async(
            "POST",
            "/conversations/get_containing_characterId",
            {"characterId": 2, "k": 1},
        ),
    )

    # Test storing and retrieving impression
    impression_data = {"from_id": 1, "to_id": 2, "impression": "lalalala"}
    print(
        "Storing Impression:",
        await make_api_request_async("POST", "/impressions/store", impression_data),
    )
    print(
        "Retrieving Impression:",
        await make_api_request_async(
            "POST", "/impressions/get", {"from_id": 1, "to_id": 2, "k": 1}
        ),
    )

    # Test storing and retrieving action
    action_data = {
        "characterId": 30021,
        "action": "nav",
        "result": {
            "characterId": 1,
            "messageCode": 3,
            "messageName": "actionresult",
            "data": {
                "actionName": "nav",
                "actionCode": 1,
                "result": True,
                "gameTime": "12:23:10",
                "msg": "Navigated to None navigated to None successfully.",
            },
        },
        "description": "I successfully navigated to the destination.",
    }
    print(
        "Storing Action:",
        await make_api_request_async("POST", "/actions/store", action_data),
    )
    print(
        "Retrieving Action:",
        await make_api_request_async(
            "POST", "/actions/get", {"characterId": 30021, "action": "nav", "k": 1}
        ),
    )

    # Test storing and retrieving descriptor
    descriptor_data = {
        "failed_action": "Find the hidden path",
        "action_id": 6,
        "characterId": 102,
        "reflection": "Should have looked at the map first.",
    }
    print(
        "Storing Descriptor:",
        await make_api_request_async("POST", "/descriptors/store", descriptor_data),
    )
    print(
        "Retrieving Descriptor:",
        await make_api_request_async(
            "POST", "/descriptors/get", {"action_id": 6, "characterId": 102, "k": 1}
        ),
    )

    # Test storing and retrieving daily objectives
    daily_objective_data = {
        "characterId": 102,
        "objectives": ["Scout the northern woods", "Gather herbs", "Set up camp"],
    }
    print(
        "Storing Daily Objective:",
        await make_api_request_async(
            "POST", "/daily_objectives/store", daily_objective_data
        ),
    )
    print(
        "Retrieving Daily Objectives:",
        await make_api_request_async(
            "POST", "/daily_objectives/get", {"characterId": 102, "k": 1}
        ),
    )

    # Test storing and retrieving plans
    plan_data = {
        "characterId": 102,
        "detailed_plan": "1. Scout woods at dawn. 2. Return to camp by dusk.",
    }
    print(
        "Storing Plan:", await make_api_request_async("POST", "/plans/store", plan_data)
    )
    print(
        "Retrieving Plans:",
        await make_api_request_async(
            "POST", "/plans/get", {"characterId": 102, "k": 1}
        ),
    )

    # Test storing and retrieving meta sequences
    meta_seq_data = {
        "characterId": 102,
        "meta_sequence": ["scout_area()", "gather_resources()", "set_up_camp()"],
    }
    print(
        "Storing Meta Sequence:",
        await make_api_request_async("POST", "/meta_sequences/store", meta_seq_data),
    )
    print(
        "Retrieving Meta Sequences:",
        await make_api_request_async(
            "POST", "/meta_sequences/get", {"characterId": 102, "k": 1}
        ),
    )

    # Updating meta sequence
    update_meta_seq_data = {
        "characterId": 102,
        "meta_sequence": [
            "new_scout_area()",
            "new_gather_resources()",
            "new_set_up_camp()",
        ],
    }
    print(
        "Updating Meta Sequence:",
        await make_api_request_async(
            "POST", "/meta_sequences/update", update_meta_seq_data
        ),
    )
    print(
        "Retrieving Updated Meta Sequences:",
        await make_api_request_async(
            "POST", "/meta_sequences/get", {"characterId": 102, "k": 1}
        ),
    )

    # Test storing and retrieving tools
    tool_data = {"API": "find-path", "text": "Pathfinding tool", "code": "find_path()"}
    print(
        "Storing Tool:", await make_api_request_async("POST", "/tools/store", tool_data)
    )
    print(
        "Retrieving Tools:",
        await make_api_request_async(
            "POST", "/tools/get", {"API": "find-path", "k": 1}
        ),
    )

    # Test storing and retrieving diaries
    diary_data = {
        "characterId": 102,
        "diary_content": "Today, I explored the forest and found new paths.",
    }
    print(
        "Storing Diary:",
        await make_api_request_async("POST", "/diaries/store", diary_data),
    )
    print(
        "Retrieving Diaries:",
        await make_api_request_async(
            "POST", "/diaries/get", {"characterId": 102, "k": 1}
        ),
    )

    # Vector Search
    vector_search_data = {
        "query_text": "探索生活习惯",
        "fields_to_return": ["characterIds", "dialogue"],
        "collection_name": "conversation",
        "k": 5,
    }
    print(
        "Vector Search:",
        await make_api_request_async("POST", "/vector_search/", vector_search_data),
    )

    # Test inserting data
    document = {
        "characterId": 200,
        "characterName": "Test User",
        "gender": "Non-binary",
        "slogan": "Testing insert_data",
        "description": "This is a test character inserted via insert_data.",
        "role": "Tester",
        "task": "Testing API endpoints",
    }
    print(
        "Inserting Data:",
        await make_api_request_async(
            "POST",
            "/crud/insert",
            {"collection_name": "character", "document": document},
        ),
    )

    print(
        "Finding Data:",
        await make_api_request_async(
            "POST",
            "/crud/find",
            {"collection_name": "character", "query": {"characterId": 200}},
        ),
    )

    # Test updating data
    update_query = {"characterId": 200}
    update_fields = {"$set": {"characterName": "Updated Test User"}}
    print(
        "Updating Data:",
        await make_api_request_async(
            "POST",
            "/crud/update",
            {
                "collection_name": "character",
                "query": update_query,
                "update": update_fields,
            },
        ),
    )

    print(
        "Finding Updated Data:",
        await make_api_request_async(
            "POST",
            "/crud/find",
            {"collection_name": "character", "query": {"characterId": 200}},
        ),
    )

    # Test deleting data
    print(
        "Deleting Data:",
        await make_api_request_async(
            "POST",
            "/crud/delete",
            {"collection_name": "character", "query": {"characterId": 200}},
        ),
    )

    print(
        "Finding Deleted Data:",
        await make_api_request_async(
            "POST",
            "/crud/find",
            {"collection_name": "character", "query": {"characterId": 200}},
        ),
    )

    # Test retrieving conversations containing a specific character ID
    print(
        "Retrieving Conversations Containing character ID 1:",
        await make_api_request_async(
            "POST",
            "/conversations/get_containing_characterId",
            {"characterId": 1, "k": 1},
        ),
    )

    # Test storing and retrieving CV
    cv_data_1 = {
        "jobid": 3,
        "characterId": 201,
        "CV_content": "CV内容5",
        "week": 1,
        "election_result": "not_yet",
    }
    cv_data_2 = {
        "jobid": 3,
        "characterId": 202,
        "CV_content": "CV内容6",
        "week": 2,
        "election_result": "not_yet",
    }
    cv_data_3 = {
        "jobid": 4,
        "characterId": 201,
        "CV_content": "CV内容7",
        "week": 1,
        "election_result": "not_yet",
    }
    cv_data_4 = {
        "jobid": 4,
        "characterId": 203,
        "CV_content": "CV内容8",
        "week": 3,
        "election_result": "not_yet",
    }

    print("Storing CV 1:", await make_api_request_async("POST", "/cv/store", cv_data_1))
    print("Storing CV 2:", await make_api_request_async("POST", "/cv/store", cv_data_2))
    print("Storing CV 3:", await make_api_request_async("POST", "/cv/store", cv_data_3))
    print("Storing CV 4:", await make_api_request_async("POST", "/cv/store", cv_data_4))

    # Test updating election result
    update_election_result_data_1 = {
        "characterId": 201,
        "election_result": "succeeded",
        "jobid": 3,
        "week": 1,
    }
    update_election_result_data_2 = {
        "characterId": 202,
        "election_result": "failed",
        "jobid": 3,
    }
    update_election_result_data_3 = {
        "characterId": 203,
        "election_result": "succeeded",
        "jobid": 4,
    }

    print(
        "Updating Election Result 1:",
        await make_api_request_async(
            "POST", "/cv/update_election_result", update_election_result_data_1
        ),
    )
    print(
        "Updating Election Result 2:",
        await make_api_request_async(
            "POST", "/cv/update_election_result", update_election_result_data_2
        ),
    )
    print(
        "Updating Election Result 3:",
        await make_api_request_async(
            "POST", "/cv/update_election_result", update_election_result_data_3
        ),
    )

    # Test retrieving CVs
    print(
        "Retrieving CV for jobid=3, characterId=201, week=1:",
        await make_api_request_async(
            "POST", "/cv/get", {"jobid": 3, "characterId": 201, "week": 1}
        ),
    )
    print(
        "Retrieving CV for jobid=3, characterId=202, week=2:",
        await make_api_request_async(
            "POST", "/cv/get", {"jobid": 3, "characterId": 202, "week": 2}
        ),
    )
    print(
        "Retrieving CV for jobid=4, characterId=201, week=1:",
        await make_api_request_async(
            "POST", "/cv/get", {"jobid": 4, "characterId": 201, "week": 1}
        ),
    )
    print(
        "Retrieving CV for jobid=4, characterId=203, week=3:",
        await make_api_request_async(
            "POST", "/cv/get", {"jobid": 4, "characterId": 203, "week": 3}
        ),
    )

    # Test storing and retrieving encounter count
    encounter_data = {"from_id": 1, "to_id": 2, "count": 1}
    print(
        "Storing Encounter Count:",
        await make_api_request_async("POST", "/encounter_count/store", encounter_data),
    )

    print(
        "Retrieving Encounter Count:",
        await make_api_request_async(
            "POST", "/encounter_count/get", {"from_id": 1, "to_id": 2}
        ),
    )

    # Incrementing encounter count
    print(
        "Incrementing Encounter Count:",
        await make_api_request_async(
            "POST", "/encounter_count/increment", {"from_id": 2, "to_id": 2}
        ),
    )

    # Updating encounter count to a specific value
    print(
        "Updating Encounter Count:",
        await make_api_request_async(
            "POST", "/encounter_count/update", {"from_id": 1, "to_id": 2, "count": 5}
        ),
    )

    print(
        "Retrieving Encounters by From ID:",
        await make_api_request_async(
            "POST", "/encounter_count/get_by_from_id", {"from_id": 1, "k": 3}
        ),
    )

    # Test storing and retrieving intimacy
    intimacy_data = {"from_id": 1, "to_id": 3, "intimacy_level": 55}
    print(
        "Storing Intimacy:",
        await make_api_request_async("POST", "/intimacy/store", intimacy_data),
    )
    print(
        "Retrieving Intimacy:",
        await make_api_request_async(
            "POST", "/intimacy/get", {"from_id": 1, "to_id": 3}
        ),
    )
    print(
        "Retrieving Intimacy by from_id:",
        await make_api_request_async("POST", "/intimacy/get", {"from_id": 1}),
    )
    print(
        "Retrieving Intimacy by to_id:",
        await make_api_request_async("POST", "/intimacy/get", {"to_id": 3}),
    )
    print(
        "Retrieving Intimacy by level range:",
        await make_api_request_async(
            "POST",
            "/intimacy/get",
            {"intimacy_level_min": 50, "intimacy_level_max": 60},
        ),
    )
    print(
        "Retrieving Intimacy by from_id and level range:",
        await make_api_request_async(
            "POST",
            "/intimacy/get",
            {"from_id": 1, "intimacy_level_min": 50, "intimacy_level_max": 60},
        ),
    )

    update_intimacy_data = {"from_id": 1, "to_id": 3, "new_intimacy_level": 77}
    print(
        "Updating Intimacy:",
        await make_api_request_async("POST", "/intimacy/update", update_intimacy_data),
    )

    # Decrease all intimacy levels by 1
    print(
        "Decreasing All Intimacy Levels:",
        await make_api_request_async("POST", "/intimacy/decrease_all", {}),
    )

    # Retrieve intimacy after decrease
    print(
        "Retrieving Intimacy after Decrease:",
        await make_api_request_async(
            "POST", "/intimacy/get", {"from_id": 1, "to_id": 3}
        ),
    )

    # Test storing and retrieving knowledge
    knowledge_data = {
        "characterId": 101,
        "day": 1,
        "environment_information": "Sunny day in the forest.",
        "personal_information": "Learned new archery skills.",
    }
    print(
        "Storing Knowledge:",
        await make_api_request_async("POST", "/knowledge/store", knowledge_data),
    )

    print(
        "Retrieving Knowledge:",
        await make_api_request_async(
            "POST", "/knowledge/get", {"characterId": 101, "day": 1}
        ),
    )

    print(
        "Retrieving Latest Knowledge:",
        await make_api_request_async(
            "POST", "/knowledge/get_latest", {"characterId": 101, "k": 1}
        ),
    )

    # Updating knowledge
    updated_knowledge_data = {
        "characterId": 101,
        "day": 1,
        "environment_information": "Cloudy day in the forest.",
        "personal_information": "Practiced archery with new techniques.",
    }
    print(
        "Updating Knowledge:",
        await make_api_request_async(
            "POST", "/knowledge/update", updated_knowledge_data
        ),
    )

    # Retrieve updated knowledge
    print(
        "Retrieving Updated Knowledge:",
        await make_api_request_async(
            "POST", "/knowledge/get", {"characterId": 101, "day": 1}
        ),
    )

    # 创建角色弧光
    character_arc_data = {
        "characterId": 1,
        "category": [
            {"item": "skill", "origin_value": "beginner"},
            {"item": "emotion", "origin_value": "neutral"},
        ],
    }
    print(
        "Storing Character Arc:",
        await make_api_request_async(
            "POST", "/character_arc/store", character_arc_data
        ),
    )

    # 创建角色弧光变化
    character_arc_change_data_1 = {
        "characterId": 1,
        "item": "skill",
        "cause": "参加职业培训",
        "context": "在朋友的建议下参加了当地的职业技能培训班",
        "change": "获得新技能",
    }
    print(
        "Storing Character Arc Change 1:",
        await make_api_request_async(
            "POST", "/character_arc/store_change", character_arc_change_data_1
        ),
    )

    character_arc_change_data_2 = {
        "characterId": 1,
        "item": "skill",
        "cause": "完成高级课程",
        "context": "通过在线学习平台完成了高级课程",
        "change": "技能提升",
    }
    print(
        "Storing Character Arc Change 2:",
        await make_api_request_async(
            "POST", "/character_arc/store_change", character_arc_change_data_2
        ),
    )

    character_arc_change_data_3 = {
        "characterId": 1,
        "item": "emotion",
        "cause": "收到好消息",
        "context": "得知自己通过了考试",
        "change": "略微积极",
    }
    print(
        "Storing Character Arc Change 3:",
        await make_api_request_async(
            "POST", "/character_arc/store_change", character_arc_change_data_3
        ),
    )

    # 获取角色弧光
    print(
        "Retrieving Character Arc:",
        await make_api_request_async("POST", "/character_arc/get", {"characterId": 1}),
    )

    # 获取角色弧光及其变化过程
    k = 2  # 选择变化过程的数量
    print(
        "Retrieving Character Arc with Changes:",
        await make_api_request_async(
            "POST", "/character_arc/get_with_changes", {"characterId": 1, "k": k}
        ),
    )

    # 更新角色弧光
    updated_character_arc_data = {
        "characterId": 1,
        "category": [
            {"item": "skill", "origin_value": "intermediate"},
            {"item": "emotion", "origin_value": "happy"},
        ],
    }
    print(
        "Updating Character Arc:",
        await make_api_request_async(
            "POST", "/character_arc/update", updated_character_arc_data
        ),
    )

    # 获取角色弧光变化
    print(
        "Retrieving Character Arc Changes for 'skill':",
        await make_api_request_async(
            "POST",
            "/character_arc/get_changes",
            {"characterId": 1, "item": "skill", "k": k},
        ),
    )
    print(
        "Retrieving Character Arc Changes for 'emotion':",
        await make_api_request_async(
            "POST",
            "/character_arc/get_changes",
            {"characterId": 1, "item": "emotion", "k": k},
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
