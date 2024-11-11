# database/domain_specific_queries.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pymongo import DESCENDING
from database import config
from database.utils import embed_text  # Remove connect_to_mongo import
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError
from database.mongo_utils import MongoDBUtils
import random


class DomainSpecificQueries:
    def __init__(self, db_utils):
        self.db_utils = db_utils

    def vector_search(
        self, collection_name, query_text, fields_to_return, k, filter_list=None
    ):
        # Generate query embedding
        query_embedding = embed_text(
            query_text, config.model_name, config.base_url, config.api_key
        )
        # Use existing db connection
        collection = self.db_utils.db[collection_name]

        # Prepare projection based on fields to return
        projection = {field: 1 for field in fields_to_return}
        projection["_id"] = 0  # Do not return the _id field
        projection["score"] = {"$meta": "vectorSearchScore"}  # Include similarity score

        # Build the aggregation pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": config.index_name,
                    "queryVector": query_embedding,
                    "path": "text_embedding",
                    "numCandidates": config.numCandidates,  # You can adjust this as needed
                    "limit": k,
                    "exact": False,  # Approximate nearest neighbor search
                }
            }
        ]

        # Add match stage after $vectorSearch to filter by characterId
        if filter_list is not None:
            pipeline.append({"$match": {"characterId": {"$in": filter_list}}})

        # Add project stage
        pipeline.append({"$project": projection})

        # Execute search
        results = collection.aggregate(pipeline)
        return list(results)

    def get_latest_k_documents(self, collection_name, characterId, k, item):
        documents = self.db_utils.find_documents(
            collection_name=collection_name,
            query={"characterId": characterId},
            projection={item: 1, "_id": 0},
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        # Return in JSON format
        return [doc[item] for doc in documents]

    def get_candidates_from_mongo(self):
        one_week_ago = datetime.now() - timedelta(days=7)
        candidates = self.db_utils.find_documents(
            collection_name=config.cv_collection_name,
            query={"created_at": {"$gte": one_week_ago.strftime("%Y-%m-%d %H:%M:%S")}},
            projection={"_id": 0, "jobid": 1, "characterName": 1, "characterId": 1},
        )
        return candidates

    def get_conversations_with_characterIds(self, characterIds_list, k):
        query = {"characterIds": {"$all": characterIds_list}}
        documents = self.db_utils.find_documents(
            collection_name=config.conversation_collection_name,
            query=query,
            limit=k,
        )
        return documents

    def get_conversations_containing_characterId(self, characterId, k):
        query = {"characterIds": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.conversation_collection_name,
            query=query,
            limit=k,
        )
        return documents

    def get_conversation_by_id_day_time(self, characterIds_list, day, time):
        query = {
            "characterIds": {"$all": characterIds_list},
            "start_day": day,
            "start_time": time,
        }
        documents = self.db_utils.find_documents(
            collection_name=config.conversation_collection_name,
            query=query,
        )
        return documents

    def get_conversations_by_id_and_day(self, characterId, day):
        query = {"characterIds": characterId, "start_day": day}
        documents = self.db_utils.find_documents(
            collection_name=config.conversation_collection_name,
            query=query,
        )
        return documents

    def store_conversation(self, characterIds, dialogue, start_day, start_time):
        document = {
            "characterIds": characterIds,
            "start_day": start_day,  # 新增字段
            "start_time": start_time,  # 新增字段
            "dialogue": dialogue,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.conversation_collection_name, document
        )
        return inserted_id

    def store_impression(self, from_id, to_id, impression):
        document = {
            "from_id": from_id,
            "to_id": to_id,
            "impression": impression,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.impression_collection_name, document
        )
        return inserted_id

    def get_impression_from_mongo(self, from_id, to_id, k):
        documents = self.db_utils.find_documents(
            collection_name=config.impression_collection_name,
            query={"from_id": from_id, "to_id": to_id},
            projection={"impression": 1, "_id": 0},
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        return [doc["impression"] for doc in documents]

    def store_intimacy(self, from_id, to_id, intimacy_level):
        document = {
            "from_id": from_id,
            "to_id": to_id,
            "intimacy_level": intimacy_level,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.intimacy_collection_name, document
        )
        return inserted_id

    def get_intimacy(self, from_id, to_id):
        query = {"from_id": from_id, "to_id": to_id}
        document = self.db_utils.find_documents(
            collection_name=config.intimacy_collection_name, query=query
        )
        return document

    def update_intimacy(self, from_id, to_id, new_intimacy_level):
        query = {"from_id": from_id, "to_id": to_id}
        update = {
            "$set": {
                "intimacy_level": new_intimacy_level,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        result = self.db_utils.update_documents(
            collection_name=config.intimacy_collection_name, query=query, update=update
        )
        return result

    def decrease_all_intimacy_levels(self):
        query = {"intimacy_level": {"$gt": 50}}  # 仅更新 intamacy_level > 0 的文档
        update = {
            "$inc": {"intimacy_level": -1},  # 将 intimacy_level 递减 1
            "$set": {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        }
        result = self.db_utils.update_documents(
            collection_name=config.intimacy_collection_name,
            query=query,
            update=update,
            multi=True,
        )
        return result

    def get_encounter_count(self, from_id, to_id):
        query = {"from_id": from_id, "to_id": to_id}
        document = self.db_utils.find_documents(
            collection_name=config.encounter_count_collection_name, query=query
        )
        return document

    def store_encounter_count(self, from_id, to_id, count):
        document = {
            "from_id": from_id,
            "to_id": to_id,
            "count": count,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.encounter_count_collection_name, document
        )
        return inserted_id

    def update_encounter_count(self, from_id, to_id, new_count):
        query = {"from_id": from_id, "to_id": to_id}
        update = {
            "$set": {
                "count": new_count,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        result = self.db_utils.update_documents(
            collection_name=config.encounter_count_collection_name,
            query=query,
            update=update,
        )
        return result

    def get_encounters_by_from_id(self, from_id, k):
        query = {"from_id": from_id}
        documents = self.db_utils.find_documents(
            collection_name=config.encounter_count_collection_name,
            query=query,
            limit=k,
        )
        return documents

    def store_cv(self, jobid, characterId, characterName, CV_content):
        document = {
            "jobid": jobid,
            "characterId": characterId,
            "characterName": characterName,
            "CV_content": CV_content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(config.cv_collection_name, document)
        return inserted_id

    def get_cv(self, jobid, characterId, k):
        query = {"jobid": jobid, "characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.cv_collection_name,
            query=query,
            limit=k,
        )
        return documents

    def store_action(self, characterId, action, result, description):
        document = {
            "characterId": characterId,
            "action": action,
            "result": result,
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.action_collection_name, document
        )
        return inserted_id

    def get_action(self, characterId, action, k):
        query = {"characterId": characterId, "action": action}
        documents = self.db_utils.find_documents(
            collection_name=config.action_collection_name,
            query=query,
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        return documents

    def store_descriptor(self, failed_action, action_id, characterId, reflection):
        document = {
            "failed_action": failed_action,
            "action_id": action_id,
            "characterId": characterId,
            "reflection": reflection,
        }
        inserted_id = self.db_utils.insert_document(
            config.descriptor_collection_name, document
        )
        return inserted_id

    def get_descriptor(self, action_id, characterId, k):
        query = {"action_id": action_id, "characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.descriptor_collection_name,
            query=query,
            limit=k,
        )
        return documents

    def store_daily_objective(self, characterId, objectives):
        document = {
            "characterId": characterId,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "objectives": objectives,
        }
        inserted_id = self.db_utils.insert_document(
            config.daily_objective_collection_name, document
        )
        return inserted_id

    def get_daily_objectives(self, characterId, k):
        documents = self.db_utils.find_documents(
            collection_name=config.daily_objective_collection_name,
            query={"characterId": characterId},
            projection={"objectives": 1, "_id": 0},
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        return [doc["objectives"] for doc in documents]

    def store_plan(self, characterId, detailed_plan):
        document = {
            "characterId": characterId,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "detailed_plan": detailed_plan,
        }
        inserted_id = self.db_utils.insert_document(
            config.plan_collection_name, document
        )
        return inserted_id

    def get_plans(self, characterId, k):
        documents = self.db_utils.find_documents(
            collection_name=config.plan_collection_name,
            query={"characterId": characterId},
            projection={"detailed_plan": 1, "_id": 0},
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        return [doc["detailed_plan"] for doc in documents]

    def store_meta_seq(self, characterId, meta_sequence):
        document = {
            "characterId": characterId,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "meta_sequence": meta_sequence,
        }
        inserted_id = self.db_utils.insert_document(
            config.meta_seq_collection_name, document
        )
        return inserted_id

    def get_meta_sequences(self, characterId, k):
        documents = self.db_utils.find_documents(
            collection_name=config.meta_seq_collection_name,
            query={"characterId": characterId},
            projection={"meta_sequence": 1, "_id": 0},
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        return [doc["meta_sequence"] for doc in documents]

    def update_meta_seq(self, characterId, meta_sequence):
        # Find the latest meta_sequence document for the given characterId
        documents = self.db_utils.find_documents(
            collection_name=config.meta_seq_collection_name,
            query={"characterId": characterId},
            projection={"_id": 1},
            limit=1,
            sort=[("created_at", DESCENDING)],
            include_id=True,
        )

        if documents:
            # There is at least one document, get its _id
            document_id = documents[0]["_id"]

            # Prepare the update data structure
            update_data = {
                "$set": {
                    "meta_sequence": meta_sequence,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            }

            # Update the document's fields based on update_meta_seq
            modified_count = self.db_utils.update_documents(
                collection_name=config.meta_seq_collection_name,
                query={"_id": document_id},
                update=update_data,
                upsert=False,
                multi=False,
            )

            return modified_count
        else:
            # No documents found for the characterId
            return 0  # or raise an exception

    def store_knowledge(
        self, characterId, day, environment_information, personal_information
    ):
        document = {
            "characterId": characterId,
            "day": day,
            "environment_information": environment_information,
            "personal_information": personal_information,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.knowledge_collection_name, document
        )
        return inserted_id

    def get_knowledge(self, characterId, day):
        query = {"characterId": characterId, "day": day}
        documents = self.db_utils.find_documents(
            collection_name=config.knowledge_collection_name,
            query=query,
            projection={"_id": 0},  # 不返回 _id 字段
        )
        return documents

    def get_latest_knowledge(self, characterId, k):
        documents = self.db_utils.find_documents(
            collection_name=config.knowledge_collection_name,
            query={"characterId": characterId},
            projection={"_id": 0},  # 不返回 _id 字段
            limit=k,
            sort=[("created_at", DESCENDING)],  # 按创建时间降序排列
        )
        return documents

    def update_knowledge(
        self, characterId, day, environment_information=None, personal_information=None
    ):
        query = {"characterId": characterId, "day": day}
        update_data = {"$set": {}}

        if environment_information is not None:
            update_data["$set"]["environment_information"] = environment_information

        if personal_information is not None:
            update_data["$set"]["personal_information"] = personal_information

        update_data["$set"]["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = self.db_utils.update_documents(
            collection_name=config.knowledge_collection_name,
            query=query,
            update=update_data,
            upsert=False,
            multi=False,
        )
        return result

    def store_tool(self, API, text, code):
        document = {
            "API": API,
            "text": text,
            "code": code,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.tool_collection_name, document
        )
        return inserted_id

    def get_tools(self, API, k):
        query = {}
        if API:
            query["API"] = API
        documents = self.db_utils.find_documents(
            collection_name=config.tool_collection_name,
            query=query,
            projection={"created_at": 0, "_id": 0},
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        return documents

    def store_diary(self, characterId, diary_content):
        document = {
            "characterId": characterId,
            "diary_content": diary_content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.diary_collection_name, document
        )
        return inserted_id

    def get_diaries(self, characterId, k):
        documents = self.db_utils.find_documents(
            collection_name=config.diary_collection_name,
            query={"characterId": characterId},
            projection={"diary_content": 1, "_id": 0},
            limit=k,
            sort=[("created_at", DESCENDING)],
        )
        return [doc["diary_content"] for doc in documents]

    def store_character(
        self, characterId, characterName, gender, slogan, description, role, task
    ):
        # 生成 full_profile
        full_profile = (
            f"{characterName}; {gender}; {slogan}; {description}; {role}; {task}"
        )
        document = {
            "characterId": characterId,
            "characterName": characterName,
            "gender": gender,
            "slogan": slogan,
            "description": description,
            "role": role,
            "task": task,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "full_profile": full_profile,
        }
        # Insert the document
        inserted_id = self.db_utils.insert_document(
            config.agent_profile_collection_name, document
        )
        return inserted_id

    def get_character(self, characterId):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.agent_profile_collection_name,
            query=query,
        )
        return documents

    def get_character_RAG(self, characterId, topic, k):
        character_documents = self.get_character(characterId)

        character = character_documents[0]
        full_profile = character["full_profile"]

        query_text = f"{full_profile}; {topic}"
        documents = self.vector_search(
            collection_name=config.agent_profile_collection_name,
            query_text=query_text,
            fields_to_return=["characterId", "characterName"],
            k=k + 1,
        )

        filtered_documents = [
            doc for doc in documents if doc["characterId"] != characterId
        ]
        return filtered_documents

    def get_character_RAG_in_list(self, characterId, characterList, topic, k):
        # Retrieve the character's profile
        character_documents = self.get_character(characterId)
        if not character_documents:
            return []

        character = character_documents[0]
        full_profile = character.get("full_profile", "")

        # Formulate the query text
        query_text = f"{full_profile}; {topic}"

        # Perform vector search within the characterList
        documents = self.vector_search(
            collection_name=config.agent_profile_collection_name,
            query_text=query_text,
            fields_to_return=["characterId", "characterName"],
            k=config.numCandidates,
            filter_list=characterList,
        )
        return documents[:k]

    def update_character(self, characterId, update_fields):
        # 首先获取当前character的完整信息
        current_character = self.get_character(characterId)

        # 如果没有找到character，直接返回0
        if not current_character:
            return 0

        current_character = current_character[0]
        update_query = {"characterId": characterId}
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 准备更新数据
        update_data = {"$set": {"updated_at": current_time}}

        # 更新字段
        for key, value in update_fields.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    update_data["$set"][f"{key}.{sub_key}"] = sub_value
                    current_character[key][sub_key] = sub_value
            else:
                update_data["$set"][key] = value
                current_character[key] = value

        # 更新full_profile
        full_profile = f"{current_character['characterName']}; {current_character['gender']}; {current_character['slogan']}; {current_character['description']}; {current_character['role']}; {current_character['task']}"
        update_data["$set"]["full_profile"] = full_profile

        # 生成新的text_embedding
        new_embedding = embed_text(
            full_profile, config.model_name, config.base_url, config.api_key
        )
        update_data["$set"]["text_embedding"] = new_embedding

        # 执行更新操作
        result = self.db_utils.update_documents(
            config.agent_profile_collection_name, update_query, update_data
        )
        return result

    def store_character_arc(self, characterId, category):
        document = {
            "characterId": characterId,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.character_arc_collection_name, document
        )
        return inserted_id

    def get_character_arc(self, characterId):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.character_arc_collection_name,
            query=query,
        )
        return documents

    def get_character_arc_with_changes(self, characterId, k):
        # 获取角色弧光信息
        arc_documents = self.get_character_arc(characterId)
        if not arc_documents:
            return None

        # 获取角色弧光变化信息
        arc_changes = {}
        for category in arc_documents[0]["category"]:
            item = category["item"]
            changes = self.get_character_arc_changes(characterId, item, k)
            arc_changes[item] = changes

        # 组合角色弧光信息和变化过程
        combined_result = {"characterId": characterId, "category": []}

        for category in arc_documents[0]["category"]:
            item = category["item"]
            origin_value = category["origin_value"]
            change_process = [
                {
                    "cause": change["cause"],
                    "context": change["context"],
                    "change": change["change"],
                    "created_at": change["created_at"],
                }
                for change in arc_changes.get(item, [])
            ]

            combined_result["category"].append(
                {
                    "item": item,
                    "origin_value": origin_value,
                    "change_process": change_process,
                }
            )

        return combined_result

    def update_character_arc(self, characterId, category):
        query = {"characterId": characterId}
        update_data = {
            "$set": {
                "category": category,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        result = self.db_utils.update_documents(
            collection_name=config.character_arc_collection_name,
            query=query,
            update=update_data,
            upsert=False,
            multi=False,
        )
        return result

    def store_character_arc_change(self, characterId, item, cause, context, change):
        document = {
            "characterId": characterId,
            "item": item,
            "cause": cause,
            "context": context,
            "change": change,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.character_arc_change_collection_name, document
        )
        return inserted_id

    def get_character_arc_changes(self, characterId, item, k):
        query = {"characterId": characterId, "item": item}

        # 获取所有符合条件的文档
        all_documents = list(
            self.db_utils.find_documents(
                collection_name=config.character_arc_change_collection_name,
                query=query,
                sort=[("created_at", DESCENDING)],
            )
        )

        # 确保包含最新的文档
        if not all_documents:
            return []

        latest_document = all_documents[0]

        # 随机选择 k-1 个文档
        if len(all_documents) > 1:
            random_documents = random.sample(
                all_documents[1:], min(k - 1, len(all_documents) - 1)
            )
        else:
            random_documents = []

        # 将最新的文档添加到选择的文档列表中
        selected_documents = random_documents + [latest_document]

        # 按照创建时间从旧到新排序
        selected_documents.sort(key=lambda doc: doc["created_at"])

        return selected_documents


if __name__ == "__main__":
    db_utils = MongoDBUtils()
    queries = DomainSpecificQueries(db_utils=db_utils)
    # print(queries.get_conversations_with_characterIds(characterIds_list=[1, 5], k=1))
    # print(queries.get_character_RAG(2, "study with my friends", 3))

    # print(queries.get_conversations_containing_characterId(2, 2))

    # # 测试 update_character 方法
    # test_characterId = 1

    # # 获取更新前的 character 数据
    # print("character 数据更新前:")
    # original_character = queries.get_character(test_characterId)
    # print(original_character)

    # # 准备更新数据
    # update_data = {"slogan": "更新后的口号"}

    # # 执行更新
    # update_result = queries.update_character(test_characterId, update_data)
    # print(f"\n更新结果: {update_result}")

    # # 获取更新后的 character 数据
    # print("\ncharacter 数据更新后:")
    # updated_character = queries.get_character(test_characterId)
    # print(updated_character)

    # # 测试获取相遇次数
    # character_ids = [1, 2]
    # encounter_count = queries.get_encounter_count(character_ids)
    # print(f"Initial encounter count for {character_ids}: {encounter_count}")

    # # 测试增量更新相遇次数
    # if encounter_count:
    #     new_count = encounter_count[0]["count"] + 1
    #     result = queries.update_encounter_count(character_ids, new_count)
    #     print(
    #         f"Incremented encounter count for {character_ids}: {new_count}, Result: {result}"
    #     )
    # else:
    #     print(f"No encounter count found for {character_ids} to increment.")

    # # 测试直接更新相遇次数为指定值
    # specified_count = 5
    # result = queries.update_encounter_count(character_ids, specified_count)
    # print(
    #     f"Updated encounter count for {character_ids} to {specified_count}, Result: {result}"
    # )

    # # 测试获取当前好感度
    # from_id = 1
    # to_id = 2
    # current_intimacy = queries.get_intimacy(from_id, to_id)
    # print(f"Initial intimacy level from {from_id} to {to_id}: {current_intimacy}")

    # # 测试更新好感度为新值
    # new_intimacy_level = 7
    # result = queries.update_intimacy(from_id, to_id, new_intimacy_level)
    # print(
    #     f"Updated intimacy level from {from_id} to {to_id} to {new_intimacy_level}, Result: {result}"
    # )

    # # 再次获取以验证更新
    # updated_intimacy = queries.get_intimacy(from_id, to_id)
    # print(f"Updated intimacy level from {from_id} to {to_id}: {updated_intimacy}")

    # # 测试更新 meta_sequence
    # character_id = 102  # 假设的 characterId
    # update_meta_seq = ["scout_area()", "gather_resources()", "set_up_camp()"]

    # # 执行更新操作
    # modified_count = queries.update_meta_seq(character_id, update_meta_seq)
    # print(
    #     f"Updated meta_sequence for characterId {character_id}, Modified Count: {modified_count}"
    # )
    # queries.store_encounter_count(1, 5, 1)
    # print(queries.get_encounters_by_from_id(1, 1))

    # character_list = [2, 3, 4]
    # print(queries.get_character_RAG_in_list(1, character_list, "探索森林", 2))

    db_utils = MongoDBUtils()
    queries = DomainSpecificQueries(db_utils=db_utils)

    # 示例数据存储
    character_id = 1
    # category_data = [
    #     {"item": "skill", "origin_value": "beginner"},
    #     {"item": "emotion", "origin_value": "neutral"},
    # ]

    # # 存储角色弧光信息
    # queries.store_character_arc(character_id, category_data)

    # 存储角色弧光变化信息
    queries.store_character_arc_change(
        characterId=character_id,
        item="skill",
        cause="参加职业培训2",
        context="在朋友的建议下参加了当地的职业技能培训班2",
        change="获得新技能2",
    )

    queries.store_character_arc_change(
        characterId=character_id,
        item="emotion",
        cause="收到好消息2",
        context="得知自己通过了考试2",
        change="略微积极2",
    )

    # 获取角色弧光信息及其变化过程
    k = 2  # 选择变化过程的数量
    arc_with_changes = queries.get_character_arc_with_changes(character_id, k)
    print(arc_with_changes)
