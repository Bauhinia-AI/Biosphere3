# app/client.py
import sys
import os
import logging
import requests
import json
import time
from datetime import datetime

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import config  # 如果需要使用 config

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 在项目根目录下创建 logs 文件夹
log_directory = os.path.join(project_root, "logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "client.log")),
        logging.StreamHandler(),
    ],
)


class APIClient:
    def __init__(self, base_url="http://localhost:8085", retries=3, delay=5):
        self.base_url = base_url
        self.retries = retries
        self.delay = delay

    def _make_request(self, method, url, json_data=None):
        for attempt in range(1, self.retries + 1):
            try:
                logging.debug(
                    f"Making {method} request to {url} with data: {json_data}"
                )
                if method == "POST":
                    response = requests.post(url, json=json_data, timeout=20)
                elif method == "GET":
                    response = requests.get(url, timeout=20)
                else:
                    raise ValueError("Unsupported HTTP method")

                response_data = (
                    response.json()
                    if response.headers.get("Content-Type") == "application/json"
                    else {}
                )

                if (
                    "code" in response_data
                    and "message" in response_data
                    and "data" in response_data
                ):
                    return response_data
                else:
                    return {
                        "code": 0,
                        "message": "Unexpected response structure from server.",
                        "data": None,
                    }

            except requests.exceptions.RequestException as e:
                logging.error(f"Error on attempt {attempt}: {e}", exc_info=True)
                if attempt < self.retries:
                    logging.info(f"Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    return {
                        "code": 0,
                        "message": "Network error, unable to connect to the server.",
                        "data": None,
                    }

    # API调用方法，使用新的分路由

    # CRUD操作
    def insert_data(self, collection_name, document):
        return self._make_request(
            "POST",
            f"{self.base_url}/crud/insert",
            {"collection_name": collection_name, "document": document},
        )

    def update_data(self, collection_name, query, update, upsert=False, multi=False):
        return self._make_request(
            "POST",
            f"{self.base_url}/crud/update",
            {
                "collection_name": collection_name,
                "query": query,
                "update": update,
                "upsert": upsert,
                "multi": multi,
            },
        )

    def delete_data(self, collection_name, query, multi=False):
        return self._make_request(
            "POST",
            f"{self.base_url}/crud/delete",
            {"collection_name": collection_name, "query": query, "multi": multi},
        )

    def find_data(self, collection_name, query={}, projection=None, limit=0, sort=None):
        return self._make_request(
            "POST",
            f"{self.base_url}/crud/find",
            {
                "collection_name": collection_name,
                "query": query,
                "projection": projection,
                "limit": limit,
                "sort": sort,
            },
        )

    # Vector Search
    def vector_search(self, query_text, fields_to_return, collection_name, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/vector_search",
            {
                "query_text": query_text,
                "fields_to_return": fields_to_return,
                "collection_name": collection_name,
                "k": k,
            },
        )

    # Impressions
    def store_impression(self, from_id, to_id, impression):
        return self._make_request(
            "POST",
            f"{self.base_url}/impressions/store",
            {"from_id": from_id, "to_id": to_id, "impression": impression},
        )

    def get_impression(self, from_id, to_id, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/impressions/get",
            {"from_id": from_id, "to_id": to_id, "k": k},
        )

    # Candidates
    def get_candidates(self):
        return self._make_request("GET", f"{self.base_url}/candidates/get")

    # Conversations
    def store_conversation(self, characterIds, dialogue, start_day, start_time):
        return self._make_request(
            "POST",
            f"{self.base_url}/conversations/store",
            {
                "characterIds": characterIds,
                "dialogue": dialogue,
                "start_day": start_day,  # 新增字段
                "start_time": start_time,  # 新增字段
            },
        )

    def get_conversation_by_id_day_time(self, characterIds_list, day, time):
        return self._make_request(
            "POST",
            f"{self.base_url}/conversations/get_by_id_day_time",
            {
                "characterIds_list": characterIds_list,  # 更新为 characterIds_list
                "day": day,
                "time": time,
            },
        )

    def get_conversations_by_id_and_day(self, characterId, day):
        return self._make_request(
            "POST",
            f"{self.base_url}/conversations/get_by_id_and_day",
            {
                "characterId": characterId,
                "day": day,
            },
        )

    def get_conversations_with_characterIds(self, characterIds_list, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/conversations/get_with_characterIds",
            {"characterIds_list": characterIds_list, "k": k},
        )

    def get_conversations_containing_characterId(self, characterId, k=0):
        return self._make_request(
            "POST",
            f"{self.base_url}/conversations/get_containing_characterId",
            {"characterId": characterId, "k": k},
        )

    # CVs
    def store_cv(self, jobid, characterId, characterName, CV_content):
        return self._make_request(
            "POST",
            f"{self.base_url}/cvs/store",
            {
                "jobid": jobid,
                "characterId": characterId,
                "characterName": characterName,
                "CV_content": CV_content,
            },
        )

    def get_cv(self, jobid, characterId, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/cvs/get",
            {"jobid": jobid, "characterId": characterId, "k": k},
        )

    # Actions
    def store_action(self, characterId, action, result, description):
        return self._make_request(
            "POST",
            f"{self.base_url}/actions/store",
            {
                "characterId": characterId,
                "action": action,
                "result": result,
                "description": description,
            },
        )

    def get_action(self, characterId, action, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/actions/get",
            {"characterId": characterId, "action": action, "k": k},
        )

    # Descriptors
    def store_descriptor(self, failed_action, action_id, characterId, reflection):
        return self._make_request(
            "POST",
            f"{self.base_url}/descriptors/store",
            {
                "failed_action": failed_action,
                "action_id": action_id,
                "characterId": characterId,
                "reflection": reflection,
            },
        )

    def get_descriptor(self, action_id, characterId, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/descriptors/get",
            {"action_id": action_id, "characterId": characterId, "k": k},
        )

    # Daily Objectives
    def store_daily_objective(self, characterId, objectives):
        return self._make_request(
            "POST",
            f"{self.base_url}/daily_objectives/store",
            {"characterId": characterId, "objectives": objectives},
        )

    def get_daily_objectives(self, characterId, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/daily_objectives/get",
            {"characterId": characterId, "k": k},
        )

    # Plans
    def store_plan(self, characterId, detailed_plan):
        return self._make_request(
            "POST",
            f"{self.base_url}/plans/store",
            {"characterId": characterId, "detailed_plan": detailed_plan},
        )

    def get_plans(self, characterId, k=1):
        return self._make_request(
            "POST", f"{self.base_url}/plans/get", {"characterId": characterId, "k": k}
        )

    # Meta Sequences
    def store_meta_seq(self, characterId, meta_sequence):
        return self._make_request(
            "POST",
            f"{self.base_url}/meta_sequences/store",
            {"characterId": characterId, "meta_sequence": meta_sequence},
        )

    def get_meta_sequences(self, characterId, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/meta_sequences/get",
            {"characterId": characterId, "k": k},
        )

    def update_meta_seq(self, characterId, meta_sequence):
        return self._make_request(
            "POST",
            f"{self.base_url}/meta_sequences/update",
            {"characterId": characterId, "meta_sequence": meta_sequence},
        )

    # Tools
    def store_tool(self, API, text, code):
        return self._make_request(
            "POST",
            f"{self.base_url}/tools/store",
            {"API": API, "text": text, "code": code},
        )

    def get_tools(self, API=None, k=1):
        data = {"API": API, "k": k} if API else {"k": k}
        return self._make_request("POST", f"{self.base_url}/tools/get", data)

    # Diaries
    def store_diary(self, characterId, diary_content):
        return self._make_request(
            "POST",
            f"{self.base_url}/diaries/store",
            {"characterId": characterId, "diary_content": diary_content},
        )

    def get_diaries(self, characterId, k=1):
        return self._make_request(
            "POST", f"{self.base_url}/diaries/get", {"characterId": characterId, "k": k}
        )

    # Characters
    def store_character(
        self, characterId, characterName, gender, slogan, description, role, task
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/characters/store",
            {
                "characterId": characterId,
                "characterName": characterName,
                "gender": gender,
                "slogan": slogan,
                "description": description,
                "role": role,
                "task": task,
            },
        )

    def get_character(self, characterId):
        return self._make_request(
            "POST", f"{self.base_url}/characters/get", {"characterId": characterId}
        )

    def get_character_rag(self, characterId, topic, k):
        return self._make_request(
            "POST",
            f"{self.base_url}/characters/get_rag",
            {"characterId": characterId, "topic": topic, "k": k},
        )

    def get_character_rag_in_list(self, characterId, characterList, topic, k):
        return self._make_request(
            "POST",
            f"{self.base_url}/characters/get_rag_in_list",
            {
                "characterId": characterId,
                "characterList": characterList,
                "topic": topic,
                "k": k,
            },
        )

    def update_character(self, characterId, update_fields):
        return self._make_request(
            "POST",
            f"{self.base_url}/characters/update",
            {"characterId": characterId, "update_fields": update_fields},
        )

    # Encounter Count
    def get_encounter_count(self, from_id, to_id):
        return self._make_request(
            "POST",
            f"{self.base_url}/encounter_count/get",
            {"from_id": from_id, "to_id": to_id},
        )

    def get_encounters_by_from_id(self, from_id, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/encounter_count/get_by_from_id",
            {"from_id": from_id, "k": k},
        )

    def store_encounter_count(self, from_id, to_id, count=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/encounter_count/store",
            {"from_id": from_id, "to_id": to_id, "count": count},
        )

    def increment_encounter_count(self, from_id, to_id):
        return self._make_request(
            "POST",
            f"{self.base_url}/encounter_count/increment",
            {"from_id": from_id, "to_id": to_id},
        )

    def update_encounter_count(self, from_id, to_id, count):
        return self._make_request(
            "POST",
            f"{self.base_url}/encounter_count/update",
            {"from_id": from_id, "to_id": to_id, "count": count},
        )

    # Intimacy
    def get_intimacy(self, from_id, to_id):
        return self._make_request(
            "POST",
            f"{self.base_url}/intimacy/get",
            {"from_id": from_id, "to_id": to_id},
        )

    def store_intimacy(self, from_id, to_id, intimacy_level):
        return self._make_request(
            "POST",
            f"{self.base_url}/intimacy/store",
            {"from_id": from_id, "to_id": to_id, "intimacy_level": intimacy_level},
        )

    def update_intimacy(self, from_id, to_id, new_intimacy_level):
        return self._make_request(
            "POST",
            f"{self.base_url}/intimacy/update",
            {
                "from_id": from_id,
                "to_id": to_id,
                "new_intimacy_level": new_intimacy_level,
            },
        )

    def decrease_all_intimacy_levels(self):
        return self._make_request("POST", f"{self.base_url}/intimacy/decrease_all", {})

    # Knowledge
    def store_knowledge(
        self, characterId, day, environment_information, personal_information
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/knowledge/store",
            {
                "characterId": characterId,
                "day": day,
                "environment_information": environment_information,
                "personal_information": personal_information,
            },
        )

    def get_knowledge(self, characterId, day):
        return self._make_request(
            "POST",
            f"{self.base_url}/knowledge/get",
            {"characterId": characterId, "day": day},
        )

    def get_latest_knowledge(self, characterId, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/knowledge/get_latest",
            {"characterId": characterId, "k": k},
        )

    def update_knowledge(
        self, characterId, day, environment_information=None, personal_information=None
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/knowledge/update",
            {
                "characterId": characterId,
                "day": day,
                "environment_information": environment_information,
                "personal_information": personal_information,
            },
        )

    # Character Arc
    def store_character_arc(self, characterId, category):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc/store",
            {"characterId": characterId, "category": category},
        )

    def get_character_arc(self, characterId):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc/get",
            {"characterId": characterId},
        )

    def get_character_arc_with_changes(self, characterId, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc/get_with_changes",
            {"characterId": characterId, "k": k},
        )

    def update_character_arc(self, characterId, category):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc/update",
            {"characterId": characterId, "category": category},
        )

    # Character Arc Change
    def store_character_arc_change(self, characterId, item, cause, context, change):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc/store_change",
            {
                "characterId": characterId,
                "item": item,
                "cause": cause,
                "context": context,
                "change": change,
            },
        )

    def get_character_arc_changes(self, characterId, item, k=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc/get_changes",
            {"characterId": characterId, "item": item, "k": k},
        )


if __name__ == "__main__":
    client = APIClient(base_url="http://localhost:8085")

    # # 测试存储和检索 character
    # character_data = {
    #     "characterId": 102,
    #     "characterName": "Diana",
    #     "gender": "Female",
    #     "slogan": "Swift and silent.",
    #     "description": "An agile ranger with unparalleled archery skills.",
    #     "role": "Ranger",
    #     "task": "Scout and protect the realm",
    # }
    # print("Storing character:", client.store_character(**character_data))
    # # Storing character: {'code': 1, 'message': 'character stored successfully.', 'data': '67222a374106d9bcf5176448'}
    # print("Storing character:", client.store_character(**character_data))
    # # 若characterId已存在
    # # Storing character: {'code': 2, 'message': 'Character with characterId 102 already exists.', 'data': None}

    # print("Retrieving character:", client.get_character(102))
    # # Retrieving character: {'code': 1, 'message': 'characters retrieved successfully.', 'data': [{'characterId': 102, 'characterName': 'Diana', 'gender': 'Female', 'slogan': 'Swift and silent.', 'description': 'An agile ranger with unparalleled archery skills.', 'role': 'Ranger', 'task': 'Scout and protect the realm', 'created_at': '2024-10-30 20:23:39', 'full_profile': 'Diana; Female; Swift and silent.; An agile ranger with unparalleled archery skills.; Ranger; Scout and protect the realm'}]}
    # print(
    #     "Retrieving character RAG:",
    #     client.get_character_rag(characterId=1, topic="探索森林", k=3),
    # )
    # # Retrieving character RAG: {'code': 1, 'message': 'character RAG results retrieved successfully.', 'data': [{'characterId': 7, 'characterName': 'Grace', 'score': 0.48345035314559937}, {'characterId': 102, 'characterName': 'Diana', 'score': 0.4771277904510498}, {'characterId': 9, 'characterName': 'Ivy', 'score': 0.4691719114780426}]}

    # # 测试获取角色RAG
    # character_list = [2, 3, 4]  # 假设这是您要查询的角色ID列表
    # print(
    #     "Retrieving character RAG in list:",
    #     client.get_character_rag_in_list(
    #         characterId=1, characterList=character_list, topic="探索森林", k=2
    #     ),
    # )
    # # Retrieving character RAG in list: {'code': 1, 'message': 'Character RAG in list results retrieved successfully.', 'data': [{'characterId': 3, 'characterName': 'Charlie', 'score': 0.45353084802627563}, {'characterId': 4, 'characterName': 'David', 'score': 0.43324798345565796}]}

    # # 测试更新 character
    # character_update_data = {"slogan": "Silent but deadly."}
    # print("Updating character:", client.update_character(102, character_update_data))
    # # Updating character: {'code': 1, 'message': 'character updated successfully.', 'data': 1}
    # print("Retrieving Updated character:", client.get_character(102))
    # # Retrieving Updated character: {'code': 1, 'message': 'characters retrieved successfully.', 'data': [{'characterId': 102, 'characterName': 'Diana', 'gender': 'Female', 'slogan': 'Silent but deadly.', 'description': 'An agile ranger with unparalleled archery skills.', 'role': 'Ranger', 'task': 'Scout and protect the realm', 'created_at': '2024-10-30 20:24:16', 'full_profile': 'Diana; Female; Silent but deadly.; An agile ranger with unparalleled archery skills.; Ranger; Scout and protect the realm'}]}

    # # 测试存储和检索对话
    # conversation_data = {
    #     "characterIds": [2, 3],
    #     "dialogue": [
    #         {"Bob": "XXXX"},
    #         {"sdjf": "HJFHFDKSD"},
    #         {"Bob": "JFLKFJDL"},
    #     ],
    #     "start_day": 2,  # 更新字段
    #     "start_time": "9:00:00",  # 更新字段
    # }
    # print("Storing Conversation:", client.store_conversation(**conversation_data))
    # # Storing Conversation: {'code': 1, 'message': 'Conversation stored successfully.', 'data': '672225794a336f6004966cd2'}

    # print(
    #     "Retrieving Conversation by ID, Day, and Time:",
    #     client.get_conversation_by_id_day_time(
    #         characterIds_list=[2, 1], day=2, time="9:00:00"
    #     ),
    # )
    # # Retrieving Conversation by ID, Day, and Time: {'code': 1, 'message': 'Conversation retrieved successfully.', 'data': [{'characterIds': [2, 1], 'start_day': 2, 'start_time': '9:00:00', 'dialogue': [{'Bob': 'Hello Alice! Why do you look so tired?'}, {'Alice': "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."}, {'Bob': 'Although final exams are very important, you still need to have enough sleep.'}], 'created_at': '2024-11-07 19:02:50'}]}

    # print(
    #     "Retrieving Conversations by ID and Day:",
    #     client.get_conversations_by_id_and_day(characterId=2, day=2),
    # )
    # # Retrieving Conversations by ID and Day: {'code': 1, 'message': 'Conversations retrieved successfully.', 'data': [{'characterIds': [2, 3], 'start_day': 2, 'start_time': '9:00:00', 'dialogue': [{'Bob': 'XXXX'}, {'sdjf': 'HJFHFDKSD'}, {'Bob': 'JFLKFJDL'}], 'created_at': '2024-11-07 19:05:10'}, {'characterIds': [2, 1], 'start_day': 2, 'start_time': '9:00:00', 'dialogue': [{'Bob': 'Hello Alice! Why do you look so tired?'}, {'Alice': "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."}, {'Bob': 'Although final exams are very important, you still need to have enough sleep.'}], 'created_at': '2024-11-07 19:02:50'}]}

    # print(
    #     "Retrieving Conversation:",
    #     client.get_conversations_with_characterIds([2, 1], k=1),
    # )
    # # Retrieving Conversation: {'code': 1, 'message': 'Conversations retrieved successfully.', 'data': [{'characterIds': [2, 1], 'start_day': 2, 'start_time': '9:00:00', 'dialogue': [{'Bob': 'Hello Alice! Why do you look so tired?'}, {'Alice': "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."}, {'Bob': 'Although final exams are very important, you still need to have enough sleep.'}], 'created_at': '2024-11-07 19:02:50'}]}

    # print(
    #     "Retrieving Conversation:",
    #     client.get_conversations_containing_characterId(2, k=1),
    # )
    # # Retrieving Conversation: {'code': 1, 'message': 'Conversations retrieved successfully.', 'data': [{'characterIds': [2, 1], 'start_day': 2, 'start_time': '9:00:00', 'dialogue': [{'Bob': 'Hello Alice! Why do you look so tired?'}, {'Alice': "Hello Bob! I'm preparing for the final exams. I've been staying up late for days."}, {'Bob': 'Although final exams are very important, you still need to have enough sleep.'}], 'created_at': '2024-11-07 19:02:50'}]}

    # # 测试存储和检索印象
    # impression_data = {"from_id": 1, "to_id": 2, "impression": "lalalala"}
    # print("Storing Impression:", client.store_impression(**impression_data))
    # # Storing Impression: {'code': 1, 'message': 'Impression stored successfully.', 'data': '672225814a336f6004966cd3'}

    # print("Retrieving Impression:", client.get_impression(1, 2, k=1))
    # # Retrieving Impression: {'code': 1, 'message': 'Impressions retrieved successfully.', 'data': ['lalalala']}
    # # 测试存储和检索行动
    # action_data = {
    #     "characterId": 30021,
    #     "action": "nav",
    #     "result": {
    #         "characterId": 1,
    #         "messageCode": 3,
    #         "messageName": "actionresult",
    #         "data": {
    #             "actionName": "nav",
    #             "actionCode": 1,
    #             "result": True,
    #             "gameTime": "12:23:10",
    #             "msg": "Navigated to None navigated to None successfully.",
    #         },
    #     },
    #     "description": "I successfully navigated to the destination.",
    # }
    # print("Storing Action:", client.store_action(**action_data))
    # # Storing Action: {'code': 1, 'message': 'Action stored successfully.', 'data': '672225854a336f6004966cd4'}

    # print("Retrieving Action:", client.get_action(characterId=30021, action="nav", k=1))
    # # Retrieving Action: {'code': 1, 'message': 'Actions retrieved successfully.', 'data': [{'characterId': 30021, 'action': 'nav', 'result': {'characterId': 1, 'messageCode': 3, 'messageName': 'actionresult', 'data': {'actionName': 'nav', 'actionCode': 1, 'result': True, 'gameTime': '12:23:10', 'msg': 'Navigated to None navigated to None successfully.'}}, 'description': 'I successfully navigated to the destination.', 'created_at': '2024-10-30 20:24:37'}]}

    # # 测试存储和检索失败描述
    # descriptor_data = {
    #     "failed_action": "Find the hidden path",
    #     "action_id": 6,
    #     "characterId": 102,
    #     "reflection": "Should have looked at the map first.",
    # }
    # print("Storing Descriptor:", client.store_descriptor(**descriptor_data))
    # # Storing Descriptor: {'code': 1, 'message': 'Descriptor stored successfully.', 'data': '6722258a4a336f6004966cd5'}

    # print("Retrieving Descriptor:", client.get_descriptor(action_id=6, characterId=102))
    # # Retrieving Descriptor: {'code': 1, 'message': 'Descriptors retrieved successfully.', 'data': [{'failed_action': 'Find the hidden path', 'action_id': 6, 'characterId': 102, 'reflection': 'Should have looked at the map first.'}]}

    # # 测试存储和检索每日目标
    # daily_objective_data = {
    #     "characterId": 102,
    #     "objectives": ["Scout the northern woods", "Gather herbs", "Set up camp"],
    # }
    # print(
    #     "Storing Daily Objective:", client.store_daily_objective(**daily_objective_data)
    # )
    # # Storing Daily Objective: {'code': 1, 'message': 'Daily objectives stored successfully.', 'data': '6722258f4a336f6004966cd6'}

    # print(
    #     "Retrieving Daily Objectives:",
    #     client.get_daily_objectives(characterId=102, k=1),
    # )
    # # Retrieving Daily Objectives: {'code': 1, 'message': 'Daily objectives retrieved successfully.', 'data': [['Scout the northern woods', 'Gather herbs', 'Set up camp']]}

    # # 测试存储和检索计划
    # plan_data = {
    #     "characterId": 102,
    #     "detailed_plan": "1. Scout woods at dawn. 2. Return to camp by dusk.",
    # }
    # print("Storing Plan:", client.store_plan(**plan_data))
    # # Storing Plan: {'code': 1, 'message': 'Plan stored successfully.', 'data': '672225944a336f6004966cd7'}

    # print("Retrieving Plans:", client.get_plans(characterId=102, k=1))
    # # Retrieving Plans: {'code': 1, 'message': 'Plans retrieved successfully.', 'data': ['1. Scout woods at dawn. 2. Return to camp by dusk.']}

    # # 测试存储和检索元序列
    # meta_seq_data = {
    #     "characterId": 102,
    #     "meta_sequence": ["scout_area()", "gather_resources()", "set_up_camp()"],
    # }
    # print("Storing Meta Sequence:", client.store_meta_seq(**meta_seq_data))
    # # Storing Meta Sequence: {'code': 1, 'message': 'Meta sequence stored successfully.', 'data': '672225984a336f6004966cd8'}

    # print("Retrieving Meta Sequences:", client.get_meta_sequences(characterId=102, k=1))
    # # Retrieving Meta Sequences: {'code': 1, 'message': 'Meta sequences retrieved successfully.', 'data': [['scout_area()', 'gather_resources()', 'set_up_camp()']]}

    # # 更新元序列
    # update_meta_seq_data = {
    #     "characterId": 102,
    #     "meta_sequence": [
    #         "new_scout_area()",
    #         "new_gather_resources()",
    #         "new_set_up_camp()",
    #     ],
    # }
    # print("Updating Meta Sequence:", client.update_meta_seq(**update_meta_seq_data))
    # # Updating Meta Sequence: {'code': 1, 'message': 'Meta sequence updated successfully.', 'data': 1}

    # print(
    #     "Retrieving Updated Meta Sequences:",
    #     client.get_meta_sequences(characterId=102, k=1),
    # )
    # # Retrieving Updated Meta Sequences: {'code': 1, 'message': 'Meta sequences retrieved successfully.', 'data': [['new_scout_area()', 'new_gather_resources()', 'new_set_up_camp()']]}

    # # 测试存储和检索工具
    # tool_data = {"API": "find-path", "text": "Pathfinding tool", "code": "find_path()"}
    # print("Storing Tool:", client.store_tool(**tool_data))
    # # Storing Tool: {'code': 1, 'message': 'Tool stored successfully.', 'data': '672225a54a336f6004966cd9'}

    # print("Retrieving Tools:", client.get_tools(API="find-path"))
    # # Retrieving Tools: {'code': 1, 'message': 'Tools retrieved successfully.', 'data': [{'API': 'find-path', 'text': 'Pathfinding tool', 'code': 'find_path()'}]}

    # # 测试存储和检索日记
    # diary_data = {
    #     "characterId": 102,
    #     "diary_content": "Today, I explored the forest and found new paths.",
    # }
    # print("Storing Diary:", client.store_diary(**diary_data))
    # # Storing Diary: {'code': 1, 'message': 'Diary entry stored successfully.', 'data': '672225a94a336f6004966cda'}

    # print("Retrieving Diaries:", client.get_diaries(characterId=102, k=0))
    # # Retrieving Diaries: {'code': 1, 'message': 'Diaries retrieved successfully.', 'data': ['Today, I explored the forest and found new paths.']}

    # # 使用向量搜索
    # vector_search_data = {
    #     "query_text": "学习",
    #     "fields_to_return": ["characterId", "characterName"],
    #     "collection_name": "agent_profile",
    #     "k": 5,
    # }
    # print("Vector Search:", client.vector_search(**vector_search_data))
    # # Vector Search: {'code': 1, 'message': 'Vector search completed successfully.', 'data': [{'characterId': 1, 'characterName': 'Alice', 'score': 0.4139921963214874}]}

    # # 测试插入数据
    # document = {
    #     "characterId": 200,
    #     "characterName": "Test User",
    #     "gender": "Non-binary",
    #     "slogan": "Testing insert_data",
    #     "description": "This is a test character inserted via insert_data.",
    #     "role": "Tester",
    #     "task": "Testing API endpoints",
    # }
    # print("Inserting Data:", client.insert_data("character", document))
    # # Inserting Data: {'code': 1, 'message': 'Document inserted successfully.', 'data': '672225b84a336f6004966cdc'}

    # print("Finding Data:", client.find_data("character", {"characterId": 200}))
    # # Finding Data: {'code': 1, 'message': 'Documents retrieved successfully.', 'data': [{'characterId': 200, 'characterName': 'Test User', 'gender': 'Non-binary', 'slogan': 'Testing insert_data', 'description': 'This is a test character inserted via insert_data.', 'role': 'Tester', 'task': 'Testing API endpoints'}]}

    # # 测试更新数据
    # update_query = {"characterId": 200}
    # update_fields = {"$set": {"characterName": "Updated Test User"}}
    # print(
    #     "Updating Data:", client.update_data("character", update_query, update_fields)
    # )
    # # Updating Data: {'code': 1, 'message': 'Documents updated successfully.', 'data': 1}

    # print("Finding Updated Data:", client.find_data("character", {"characterId": 200}))
    # # Finding Updated Data: {'code': 1, 'message': 'Documents retrieved successfully.', 'data': [{'characterId': 200, 'characterName': 'Updated Test User', 'gender': 'Non-binary', 'slogan': 'Testing insert_data', 'description': 'This is a test character inserted via insert_data.', 'role': 'Tester', 'task': 'Testing API endpoints'}]}

    # # 测试删除数据
    # print("Deleting Data:", client.delete_data("character", {"characterId": 200}))
    # # Deleting Data: {'code': 1, 'message': 'Document deleted successfully.', 'data': 1}

    # print("Finding Deleted Data:", client.find_data("character", {"characterId": 200}))
    # # Finding Deleted Data: {'code': 0, 'message': 'No documents found.', 'data': None}

    # # 测试获取包含特定 character ID 的对话
    # print(
    #     "Retrieving Conversations Containing character ID 1:",
    #     client.get_conversations_containing_characterId(1),
    # )
    # # Retrieving Conversations Containing character ID 1: {'code': 1, 'message': 'Conversations retrieved successfully.', 'data': [{'characterIds': [1, 5], 'dialogue': 'Alice: Hi Eva! You always seem so healthy and energetic. What’s your secret? ...', 'created_at': '2024-10-30 20:24:23'}]}

    # # 测试获取候选项
    # print("Retrieving Candidates:", client.get_candidates())
    # # Retrieving Candidates: {'code': 0, 'message': 'No candidates found.', 'data': None}

    # # 测试存储和检索简历
    # cv_data = {
    #     "jobid": 5001,
    #     "characterId": 103,
    #     "characterName": "Test Candidate",
    #     "CV_content": "This is a test CV content.",
    # }
    # print("Storing CV:", client.store_cv(**cv_data))
    # # Storing CV: {'code': 1, 'message': 'CV stored successfully.', 'data': '672225cb4a336f6004966cdd'}

    # print("Retrieving CV:", client.get_cv(jobid=5001, characterId=103))
    # # Retrieving CV: {'code': 1, 'message': 'CVs retrieved successfully.', 'data': [{'jobid': 5001, 'characterId': 103, 'characterName': 'Test Candidate', 'CV_content': 'This is a test CV content.', 'created_at': '2024-10-30 20:25:47'}]}

    # # Testing storing and retrieving encounter count
    # encounter_data = {"from_id": 1, "to_id": 2, "count": 1}
    # print("Storing Encounter Count:", client.store_encounter_count(**encounter_data))
    # # Storing Encounter Count: {'code': 1, 'message': 'Encounter count stored successfully.', 'data': '672b2eb55a298eaf4d03e7c6'}

    # print("Retrieving Encounter Count:", client.get_encounter_count(1, 2))
    # # Retrieving Encounter Count: {'code': 1, 'message': 'Encounter count retrieved successfully.', 'data': [{'from_id': 1, 'to_id': 2, 'count': 1, 'created_at': '2024-11-06 16:54:13', 'updated_at': '2024-11-06 16:54:13'}]}

    # # Incrementing encounter count
    # print("Incrementing Encounter Count:", client.increment_encounter_count(2, 2))
    # # Incrementing Encounter Count: {'code': 1, 'message': 'Encounter count incremented successfully.', 'data': 1}

    # # Updating encounter count to a specific value
    # print("Updating Encounter Count:", client.update_encounter_count(1, 2, 5))
    # # Updating Encounter Count: {'code': 1, 'message': 'Encounter count updated successfully.', 'data': 1}

    # print(
    #     "Retrieving Encounters by From ID:",
    #     client.get_encounters_by_from_id(1, k=3),
    # )
    # # Retrieving Encounters by From ID: {'code': 1, 'message': 'Encounters retrieved successfully.', 'data': [{'from_id': 1, 'to_id': 5, 'count': 1, 'created_at': '2024-11-06 16:56:16', 'updated_at': '2024-11-06 16:56:16'}, {'from_id': 1, 'to_id': 2, 'count': 5, 'created_at': '2024-11-06 16:54:13', 'updated_at': '2024-11-06 16:56:27'}]}

    # # 测试存储和检索好感度
    # intimacy_data = {"from_id": 1, "to_id": 3, "intimacy_level": 55}
    # print("Storing Intimacy:", client.store_intimacy(**intimacy_data))
    # # Storing Intimacy: {'code': 1, 'message': 'Intimacy level stored successfully.', 'data': 1}

    # print("Retrieving Intimacy:", client.get_intimacy(1, 3))
    # # Retrieving Intimacy: {'code': 1, 'message': 'Intimacy level retrieved successfully.', 'data': [{'from_id': 1, 'to_id': 3, 'intimacy_level': 55, 'created_at': '2024-11-01 02:57:19', 'updated_at': '2024-11-01 03:09:37'}]}

    # update_intimacy_data = {"from_id": 1, "to_id": 3, "new_intimacy_level": 77}
    # print("Updating Intimacy:", client.update_intimacy(**update_intimacy_data))
    # # Updating Intimacy: {'code': 1, 'message': 'Intimacy level updated successfully.', 'data': 1}

    # # 测试将所有好感度等级下降 1
    # print("Decreasing All Intimacy Levels:", client.decrease_all_intimacy_levels())
    # # Decreasing All Intimacy Levels: {'code': 1, 'message': 'All intimacy levels decreased by 1 successfully.', 'data': 'Number of updated documents'}

    # # 再次检索，验证好感度下降
    # print("Retrieving Intimacy after Decrease:", client.get_intimacy(1, 3))
    # # Retrieving Intimacy after Decrease: {'code': 1, 'message': 'Intimacy level retrieved successfully.', 'data': [{'from_id': 1, 'to_id': 3, 'intimacy_level': 76, 'created_at': '2024-11-01 02:57:19', 'updated_at': '2024-11-01 03:09:37'}]}

    # # 测试存储知识
    # knowledge_data = {
    #     "characterId": 101,
    #     "day": 1,
    #     "environment_information": "Sunny day in the forest.",
    #     "personal_information": "Learned new archery skills.",
    # }
    # print("Storing Knowledge:", client.store_knowledge(**knowledge_data))
    # # 预期输出: {'code': 1, 'message': 'Knowledge stored successfully.', 'data': 'some_id'}

    # # 测试获取知识
    # print("Retrieving Knowledge:", client.get_knowledge(characterId=101, day=1))
    # # 预期输出: {'code': 1, 'message': 'Knowledge retrieved successfully.', 'data': [{'characterId': 101, 'day': 1, 'environment_information': 'Sunny day in the forest.', 'personal_information': 'Learned new archery skills.', 'created_at': 'some_date'}]}

    # # 测试获取最新知识
    # print(
    #     "Retrieving Latest Knowledge:",
    #     client.get_latest_knowledge(characterId=101, k=1),
    # )
    # # 预期输出: {'code': 1, 'message': 'Latest knowledge retrieved successfully.', 'data': [{'characterId': 101, 'day': 1, 'environment_information': 'Sunny day in the forest.', 'personal_information': 'Learned new archery skills.', 'created_at': 'some_date'}]}

    # # 测试更新知识
    # updated_knowledge_data = {
    #     "characterId": 101,
    #     "day": 1,
    #     "environment_information": "Cloudy day in the forest.",
    #     "personal_information": "Practiced archery with new techniques.",
    # }
    # print("Updating Knowledge:", client.update_knowledge(**updated_knowledge_data))
    # # Updating Knowledge: {'code': 1, 'message': 'Knowledge updated successfully.', 'data': 1}

    # # 再次检索以验证更新
    # print("Retrieving Updated Knowledge:", client.get_knowledge(characterId=101, day=1))
    # # Retrieving Updated Knowledge: {'code': 1, 'message': 'Knowledge retrieved successfully.', 'data': [{'characterId': 101, 'day': 1, 'environment_information': 'Cloudy day in the forest.', 'personal_information': 'Practiced archery with new techniques.', 'created_at': '2024-11-07 17:19:11'}]}

    # 测试存储角色弧光
    character_id = 2
    category_data = [
        {"item": "skill", "origin_value": "beginner"},
        {"item": "emotion", "origin_value": "neutral"},
    ]
    print(
        "Storing Character Arc:",
        client.store_character_arc(character_id, category_data),
    )
    # Storing Character Arc: {'code': 1, 'message': 'Character arc stored successfully.', 'data': '672d2c5357974f093a92fd06'}

    # 测试存储角色弧光变化
    print(
        "Storing Character Arc Change 1:",
        client.store_character_arc_change(
            characterId=character_id,
            item="skill",
            cause="参加职业培训",
            context="在朋友的建议下参加了当地的职业技能培训班",
            change="获得新技能",
        ),
    )
    # Storing Character Arc Change 1: {'code': 1, 'message': 'Character arc change stored successfully.', 'data': '672d2c5757974f093a92fd07'}

    print(
        "Storing Character Arc Change 2:",
        client.store_character_arc_change(
            characterId=character_id,
            item="skill",
            cause="完成高级课程",
            context="通过在线学习平台完成了高级课程",
            change="技能提升",
        ),
    )

    print(
        "Storing Character Arc Change 3:",
        client.store_character_arc_change(
            characterId=character_id,
            item="emotion",
            cause="收到好消息",
            context="得知自己通过了考试",
            change="略微积极",
        ),
    )

    # 测试获取角色弧光
    print("Retrieving Character Arc:", client.get_character_arc(character_id))
    # Retrieving Character Arc: {'code': 1, 'message': 'Character arc retrieved successfully.', 'data': [{'characterId': 2, 'category': [{'item': 'skill', 'origin_value': 'beginner'}, {'item': 'emotion', 'origin_value': 'neutral'}], 'created_at': '2024-11-08 05:08:35'}]}

    # 测试获取角色弧光及其变化过程
    k = 2  # 选择变化过程的数量
    print(
        "Retrieving Character Arc with Changes:",
        client.get_character_arc_with_changes(character_id, k),
    )
    # Retrieving Character Arc with Changes: {'code': 1, 'message': 'Character arc with changes retrieved successfully.', 'data': {'characterId': 2, 'category': [{'item': 'skill', 'origin_value': 'beginner', 'change_process': [{'cause': '参加职业培训', 'context': '在朋友的建议下参加了当地的职业技能培训班', 'change': '获得新技能', 'created_at': '2024-11-08 05:08:39'}, {'cause': '完成高级课程', 'context': '通过在线学习平台完成了高级课程', 'change': '技能提升', 'created_at': '2024-11-08 05:08:41'}]}, {'item': 'emotion', 'origin_value': 'neutral', 'change_process': [{'cause': '收到好消息', 'context': '得知自己通过了考试', 'change': '略微积极', 'created_at': '2024-11-08 05:08:43'}]}]}}

    # 测试更新角色弧光
    updated_category_data = [
        {"item": "skill", "origin_value": "intermediate"},
        {"item": "emotion", "origin_value": "happy"},
    ]
    print(
        "Updating Character Arc:",
        client.update_character_arc(character_id, updated_category_data),
    )
    # Updating Character Arc: {'code': 1, 'message': 'Character arc updated successfully.', 'data': 1}
