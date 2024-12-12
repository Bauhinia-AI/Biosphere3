# app/client.py
import sys
import os
import logging
import requests
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import config  # 如果需要使用 config

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

    def _make_request(self, method, url, json_data=None, params=None):
        """
        新增对GET、PUT、DELETE等请求的支持:
        - GET请求使用params传递查询参数
        - PUT、PATCH、DELETE请求支持通过json_data传递请求体
        """
        for attempt in range(1, self.retries + 1):
            try:
                logging.debug(
                    f"Making {method} request to {url} with data: {json_data} params: {params}"
                )
                if method == "POST":
                    response = requests.post(url, json=json_data, timeout=20)
                elif method == "GET":
                    response = requests.get(url, params=params, timeout=20)
                elif method == "PUT":
                    response = requests.put(url, json=json_data, timeout=20)
                elif method == "PATCH":
                    response = requests.patch(url, json=json_data, timeout=20)
                elif method == "DELETE":
                    response = requests.delete(url, json=json_data, timeout=20)
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

    # CRUD操作
    def insert_data(self, collection_name, document):
        return self._make_request(
            "POST",
            f"{self.base_url}/crud/insert",
            {"collection_name": collection_name, "document": document},
        )

    def update_data(self, collection_name, query, update, upsert=False, multi=False):
        return self._make_request(
            "PUT",
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
            "DELETE",
            f"{self.base_url}/crud/delete",
            {"collection_name": collection_name, "query": query, "multi": multi},
        )

    def find_data(self, collection_name, query={}, projection=None, limit=0, sort=None):
        # 需要将 query, projection, sort 转为字符串或符合URL的形式
        # 以下是示例，请根据实际实现进行序列化
        params = {
            "collection_name": collection_name,
            # 您需要根据实际情况将query,projection,sort序列化为字符串或其他可在URL上传递的形式
            # 这里假设仅传collection_name进行测试，如需传query则需要json.dumps(query)
            # "query": json.dumps(query),
            # "projection": json.dumps(projection) if projection else None,
            # "limit": limit,
            # "sort": json.dumps(sort) if sort else None
        }
        return self._make_request("GET", f"{self.base_url}/crud/find", params=params)

    # Vector Search
    def vector_search(self, query_text, fields_to_return, collection_name, k=1):
        # fields_to_return 应转为字符串，如 'field1,field2'
        fields_str = ",".join(fields_to_return)
        params = {
            "collection_name": collection_name,
            "query_text": query_text,
            "fields_to_return": fields_str,
            "k": k,
        }
        return self._make_request(
            "GET",
            f"{self.base_url}/vector_search",
            params=params,
        )

    # Impressions
    def store_impression(self, from_id, to_id, impression):
        return self._make_request(
            "POST",
            f"{self.base_url}/impressions",
            {"from_id": from_id, "to_id": to_id, "impression": impression},
        )

    def get_impression(self, from_id, to_id, k=1):
        params = {"from_id": from_id, "to_id": to_id, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/impressions",
            params=params,
        )

    # Conversations
    def store_conversation(self, characterIds, dialogue, start_day, start_time):
        return self._make_request(
            "POST",
            f"{self.base_url}/conversations",
            {
                "characterIds": characterIds,
                "dialogue": dialogue,
                "start_day": start_day,
                "start_time": start_time,
            },
        )

    def get_conversation_by_id_day_time(self, characterIds_list, day, time):
        # characterIds_list 用逗号分隔
        ids_str = ",".join(str(i) for i in characterIds_list)
        params = {"characterIds_list": ids_str, "day": day, "time": time}
        return self._make_request(
            "GET",
            f"{self.base_url}/conversations/by_id_day_time",
            params=params,
        )

    def get_conversations_by_id_and_day(self, characterId, day):
        params = {"characterId": characterId, "day": day}
        return self._make_request(
            "GET",
            f"{self.base_url}/conversations/by_id_and_day",
            params=params,
        )

    def get_conversations_with_characterIds(self, characterIds_list, k=1):
        ids_str = ",".join(str(i) for i in characterIds_list)
        params = {"characterIds_list": ids_str, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/conversations/with_character_ids",
            params=params,
        )

    def get_conversations_containing_characterId(self, characterId, k=0):
        params = {"characterId": characterId, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/conversations/containing_character_id",
            params=params,
        )

    # CVs
    def store_cv(
        self,
        jobid,
        characterId,
        CV_content,
        week,
        health,
        studyxp,
        date,
        jobName,  # 新增字段
        election_status="not_yet",  # 更新字段名
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/cv",
            {
                "jobid": jobid,
                "characterId": characterId,
                "CV_content": CV_content,
                "week": week,
                "health": health,  # 新增字段
                "studyxp": studyxp,  # 新增字段
                "date": date,  # 新增字段
                "jobName": jobName,  # 新增字段
                "election_status": election_status,  # 更新字段名
            },
        )

    def update_election_status(
        self, characterId, election_status, jobid=None, week=None
    ):
        return self._make_request(
            "PUT",
            f"{self.base_url}/cv/election_status",
            {
                "characterId": characterId,
                "election_status": election_status,
                "jobid": jobid,
                "week": week,
            },
        )

    def get_cv(self, jobid=None, characterId=None, week=None, election_status=None):
        params = {}
        if jobid is not None:
            params["jobid"] = jobid
        if characterId is not None:
            params["characterId"] = characterId
        if week is not None:
            params["week"] = week
        if election_status is not None:
            params["election_status"] = election_status
        return self._make_request(
            "GET",
            f"{self.base_url}/cv",
            params=params,
        )

    # Actions
    def store_action(self, characterId, action, result, description):
        return self._make_request(
            "POST",
            f"{self.base_url}/actions",
            {
                "characterId": characterId,
                "action": action,
                "result": result,
                "description": description,
            },
        )

    def get_action(self, characterId, action, k=1):
        params = {"characterId": characterId, "action": action, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/actions",
            params=params,
        )

    # Descriptors
    def store_descriptor(self, failed_action, action_id, characterId, reflection):
        return self._make_request(
            "POST",
            f"{self.base_url}/descriptors",
            {
                "failed_action": failed_action,
                "action_id": action_id,
                "characterId": characterId,
                "reflection": reflection,
            },
        )

    def get_descriptor(self, action_id, characterId, k=1):
        params = {"action_id": action_id, "characterId": characterId, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/descriptors",
            params=params,
        )

    # Daily Objectives
    def store_daily_objective(self, characterId, objectives):
        return self._make_request(
            "POST",
            f"{self.base_url}/daily_objectives",
            {"characterId": characterId, "objectives": objectives},
        )

    def get_daily_objectives(self, characterId, k=1):
        params = {"characterId": characterId, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/daily_objectives",
            params=params,
        )

    # Plans
    def store_plan(self, characterId, detailed_plan):
        return self._make_request(
            "POST",
            f"{self.base_url}/plans",
            {"characterId": characterId, "detailed_plan": detailed_plan},
        )

    def get_plans(self, characterId, k=1):
        params = {"characterId": characterId, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/plans",
            params=params,
        )

    # Meta Sequences
    def store_meta_seq(self, characterId, meta_sequence):
        return self._make_request(
            "POST",
            f"{self.base_url}/meta_sequences",
            {"characterId": characterId, "meta_sequence": meta_sequence},
        )

    def get_meta_sequences(self, characterId, k=1):
        params = {"characterId": characterId, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/meta_sequences",
            params=params,
        )

    def update_meta_seq(self, characterId, meta_sequence):
        return self._make_request(
            "PUT",
            f"{self.base_url}/meta_sequences",
            {"characterId": characterId, "meta_sequence": meta_sequence},
        )

    # Diaries
    def store_diary(self, characterId, diary_content):
        return self._make_request(
            "POST",
            f"{self.base_url}/diaries",
            {"characterId": characterId, "diary_content": diary_content},
        )

    def get_diaries(self, characterId, k=1):
        params = {"characterId": characterId, "k": k}
        return self._make_request("GET", f"{self.base_url}/diaries", params=params)

    # Characters
    def store_character(
        self,
        characterId,
        characterName=None,
        gender=None,
        spriteId=0,
        relationship=None,
        personality=None,
        long_term_goal=None,
        short_term_goal=None,
        language_style=None,
        biography=None,
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/characters",
            {
                "characterId": characterId,
                "characterName": characterName,
                "gender": gender,
                "spriteId": spriteId,
                "relationship": relationship,
                "personality": personality,
                "long_term_goal": long_term_goal,
                "short_term_goal": short_term_goal,
                "language_style": language_style,
                "biography": biography,
            },
        )

    def get_character(self, characterId=None):
        params = {}
        if characterId is not None:
            params["characterId"] = characterId
        return self._make_request("GET", f"{self.base_url}/characters", params=params)

    def get_character_rag(self, characterId, topic, k):
        params = {"characterId": characterId, "topic": topic, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/characters/rag",
            params=params,
        )

    def get_character_rag_in_list(self, characterId, characterList, topic, k):
        params = {
            "characterId": characterId,
            "topic": topic,
            "k": k,
            "characterList": characterList,
        }
        return self._make_request(
            "GET",
            f"{self.base_url}/characters/rag_in_list",
            params=params,
        )

    def update_character(self, characterId, update_fields):
        return self._make_request(
            "PUT",
            f"{self.base_url}/characters",
            {"characterId": characterId, "update_fields": update_fields},
        )

    # Encounter Count
    def get_encounter_count(self, from_id, to_id):
        params = {"from_id": from_id, "to_id": to_id}
        return self._make_request(
            "GET",
            f"{self.base_url}/encounter_count",
            params=params,
        )

    def get_encounters_by_from_id(self, from_id, k=1):
        params = {"from_id": from_id, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/encounter_count/by_from_id",
            params=params,
        )

    def store_encounter_count(self, from_id, to_id, count=1):
        return self._make_request(
            "POST",
            f"{self.base_url}/encounter_count",
            {"from_id": from_id, "to_id": to_id, "count": count},
        )

    def increment_encounter_count(self, from_id, to_id):
        params = {"from_id": from_id, "to_id": to_id}
        return self._make_request(
            "PUT",
            f"{self.base_url}/encounter_count/increment",
            params=params,
        )

    def update_encounter_count(self, from_id, to_id, count):
        return self._make_request(
            "PUT",
            f"{self.base_url}/encounter_count",
            {"from_id": from_id, "to_id": to_id, "count": count},
        )

    # Intimacy
    def get_intimacy(
        self,
        from_id=None,
        to_id=None,
        intimacy_level_min=None,
        intimacy_level_max=None,
        have_conversation=False,
    ):
        params = {}
        if from_id is not None:
            params["from_id"] = from_id
        if to_id is not None:
            params["to_id"] = to_id
        if intimacy_level_min is not None:
            params["intimacy_level_min"] = intimacy_level_min
        if intimacy_level_max is not None:
            params["intimacy_level_max"] = intimacy_level_max
        if have_conversation:
            params["have_conversation"] = "true"

        return self._make_request(
            "GET",
            f"{self.base_url}/intimacy",
            params=params,
        )

    def store_intimacy(self, from_id, to_id, intimacy_level):
        return self._make_request(
            "POST",
            f"{self.base_url}/intimacy",
            {"from_id": from_id, "to_id": to_id, "intimacy_level": intimacy_level},
        )

    def update_intimacy(self, from_id, to_id, new_intimacy_level):
        return self._make_request(
            "PUT",
            f"{self.base_url}/intimacy",
            {
                "from_id": from_id,
                "to_id": to_id,
                "new_intimacy_level": new_intimacy_level,
            },
        )

    def decrease_all_intimacy_levels(self):
        return self._make_request("PATCH", f"{self.base_url}/intimacy/decrease_all")

    # Knowledge
    def store_knowledge(
        self, characterId, day, environment_information, personal_information
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/knowledge",
            {
                "characterId": characterId,
                "day": day,
                "environment_information": environment_information,
                "personal_information": personal_information,
            },
        )

    def get_knowledge(self, characterId, day):
        params = {"characterId": characterId, "day": day}
        return self._make_request(
            "GET",
            f"{self.base_url}/knowledge",
            params=params,
        )

    def get_latest_knowledge(self, characterId, k=1):
        params = {"characterId": characterId, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/knowledge/latest",
            params=params,
        )

    def update_knowledge(
        self, characterId, day, environment_information=None, personal_information=None
    ):
        data = {
            "characterId": characterId,
            "day": day,
        }
        if environment_information is not None:
            data["environment_information"] = environment_information
        if personal_information is not None:
            data["personal_information"] = personal_information

        return self._make_request(
            "PUT",
            f"{self.base_url}/knowledge",
            data,
        )

    # Character Arc
    def store_character_arc(self, characterId, category):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc",
            {"characterId": characterId, "category": category},
        )

    def get_character_arc(self, characterId):
        params = {"characterId": characterId}
        return self._make_request(
            "GET",
            f"{self.base_url}/character_arc",
            params=params,
        )

    def get_character_arc_with_changes(self, characterId, k=1):
        params = {"characterId": characterId, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/character_arc/with_changes",
            params=params,
        )

    def update_character_arc(self, characterId, category):
        return self._make_request(
            "PUT",
            f"{self.base_url}/character_arc",
            {"characterId": characterId, "category": category},
        )

    def store_character_arc_change(self, characterId, item, cause, context, change):
        return self._make_request(
            "POST",
            f"{self.base_url}/character_arc/change",
            {
                "characterId": characterId,
                "item": item,
                "cause": cause,
                "context": context,
                "change": change,
            },
        )

    def get_character_arc_changes(self, characterId, item, k=1):
        params = {"characterId": characterId, "item": item, "k": k}
        return self._make_request(
            "GET",
            f"{self.base_url}/character_arc/changes",
            params=params,
        )

    # Sample
    def get_sample(self, item_name=None):
        params = {}
        if item_name is not None:
            params["item_name"] = item_name
        return self._make_request(
            "GET",
            f"{self.base_url}/sample",
            params=params,
        )

    # Agent Prompt
    def store_agent_prompt(
        self,
        characterId,
        daily_goal=None,
        refer_to_previous=None,
        life_style=None,
        daily_objective_ar=None,
        task_priority=None,
        max_actions=None,
        meta_seq_ar=None,
        replan_time_limit=None,
        meta_seq_adjuster_ar=None,
        focus_topic=None,
        depth_of_reflection=None,
        reflection_ar=None,
        level_of_detail=None,
        tone_and_style=None,
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/agent_prompt",
            {
                "characterId": characterId,
                "daily_goal": daily_goal,
                "refer_to_previous": refer_to_previous,
                "life_style": life_style,
                "daily_objective_ar": daily_objective_ar,
                "task_priority": task_priority,
                "max_actions": max_actions,
                "meta_seq_ar": meta_seq_ar,
                "replan_time_limit": replan_time_limit,
                "meta_seq_adjuster_ar": meta_seq_adjuster_ar,
                "focus_topic": focus_topic,
                "depth_of_reflection": depth_of_reflection,
                "reflection_ar": reflection_ar,
                "level_of_detail": level_of_detail,
                "tone_and_style": tone_and_style,
            },
        )

    def get_agent_prompt(self, characterId):
        params = {"characterId": characterId}
        return self._make_request(
            "GET",
            f"{self.base_url}/agent_prompt",
            params=params,
        )

    def update_agent_prompt(self, characterId, update_fields):
        return self._make_request(
            "PUT",
            f"{self.base_url}/agent_prompt",
            {"characterId": characterId, "update_fields": update_fields},
        )

    def delete_agent_prompt(self, characterId):
        params = {"characterId": characterId}
        return self._make_request(
            "DELETE",
            f"{self.base_url}/agent_prompt",
            params=params,
        )

    # Conversation Prompt
    def store_conversation_prompt(
        self,
        characterId,
        topic_requirements=None,
        relation=None,
        emotion=None,
        personality=None,
        habits_and_preferences=None,
    ):
        return self._make_request(
            "POST",
            f"{self.base_url}/conversation_prompt",
            {
                "characterId": characterId,
                "topic_requirements": topic_requirements,
                "relation": relation,
                "emotion": emotion,
                "personality": personality,
                "habits_and_preferences": habits_and_preferences,
            },
        )

    def get_conversation_prompt(self, characterId):
        params = {"characterId": characterId}
        return self._make_request(
            "GET",
            f"{self.base_url}/conversation_prompt",
            params=params,
        )

    def update_conversation_prompt(self, characterId, update_fields):
        return self._make_request(
            "PUT",
            f"{self.base_url}/conversation_prompt",
            {"characterId": characterId, "update_fields": update_fields},
        )

    def delete_conversation_prompt(self, characterId):
        params = {"characterId": characterId}
        return self._make_request(
            "DELETE",
            f"{self.base_url}/conversation_prompt",
            params=params,
        )


if __name__ == "__main__":
    client = APIClient(base_url="http://localhost:8085")
    # 在此进行测试
