# database/domain_specific_queries.py
import pprint
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
import bisect
import time


class DomainSpecificQueries:
    def __init__(self, db_utils):
        self.db_utils = db_utils
        self.intimacy_thresholds = [0, 20, 30, 40, 60, 70, 80, 90]
        self.relationships = [
            "Mortal Enemies",
            "Rivals",
            "Hostile",
            "Neutral",
            "Acquaintances",
            "Friends",
            "Close Friends",
            "Best Friends",
        ]

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

    def get_relationship(self, intimacy_level):
        index = bisect.bisect_right(self.intimacy_thresholds, intimacy_level) - 1
        index = max(0, min(index, len(self.relationships) - 1))
        return self.relationships[index]

    def store_intimacy(self, from_id, to_id, intimacy_level=50, relationship="Neutral"):
        # 根据 to_id 获取角色信息
        character_documents = self.get_character(characterId=to_id)
        if character_documents:
            to_id_name = character_documents[0].get("characterName", "")  # 获取角色名字
            to_id_spriteId = character_documents[0].get("spriteId", 0)  # 获取角色样貌ID
        else:
            to_id_name = ""
            to_id_spriteId = 0  # 默认值或处理未找到角色的情况

        if intimacy_level != 50:
            relationship = self.get_relationship(intimacy_level)

        document = {
            "from_id": from_id,
            "to_id": to_id,
            "intimacy_level": intimacy_level,
            "to_id_name": to_id_name,  # 新增字段
            "to_id_spriteId": to_id_spriteId,  # 新增字段
            "relationship": relationship,  # 新增字段
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.intimacy_collection_name, document
        )
        return inserted_id

    def get_intimacy(
        self,
        from_id=None,
        to_id=None,
        intimacy_level_min=None,
        intimacy_level_max=None,
        have_conversation=False,
    ):
        # 构建查询条件
        query = {}
        if from_id is not None:
            query["from_id"] = from_id
        if to_id is not None:
            query["to_id"] = to_id
        if intimacy_level_min is not None:
            query["intimacy_level"] = {"$gte": intimacy_level_min}
        if intimacy_level_max is not None:
            if "intimacy_level" in query:
                query["intimacy_level"]["$lte"] = intimacy_level_max
            else:
                query["intimacy_level"] = {"$lte": intimacy_level_max}

        # 如果 have_conversation 为 True，获取所有包含 from_id 的 characterIds
        if have_conversation and from_id is not None:
            conversation_documents = self.db_utils.find_documents(
                collection_name=config.conversation_collection_name,
                query={"characterIds": from_id},
                projection={"characterIds": 1},
            )
            # 提取所有相关的 characterIds
            related_ids = set()
            for doc in conversation_documents:
                related_ids.update(doc["characterIds"])
            # 移除 from_id 自身
            related_ids.discard(from_id)
            # 更新查询条件
            query["to_id"] = {"$in": list(related_ids)}

        # 执行查询
        documents = self.db_utils.find_documents(
            collection_name=config.intimacy_collection_name, query=query
        )
        return documents

    def update_intimacy(self, from_id, to_id, new_intimacy_level=None):
        if new_intimacy_level is None:
            raise ValueError("new_intimacy_level must be provided")

        relationship = self.get_relationship(new_intimacy_level)

        query = {"from_id": from_id, "to_id": to_id}
        update = {
            "$set": {
                "intimacy_level": new_intimacy_level,
                "relationship": relationship,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        result = self.db_utils.update_documents(
            collection_name=config.intimacy_collection_name,
            query=query,
            update=update,
        )
        return result

    def decrease_all_intimacy_levels(self):
        # 递减 intimacy_level 并更新时间
        query = {"intimacy_level": {"$gt": 50}}
        update = {
            "$inc": {"intimacy_level": -1},
            "$set": {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        }
        result = self.db_utils.update_documents(
            collection_name=config.intimacy_collection_name,
            query=query,
            update=update,
            multi=True,
        )

        # 定义阈值与相应的新关系映射
        threshold_relationship_map = {
            59: "Neutral",
            69: "Acquaintances",
            79: "Friends",
            89: "Close Friends",
        }

        # 获取所有达到阈值的文档
        query = {"intimacy_level": {"$in": list(threshold_relationship_map.keys())}}
        documents = self.db_utils.find_documents(
            collection_name=config.intimacy_collection_name, query=query
        )

        # 构建批量更新操作
        bulk_operations = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for document in documents:
            new_level = document["intimacy_level"]
            new_relationship = threshold_relationship_map.get(
                new_level, document["relationship"]
            )
            bulk_operations.append(
                {
                    "filter": {
                        "from_id": document["from_id"],
                        "to_id": document["to_id"],
                    },
                    "update": {
                        "$set": {
                            "relationship": new_relationship,
                            "updated_at": current_time,
                        }
                    },
                }
            )

        # 执行批量更新
        self.db_utils.bulk_update_documents(
            collection_name=config.intimacy_collection_name,
            operations=bulk_operations,
            ordered=False,  # 可根据需求设置为 True 或 False
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

    def store_cv(
        self,
        jobid,
        characterId,
        CV_content,
        week,
        health,
        studyxp,
        date,
        jobName,
        election_status="not_yet",
    ):
        # 查找符合条件的文档并提取去重后的 jobName 列表
        query = {"characterId": characterId, "election_status": "succeeded"}
        documents = self.db_utils.find_documents(config.cv_collection_name, query)
        experience = list({doc["jobName"] for doc in documents})

        document = {
            "jobid": jobid,
            "characterId": characterId,
            "CV_content": CV_content,
            "week": week,
            "health": health,
            "studyxp": studyxp,
            "date": date,
            "experience": experience,  # 更新后的 experience
            "jobName": jobName,  # 新增的 jobName 字段
            "election_status": election_status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(config.cv_collection_name, document)
        return inserted_id

    def update_election_status(
        self, characterId, election_status, jobid=None, week=None
    ):
        # 构建查询条件
        query = {"characterId": characterId}
        if jobid is not None:
            query["jobid"] = jobid
        if week is not None:
            query["week"] = week

        # 如果没有提供 week，则查找最新的文档
        if week is None:
            documents = self.db_utils.find_documents(
                collection_name=config.cv_collection_name,
                query=query,
                sort=[("week", DESCENDING)],
                limit=1,
            )
            if documents:
                query["week"] = documents[0]["week"]
            else:
                raise ValueError("No CV found for the given characterId and jobid.")

        # 更新 election_status
        update_data = {"$set": {"election_status": election_status}}
        result = self.db_utils.update_documents(
            collection_name=config.cv_collection_name,
            query=query,
            update=update_data,
            upsert=False,
            multi=False,
        )
        return result

    def get_cv(self, jobid=None, characterId=None, week=None, election_status=None):
        query = {}
        if jobid is not None:
            query["jobid"] = jobid
        if characterId is not None:
            query["characterId"] = characterId
        if week is not None:
            query["week"] = week
        if election_status is not None:
            query["election_status"] = election_status

        # 查找符合条件的文档
        documents = self.db_utils.find_documents(
            collection_name=config.cv_collection_name,
            query=query,
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
        # 拼接非空字段
        fields = [
            characterName,
            gender,
            relationship,
            personality,
            biography,
            long_term_goal,
            short_term_goal,
            language_style,
        ]
        full_profile = "; ".join([field for field in fields if field])

        # 如果 full_profile 为空，则设置为 " "
        full_profile = full_profile if full_profile else " "
        document = {
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
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "full_profile": full_profile,
        }
        # 插入文档
        inserted_id = self.db_utils.insert_document(
            config.agent_profile_collection_name, document
        )
        return inserted_id

    def get_character(self, characterId=None):
        query = {}
        if characterId is not None:
            query["characterId"] = characterId

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
        fields = [
            current_character.get("characterName", ""),
            current_character.get("gender", ""),
            current_character.get("relationship", ""),
            current_character.get("personality", ""),
            current_character.get("long_term_goal", ""),
            current_character.get("short_term_goal", ""),
            current_character.get("language_style", ""),
            current_character.get("biography", ""),
        ]
        full_profile = "; ".join([field for field in fields if field])
        full_profile = full_profile if full_profile else " "
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

    def get_relationship_sample(self):
        profile_sample = self.db_utils.find_one(
            collection_name=config.profile_sample_collection_name
        )
        relationship_list = profile_sample.get("relationship", [])

        # 随机抽取 2 到 4 个关系特征
        sample_size = random.randint(2, 4)
        relationship_sample = random.sample(relationship_list, sample_size)

        return relationship_sample

    def get_personality_sample(self):
        profile_sample = self.db_utils.find_one(
            collection_name=config.profile_sample_collection_name
        )
        personality_list = profile_sample.get("personality", [])

        # 随机抽取 3 到 5 个性格特征
        sample_size = random.randint(3, 5)
        personality_sample = random.sample(personality_list, sample_size)

        return personality_sample

    def get_long_term_goal_sample(self):
        profile_sample = self.db_utils.find_one(
            collection_name=config.profile_sample_collection_name
        )
        long_term_goal_list = profile_sample.get("long_term_goal", [])

        # 随机抽取 2 到 3 个长期目标
        sample_size = random.randint(2, 3)
        long_term_goal_sample = random.sample(long_term_goal_list, sample_size)

        return long_term_goal_sample

    def get_short_term_goal_sample(self):
        profile_sample = self.db_utils.find_one(
            collection_name=config.profile_sample_collection_name
        )
        short_term_goal_list = profile_sample.get("short_term_goal", [])

        # 随机抽取 1 到 3 个短期目标
        sample_size = random.randint(1, 3)
        short_term_goal_sample = random.sample(short_term_goal_list, sample_size)

        return short_term_goal_sample

    def get_language_style_sample(self):
        profile_sample = self.db_utils.find_one(
            collection_name=config.profile_sample_collection_name
        )
        language_style_list = profile_sample.get("language_style", [])

        # 随机抽取 3 到 5 个语言风格
        sample_size = random.randint(3, 5)
        language_style_sample = random.sample(language_style_list, sample_size)

        return language_style_sample

    def get_biography_sample(self):
        profile_sample = self.db_utils.find_one(
            collection_name=config.profile_sample_collection_name
        )
        biography_list = profile_sample.get("biography", [])

        # 随机抽取一个传记
        biography_sample = random.choice(biography_list)

        return biography_sample

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
        # 默认值字典
        defaults = {
            "daily_goal": "sleep well",
            "refer_to_previous": True,
            "life_style": "Busy",
            "daily_objective_ar": "",
            "task_priority": [],
            "max_actions": 10,
            "meta_seq_ar": "",
            "replan_time_limit": 1,
            "meta_seq_adjuster_ar": "",
            "focus_topic": [],
            "depth_of_reflection": "Deep",
            "reflection_ar": "",
            "level_of_detail": "Shallow",
            "tone_and_style": "Gentle",
        }

        # 使用字典的 get 方法来设置参数值
        document = {
            "characterId": characterId,
            "daily_goal": (
                daily_goal if daily_goal is not None else defaults["daily_goal"]
            ),
            "refer_to_previous": (
                refer_to_previous
                if refer_to_previous is not None
                else defaults["refer_to_previous"]
            ),
            "life_style": (
                life_style if life_style is not None else defaults["life_style"]
            ),
            "daily_objective_ar": (
                daily_objective_ar
                if daily_objective_ar is not None
                else defaults["daily_objective_ar"]
            ),
            "task_priority": (
                task_priority
                if task_priority is not None
                else defaults["task_priority"]
            ),
            "max_actions": (
                max_actions if max_actions is not None else defaults["max_actions"]
            ),
            "meta_seq_ar": (
                meta_seq_ar if meta_seq_ar is not None else defaults["meta_seq_ar"]
            ),
            "replan_time_limit": (
                replan_time_limit
                if replan_time_limit is not None
                else defaults["replan_time_limit"]
            ),
            "meta_seq_adjuster_ar": (
                meta_seq_adjuster_ar
                if meta_seq_adjuster_ar is not None
                else defaults["meta_seq_adjuster_ar"]
            ),
            "focus_topic": (
                focus_topic if focus_topic is not None else defaults["focus_topic"]
            ),
            "depth_of_reflection": (
                depth_of_reflection
                if depth_of_reflection is not None
                else defaults["depth_of_reflection"]
            ),
            "reflection_ar": (
                reflection_ar
                if reflection_ar is not None
                else defaults["reflection_ar"]
            ),
            "level_of_detail": (
                level_of_detail
                if level_of_detail is not None
                else defaults["level_of_detail"]
            ),
            "tone_and_style": (
                tone_and_style
                if tone_and_style is not None
                else defaults["tone_and_style"]
            ),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        inserted_id = self.db_utils.insert_document(
            config.agent_prompt_collection_name, document
        )
        return inserted_id

    def get_agent_prompt(self, characterId):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.agent_prompt_collection_name,
            query=query,
        )
        return documents

    def update_agent_prompt(self, characterId, update_fields):
        query = {"characterId": characterId}
        update_data = {"$set": update_fields}
        update_data["$set"]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = self.db_utils.update_documents(
            collection_name=config.agent_prompt_collection_name,
            query=query,
            update=update_data,
            upsert=False,
            multi=False,
        )
        return result

    def delete_agent_prompt(self, characterId):
        query = {"characterId": characterId}
        result = self.db_utils.delete_documents(
            collection_name=config.agent_prompt_collection_name,
            query=query,
        )
        return result

    def store_conversation_prompt(
        self,
        characterId,
        topic_requirements=None,
        relation=None,
        emotion=None,
        personality=None,
        habits_and_preferences=None,
    ):
        document = {
            "characterId": characterId,
            "topic_requirements": topic_requirements,
            "relation": relation,
            "emotion": emotion,
            "personality": personality,
            "habits_and_preferences": habits_and_preferences,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.conversation_prompt_collection_name, document
        )
        return inserted_id

    def get_conversation_prompt(self, characterId):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.conversation_prompt_collection_name,
            query=query,
        )
        return documents

    def update_conversation_prompt(self, characterId, update_fields):
        query = {"characterId": characterId}
        update_data = {"$set": update_fields}
        update_data["$set"]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = self.db_utils.update_documents(
            collection_name=config.conversation_prompt_collection_name,
            query=query,
            update=update_data,
            upsert=False,
            multi=False,
        )
        return result

    def delete_conversation_prompt(self, characterId):
        query = {"characterId": characterId}
        result = self.db_utils.delete_documents(
            collection_name=config.conversation_prompt_collection_name,
            query=query,
        )
        return result

    def store_decision(
        self,
        characterId,
        need_replan=None,
        action_description=None,
        action_result=None,
        new_plan=None,
        daily_objective=None,
        meta_seq=None,
        reflection=None,
    ):
        document = {
            "characterId": characterId,
            "need_replan": need_replan,
            "action_description": action_description,
            "action_result": action_result,
            "new_plan": new_plan,
            "daily_objective": daily_objective,
            "meta_seq": meta_seq,
            "reflection": reflection,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.decision_collection_name, document
        )
        return inserted_id

    def get_decision(self, characterId, count=None):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.decision_collection_name,
            query=query,
            sort=[("updated_at", -1)],
        )

        if not documents:
            return []

        if count is None or not isinstance(count, int) or count <= 0:
            return [documents[0]]

        list_fields = [
            "action_description",
            "action_result",
            "new_plan",
            "daily_objective",
            "meta_seq",
            "reflection",
        ]

        latest_doc = documents[0].copy()

        for field in list_fields:
            merged_list = []
            needed = count
            for doc in documents:
                current_list = doc.get(field, [])
                if not current_list:
                    continue
                to_take = min(needed, len(current_list))
                # 从列表末尾取 to_take 个元素，这些元素已经是老->新顺序
                sublist = current_list[-to_take:]
                needed -= to_take
                if not merged_list:
                    # 第一次直接赋值
                    merged_list = sublist
                else:
                    # 老的文档数据应该放在前面
                    merged_list = sublist + merged_list

                if needed <= 0:
                    break

            latest_doc[field] = merged_list

        return [latest_doc]
    def store_current_pointer(self, characterId, current_pointer):
        document = {
            "characterId": characterId,
            "current_pointer": current_pointer,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.current_pointer_collection_name, document
        )
        return inserted_id

    def get_current_pointer(self, characterId):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.current_pointer_collection_name,
            query=query,
        )
        return documents

    def update_current_pointer(self, characterId, new_pointer):
        query = {"characterId": characterId}
        update_data = {
            "$set": {
                "current_pointer": new_pointer,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
        result = self.db_utils.update_documents(
            collection_name=config.current_pointer_collection_name,
            query=query,
            update=update_data,
            upsert=False,
            multi=False,
        )
        return result

    def delete_current_pointer(self, characterId):
        query = {"characterId": characterId}
        result = self.db_utils.delete_documents(
            collection_name=config.current_pointer_collection_name,
            query=query,
        )
        return result

if __name__ == "__main__":
    db_utils = MongoDBUtils()
    queries = DomainSpecificQueries(db_utils=db_utils)

    # 测试存储 current_pointer
    print("存储 current_pointer...")
    characterId = 1
    current_pointer = "pointer_1"
    inserted_id = queries.store_current_pointer(characterId, current_pointer)
    print(f"插入成功，文档 ID：{inserted_id}")

    # 测试获取 current_pointer
    print("\n获取 current_pointer...")
    documents = queries.get_current_pointer(characterId)
    print("获取的 current_pointer 文档：", documents)

    # 测试更新 current_pointer
    print("\n更新 current_pointer...")
    new_pointer = "pointer_2"
    update_result = queries.update_current_pointer(characterId, new_pointer)
    print(f"更新成功，修改了 {update_result} 个文档。")

    # 再次获取以验证更新
    print("\n更新后的 current_pointer...")
    updated_documents = queries.get_current_pointer(characterId)
    print("更新后的 current_pointer 文档：", updated_documents)

    # 测试删除 current_pointer
    print("\n删除 current_pointer...")
    delete_result = queries.delete_current_pointer(characterId)
    print(f"删除成功，删除了 {delete_result} 个文档。")

    # 验证删除
    print("\n验证删除后的 current_pointer...")
    deleted_documents = queries.get_current_pointer(characterId)
    print("删除后的 current_pointer 文档：", deleted_documents)


    # print("存储决策数据...")

    # characterId = 2
    # # 创建多条测试文档，使其有不同的列表数量和时间戳
    # # doc1: 较早的文档
    # queries.store_decision(
    #     characterId=characterId,
    #     need_replan=True,
    #     action_description=["desc1_1", "desc1_2"],
    #     action_result=["res1_1"],
    #     new_plan=["plan1_1", "plan1_2", "plan1_3"],
    #     daily_objective=["obj1_1"],
    #     meta_seq=["meta1_1", "meta1_2"],
    #     reflection=["ref1_1", "ref1_2", "ref1_3"],
    # )
    # time.sleep(1)

    # # doc2: 较新的文档，增加更多元素
    # queries.store_decision(
    #     characterId=characterId,
    #     need_replan=False,
    #     action_description=["desc2_1", "desc2_2", "desc2_3"],
    #     action_result=["res2_1", "res2_2"],
    #     new_plan=["plan2_1"],
    #     daily_objective=["obj2_1", "obj2_2"],
    #     meta_seq=["meta2_1"],
    #     reflection=["ref2_1"],
    # )
    # time.sleep(1)

    # # doc3: 最新的文档
    # queries.store_decision(
    #     characterId=characterId,
    #     need_replan=True,
    #     action_description=["desc3_1"],
    #     action_result=["res3_1", "res3_2", "res3_3"],
    #     new_plan=["plan3_1", "plan3_2"],
    #     daily_objective=["obj3_1", "obj3_2", "obj3_3"],
    #     meta_seq=["meta3_1", "meta3_2", "meta3_3", "meta3_4"],
    #     reflection=["ref3_1"],
    # )
    # time.sleep(1)

    # print("测试 get_decision 不带 count 参数（返回最新文档）...")
    # latest_docs = queries.get_decision(characterId=characterId)
    # for doc in latest_docs:
    #     print("---- 最新文档(不带count) ----")
    #     print(doc)

    # print("\n测试 get_decision 带 count 参数 = 3 ...")
    # # 我们要求每个列表字段都至少返回3个，如果最新文档不够，则从历史文档补充
    # limited_docs = queries.get_decision(characterId=characterId, count=10)
    # for doc in limited_docs:
    #     print("---- 限定数量的最新文档 ----")
    #     print("action_description:", doc["action_description"])
    #     print("action_result:", doc["action_result"])
    #     print("new_plan:", doc["new_plan"])
    #     print("daily_objective:", doc["daily_objective"])
    #     print("meta_seq:", doc["meta_seq"])
    #     print("reflection:", doc["reflection"])
    #     print(doc)

    # # 存储多个简历，包含不同的 election_status
    # print("存储简历...")
    # statuses = ["not_yet", "failed", "succeeded"]
    # job_names = ["工程师", "设计师", "产品经理"]  # 新增的 jobName 列表
    # for i, (status, job_name) in enumerate(zip(statuses, job_names), start=1):
    #     inserted_id = queries.store_cv(
    #         jobid=100 + i,
    #         characterId=1,
    #         CV_content=f"这是简历内容示例 {i}",
    #         week=12 + i,
    #         health=80 + i * 5,
    #         studyxp=150 + i * 10,
    #         date=20231015 + i,
    #         election_status=status,
    #         jobName=job_name,  # 传递 jobName
    #     )
    #     print(f"插入成功，文档 ID：{inserted_id}")

    # # 测试获取简历
    # print("获取简历...")
    # documents = queries.get_cv(characterId=1)
    # for doc in documents:
    #     print(doc)

    # # 测试 store_conversation_prompt 方法
    # print("存储对话提示...")
    # inserted_id = queries.store_conversation_prompt(
    #     characterId=1,
    #     topic_requirements="Discuss future plans",
    #     relation="Friend",
    #     emotion="Happy",
    #     personality="Introversion",
    #     habits_and_preferences="Likes to talk about technology"
    # )
    # print(f"插入成功，文档 ID：{inserted_id}")

    # # 测试 get_conversation_prompt 方法
    # print("\n获取对话提示...")
    # conversation_prompts = queries.get_conversation_prompt(characterId=1)
    # print("获取的对话提示：", conversation_prompts)

    # # 测试 update_conversation_prompt 方法
    # print("\n更新对话提示...")
    # update_result = queries.update_conversation_prompt(
    #     characterId=1,
    #     update_fields={"emotion": "Excited", "relation": "Best Friend"}
    # )
    # print(f"更新成功，修改了 {update_result} 个文档。")

    # # 再次获取以验证更新
    # print("\n更新后的对话提示...")
    # updated_conversation_prompts = queries.get_conversation_prompt(characterId=1)
    # print("更新后的对话提示：", updated_conversation_prompts)

    # # 测试 delete_conversation_prompt 方法
    # print("\n删除对话提示...")
    # delete_result = queries.delete_conversation_prompt(characterId=1)
    # print(f"删除成功，删除了 {delete_result} 个文档。")

    # # 验证删除
    # print("\n验证删除后的对话提示...")
    # deleted_conversation_prompts = queries.get_conversation_prompt(characterId=1)
    # print("删除后的对话提示：", deleted_conversation_prompts)

    # # 测试 get_intimacy 函数
    # print("查询 from_id=1 的所有对话记录:")
    # print(queries.get_conversations_containing_characterId(1, 0))

    # # 测试 get_intimacy 函数
    # print("查询 from_id=1 的所有记录:")
    # print(queries.get_intimacy(from_id=1))

    # # 插入更多数据：亲密度从 40 到 90
    # print("插入数据...")
    # for i in range(1, 6):
    #     queries.store_intimacy(i, i + 1, intimacy_level=40 + i * 10)
    # print(queries.get_intimacy())

    # # 测试 decrease_all_intimacy_levels：递减所有亲密度大于 50 的记录
    # print("\n执行 decrease_all_intimacy_levels...")
    # decrease_count = queries.decrease_all_intimacy_levels()
    # print(f"递减成功，更新了 {decrease_count} 个文档。")
    # print(queries.get_intimacy())

    # # 插入数据：亲密度为 50，relationship 由系统自动计算
    # print("插入数据...")
    # inserted_id = queries.store_intimacy(1, 2, intimacy_level=50)
    # print(f"插入成功，文档 ID：{inserted_id}")

    # # 获取数据：查询 from_id=1 和 to_id=2 的亲密度
    # print("\n获取数据...")
    # intimacy_records = queries.get_intimacy(1, 2)
    # print(intimacy_records)

    # # 更新数据：将亲密度更新为 80
    # print("\n更新数据...")
    # updated_count = queries.update_intimacy(1, 2, new_intimacy_level=80)
    # print(f"更新成功，修改了 {updated_count} 个文档。")

    # # 再次获取数据：查询更新后的亲密度
    # print("\n更新后的数据...")
    # updated_records = queries.get_intimacy(1, 2)
    # print(updated_records)

    # # 测试 get_personality_sample 方法
    # personality_sample = queries.get_personality_sample()
    # print("随机抽取的性格特征样本:", personality_sample)

    # # 测试 get_long_term_goal_sample 方法
    # long_term_goal_sample = queries.get_long_term_goal_sample()
    # print("随机抽取的长期目标样本:", long_term_goal_sample)

    # # 测试 get_short_term_goal_sample 方法
    # short_term_goal_sample = queries.get_short_term_goal_sample()
    # print("随机抽取的短期目标样本:", short_term_goal_sample)

    # # 测试 get_language_style_sample 方法
    # language_style_sample = queries.get_language_style_sample()
    # print("随机抽取的语言风格样本:", language_style_sample)

    # # 测试 get_biography_sample 方法
    # biography_sample = queries.get_biography_sample()
    # print("随机抽取的传记样本:", biography_sample)

    # print(queries.get_conversations_with_characterIds(characterIds_list=[1, 5], k=1))
    # print(queries.get_character_RAG(2, "study with my friends", 3))

    # print(queries.get_conversations_containing_characterId(2, 2))

    # # 测试 update_character 方法
    # test_characterId = 1

    # # 获取更新前的 character 数据
    # print("character 数据更新前:")
    # original_character = queries.get_character(test_characterId)
    # print(original_character)

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

    # # 示例数据存储
    # character_id = 1
    # # category_data = [
    # #     {"item": "skill", "origin_value": "beginner"},
    # #     {"item": "emotion", "origin_value": "neutral"},
    # # ]

    # # # 存储角色弧光信息
    # # queries.store_character_arc(character_id, category_data)

    # # 存储角色弧光变化信息
    # queries.store_character_arc_change(
    #     characterId=character_id,
    #     item="skill",
    #     cause="参加职业培训2",
    #     context="在朋友的建议下参加了当地的职业技能培训班2",
    #     change="获得新技能2",
    # )

    # queries.store_character_arc_change(
    #     characterId=character_id,
    #     item="emotion",
    #     cause="收到好消息2",
    #     context="得知自己通过了考试2",
    #     change="略微积极2",
    # )

    # # 获取角色弧光信息及其变化过程
    # k = 2  # 选择变化过程的数量
    # arc_with_changes = queries.get_character_arc_with_changes(character_id, k)
    # print(arc_with_changes)

    # # 存储测试数据
    # queries.store_intimacy(from_id=10, to_id=20, intimacy_level=75)
    # queries.store_intimacy(from_id=10, to_id=30, intimacy_level=50)
    # queries.store_intimacy(from_id=20, to_id=10, intimacy_level=60)
    # queries.store_intimacy(from_id=30, to_id=10, intimacy_level=80)

    # # 测试 get_intimacy 函数
    # print("查询 from_id=1 的所有记录:")
    # print(queries.get_intimacy(from_id=10))

    # print("\n查询 to_id=1 的所有记录:")
    # print(queries.get_intimacy(to_id=10))

    # print("\n查询 intimacy_level 在 60 到 80 之间的记录:")
    # print(queries.get_intimacy(intimacy_level_min=60, intimacy_level_max=80))

    # print("\n查询 from_id=1 且 intimacy_level 在 60 到 80 之间的记录:")
    # print(
    #     queries.get_intimacy(from_id=10, intimacy_level_min=60, intimacy_level_max=80)
    # )

    # # 存储一些测试数据
    # print("存储测试数据:")
    # queries.store_cv(jobid=1, characterId=101, CV_content="CV内容1", week=1)
    # queries.store_cv(jobid=1, characterId=102, CV_content="CV内容2", week=2)
    # queries.store_cv(jobid=2, characterId=101, CV_content="CV内容3", week=1)
    # queries.store_cv(jobid=2, characterId=103, CV_content="CV内容4", week=3)

    # # 更新选举状态
    # print("\n更新选举状态:")
    # queries.update_election_status(
    #     characterId=101, election_status="succeeded", jobid=1, week=1
    # )
    # queries.update_election_status(characterId=102, election_status="failed", jobid=1)
    # queries.update_election_status(
    #     characterId=103, election_status="succeeded", jobid=2
    # )

    # # 测试 get_cv 方法
    # print("\n测试 get_cv 方法:")

    # # 查询所有最新周的数据
    # print("\n查询所有的数据:")
    # print(queries.get_cv())

    # # 查询特定 jobid 的所有最新周的数据
    # print("\n查询 jobid=1 的所有的数据:")
    # print(queries.get_cv(jobid=1))

    # # 查询特定 characterId 的所有最新周的数据
    # print("\n查询 characterId=101 的所有的数据:")
    # print(queries.get_cv(characterId=101))

    # # 查询特定 week 的数据
    # print("\n查询 week=1 的数据:")
    # print(queries.get_cv(week=1))

    # # 查询特定选举状态的数据
    # print("\n查询选举状态为 'succeeded' 的数据:")
    # print(queries.get_cv(election_status="succeeded"))

    # # 查询特定 jobid 和选举状态的数据
    # print("\n查询 jobid=1 且选举状态为 'failed' 的数据:")
    # print(queries.get_cv(jobid=1, election_status="failed"))

    # # 查询特定 characterId 和 week 的数据
    # print("\n查询 characterId=101 且 week=1 的数据:")
    # print(queries.get_cv(characterId=101, week=1))

    # # 测试获取所有角色
    # print("获取所有角色:")
    # all_characters = queries.get_character()
    # print(all_characters)
