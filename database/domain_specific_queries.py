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
import json


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

        # 如果 have_conversation 为 True，获取所有包含 from_id 的对话
        if have_conversation and from_id is not None:
            conversation_documents = self.db_utils.find_documents(
                collection_name=config.conversation_collection_name,
                query={"$or": [{"from_id": from_id}, {"to_id": from_id}]},
                projection={"from_id": 1, "to_id": 1},
            )
            # 提取所有相关的 characterIds
            related_ids = set()
            for doc in conversation_documents:
                related_ids.add(doc["from_id"])
                related_ids.add(doc["to_id"])
            # 移除 from_id 自身
            related_ids.discard(from_id)
            # 更新查询条件
            query["to_id"] = {"$in": list(related_ids)}

        # 执行查询
        documents = self.db_utils.find_documents(
            collection_name=config.intimacy_collection_name, query=query
        )
        return documents

    def get_knowledge_graph_data(self, character_id):
        """
        一次性查询出与 character_id 直接或间接相关的 intimacy 文档，
        并将其整理成与图片所示更贴近的 JSON 格式（包含 sexType 等）。
        """

        # 1) 查找与 character_id 直接相关的文档
        direct_query = {
            "$or": [
                {"from_id": character_id},
                {"to_id": character_id},
            ]
        }
        direct_docs = self.db_utils.find_documents(
            collection_name=config.intimacy_collection_name, query=direct_query
        )

        # 收集所有相关角色ID
        related_ids = set()
        for doc in direct_docs:
            related_ids.add(doc["from_id"])
            related_ids.add(doc["to_id"])

        # 若无任何直接关联，返回空图
        if not related_ids:
            empty_result = {"rootId": f"N{character_id}", "nodes": [], "lines": []}
            return json.dumps(empty_result, ensure_ascii=False, indent=4)

        # 2) 再查 from_id、to_id 均在 related_ids 里的文档
        related_query = {
            "from_id": {"$in": list(related_ids)},
            "to_id": {"$in": list(related_ids)},
        }
        intimacy_docs = self.db_utils.find_documents(
            collection_name=config.intimacy_collection_name, query=related_query
        )

        # 3) 收集所有角色ID，批量获取角色信息
        all_ids = set()
        for doc in intimacy_docs:
            all_ids.add(doc["from_id"])
            all_ids.add(doc["to_id"])

        # 批量查角色信息，减少数据库调用
        character_query = {"characterId": {"$in": list(all_ids)}}
        character_docs = self.db_utils.find_documents(
            collection_name=config.agent_profile_collection_name, query=character_query
        )
        # 用字典缓存
        char_map = {doc["characterId"]: doc for doc in character_docs}

        # 4) 组织节点 (nodes)
        nodes = []
        for cid in sorted(all_ids):
            char_doc = char_map.get(cid, {})

            # 角色名
            text_value = char_doc.get("characterName", f"Character_{cid}")
            # 头像 spriteId（这里直接返回 spriteId，也可根据你需求构造完整URL）
            icon_value = str(
                char_doc.get("image")
                or "https://i.postimg.cc/ht2MvWwm/c57c5212d5f9861b230525a5e848bb1.png"
            )

            # 性别
            gender_value = char_doc.get("gender", "")
            if not gender_value:
                gender_value = "Unknown"

            # 这里可以给节点按性别设置不同颜色，也可统一
            if gender_value == "Female":
                node_color = "#ec6941"
                node_border = "#ff875e"
            elif gender_value == "Male":
                node_color = "rgba(0,206,253,1)"  # 示例
                node_border = "#6ec0f0"  # 示例
            else:
                # 未知性别时的默认颜色
                node_color = "#cccccc"
                node_border = "#999999"

            node_data = {
                "id": f"N{cid}",
                "text": text_value,
                "color": node_color,
                "borderColor": node_border,
                "data": {
                    # sexType 对应 gender, 不存在则为 "未知"
                    "sexType": gender_value
                },
                "icon": icon_value,
            }
            nodes.append(node_data)

        # 5) 组织连线 (lines)
        lines = []
        for doc in intimacy_docs:
            from_id = doc["from_id"]
            to_id = doc["to_id"]
            relationship = doc.get("relationship", "")
            intimacy_level = doc.get("intimacy_level", 0)

            # 三段渐变：0 -> #00C2FF, 50 -> #FFFFFF, 100 -> #F06E25
            line_color = self._intimacy_level_to_color(intimacy_level)

            line_data = {
                "from": f"N{from_id}",
                "to": f"N{to_id}",
                "text": relationship,
                "color": line_color,
                "fontColor": line_color,
                "data": {"type": relationship},
            }
            lines.append(line_data)

        # 6) 最终结果
        knowledge_graph = {"rootId": f"N{character_id}", "nodes": nodes, "lines": lines}

        # 返回 JSON 字符串
        return knowledge_graph

    def _intimacy_level_to_color(self, level: int) -> str:
        """
        将 0~100 的亲密度映射到三段渐变：
         - 0   -> #00C2FF (蓝)
         - 50  -> #FFFFFF (白)
         - 100 -> #F06E25 (橙红)
        """
        level = max(0, min(level, 100))

        if level == 0:
            return "#00C2FF"
        if level == 50:
            return "#FFFFFF"
        if level == 100:
            return "#F06E25"

        # 0~50: 从 #00C2FF -> #FFFFFF
        # 50~100: 从 #FFFFFF -> #F06E25
        if level < 50:
            start_hex, end_hex = "#00C2FF", "#FFFFFF"
            ratio = level / 50.0
        else:
            start_hex, end_hex = "#FFFFFF", "#F06E25"
            ratio = (level - 50) / 50.0

        r1, g1, b1 = self._hex_to_rgb(start_hex)
        r2, g2, b2 = self._hex_to_rgb(end_hex)
        r = int(r1 + ratio * (r2 - r1))
        g = int(g1 + ratio * (g2 - g1))
        b = int(b1 + ratio * (b2 - b1))

        return f"#{r:02X}{g:02X}{b:02X}"

    def _hex_to_rgb(self, hex_str: str) -> tuple:
        """#RRGGBB -> (R, G, B)"""
        hex_str = hex_str.lstrip("#")
        return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))

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
            sort=[("count", DESCENDING)],  # 按相遇次数降序排序
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

    def store_action(self, characterId, location, gameTime):
        """
        存储 action 数据，字段包括 characterId、location 和 gameTime。
        """
        document = {
            "characterId": characterId,
            "location": location,
            "gameTime": gameTime,
        }
        inserted_id = self.db_utils.insert_document(
            config.action_collection_name, document
        )
        return inserted_id

    def get_action_counts_in_time_range(self, from_time, to_time):
        """
        高效统计在 [from_time, to_time) 区间内，不同地点的出现次数。

        返回:
        - dict, 如: {
            "school": 2,
            "workshop": 0,
            "home": 1,
            ...,
        }
        """
        # 固定地点列表
        ALL_LOCATIONS = [
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
        ]

        # 聚合管道
        pipeline = [
            {"$match": {"gameTime": {"$gte": from_time, "$lt": to_time}}},
            {
                "$group": {
                    "_id": "$location",  # 使用 location 字段作为分组键
                    "count": {"$sum": 1},
                }
            },
        ]

        # 执行聚合查询
        results = self.db_utils.aggregate(
            collection_name=config.action_collection_name, pipeline=pipeline
        )

        # 将查询到的结果转为字典 {地点: 数量}
        action_counts = {doc["_id"]: doc["count"] for doc in results}

        # 构建最终输出，确保所有地点都在输出中
        final_counts = {loc: action_counts.get(loc, 0) for loc in ALL_LOCATIONS}

        return final_counts

    def get_all_action_counts(self):
        """
        统计从第 0 天到当前最新一天的各地点人数：

        返回:
        {
        "xAxis": [...从第 0 天到最新天的天数...],
        "series": [
            { "name": 地点, "data": [每天统计值] },
            ...
        ]
        }
        """

        # 1) 找到数据库中最大天数 maxDay
        pipeline_max_day = [
            {
                "$addFields": {
                    "dayInt": {
                        "$toInt": {"$arrayElemAt": [{"$split": ["$gameTime", ":"]}, 0]}
                    }
                }
            },
            {"$group": {"_id": None, "maxDay": {"$max": "$dayInt"}}},
        ]

        max_day_result = list(
            self.db_utils.aggregate(
                collection_name=config.action_collection_name, pipeline=pipeline_max_day
            )
        )

        if not max_day_result or max_day_result[0].get("maxDay") is None:
            # 如果库里没有任何文档 or 没有可解析的 dayInt，直接返回空数据
            return {
                "xAxis": [],
                "series": [
                    {"name": loc, "data": []}
                    for loc in [
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
                    ]
                ],
            }

        max_day = max_day_result[0]["maxDay"]

        # 确定统计的时间范围：从第 0 天到 maxDay
        start_day = 0
        end_day = max_day

        # 2) 聚合查询，统计每个地点在 [start_day..end_day] 范围内的每日数量
        pipeline_actions = [
            {
                "$addFields": {
                    "dayInt": {
                        "$toInt": {"$arrayElemAt": [{"$split": ["$gameTime", ":"]}, 0]}
                    }
                }
            },
            {"$match": {"dayInt": {"$gte": start_day, "$lte": end_day}}},
            {
                "$group": {
                    "_id": {"day": "$dayInt", "location": "$location"},
                    "count": {"$sum": 1},
                }
            },
        ]

        agg_results = list(
            self.db_utils.aggregate(
                collection_name=config.action_collection_name, pipeline=pipeline_actions
            )
        )

        # 3) 构建 {day: {location: count}} 的数据结构
        ALL_LOCATIONS = [
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
        ]

        # day_location_map 形如: { dayInt: { location: count, ... }, ... }
        day_location_map = {}
        for d in range(start_day, end_day + 1):  # 初始化所有天数
            day_location_map[d] = {loc: 0 for loc in ALL_LOCATIONS}

        for doc in agg_results:
            day_int = doc["_id"]["day"]
            location = doc["_id"]["location"]
            count = doc["count"]

            # 如果 location 不在 ALL_LOCATIONS，忽略
            if location in day_location_map[day_int]:
                day_location_map[day_int][location] += count

        # 4) 构建返回的 xAxis 和 series
        # xAxis: 确保输出从第 0 天到 maxDay 的连续天数
        xAxis = [str(d) for d in range(start_day, end_day + 1)]

        # series: [{"name": 地点, "data": [每天数据]}]
        series = []
        for location in ALL_LOCATIONS:
            data = [
                day_location_map[day].get(location, 0)
                for day in range(start_day, end_day + 1)
            ]
            series.append({"name": location, "data": data})

        # 5) 返回结果
        return {"xAxis": xAxis, "series": series}

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
        image=None,
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
            "image": image,  # 新增字段
        }
        # 插入文档
        inserted_id = self.db_utils.insert_document(
            config.agent_profile_collection_name, document
        )
        return inserted_id

    def get_character(self, characterId=None, k=None):
        query = {}
        if characterId is not None:
            query["characterId"] = characterId

        documents = self.db_utils.find_documents(
            collection_name=config.agent_profile_collection_name,
            query=query,
        )

        # 如果k不为None，则限制返回的文档数量
        if k is not None:
            documents = documents[:k]

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
        # 如果没有找到文档，返回默认值
        if not documents:
            documents = [
                {
                    "characterId": characterId,
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
                    "is_store": False,
                }
            ]

        # 添加固定内容到每个文档
        fixed_content = {
            "randomness": True,
            "tool_functions": [
                "1. goto [placeName:string]: Go to a specified location.",
                "2. pickapple [number:int]: Pick an apple, costing energy.",
                "3. gofishing [hours:int]: Fish for fish, costing energy.",
                "4. gomining [hours:int]: Mine for ore, costing energy.",
                "5. harvest [hours:int]: Harvest crops, costing energy.",
                "6. buy [itemType:string] [amount:int]: Purchase items, costing money.",
                "7. sell [itemType:string] [amount:int]: Sell items for money. The ONLY way to get money.",
                "8. sleep [hours:int]: Sleep to recover energy and health.",
                "9. study [hours:int]: Study to achieve a higher degree, will cost money.",
            ],
            "restrictions": [
                "1. goto [placeName:string]: Must be in (school,workshop,home,farm,mall,square,hospital,fruit,harvest,fishing,mine,orchard).",
                "2. pickapple [number:int]: Must have enough energy and be in the orchard.",
                "3. gofishing [hours:int]: Must have enough energy and be in the fishing area.",
                "4. gomining [hours:int]: Must have enough energy and be in the mine.",
                "5. harvest [hours:int]: Must have enough energy and be in the harvest area.",
                "6. buy [itemType:string] [amount:int]: Must have enough money, and items must be available in sufficient quantity in the AMM. ItemType:(ore,bread,apple,wheat,fish)",
                "7. sell [itemType:string] [amount:int]: Must have enough items in inventory. ItemType:(ore,bread,apple,wheat,fish)",
                "8. sleep [hours:int]: Must be at home.",
                "9. study [hours:int]: Must be in school and have enough money.",
            ],
            "available_locations": [
                "1. school",
                "2. workshop",
                "3. home",
                "4. farm",
                "5. mall",
                "6. square",
                "7. hospital",
                "8. fruit",
                "9. harvest",
                "10. fishing",
                "11. mine",
                "12. orchard",
            ],
        }

        for document in documents:
            document.update(fixed_content)

        return documents

    def update_agent_prompt(self, characterId, update_fields):
        query = {"characterId": characterId}

        # 检查是否存在文档
        existing_documents = self.db_utils.find_documents(
            collection_name=config.agent_prompt_collection_name,
            query=query,
        )

        # 如果没有找到文档，先插入默认值
        if not existing_documents:
            default_document = {
                "characterId": characterId,
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
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.db_utils.insert_document(
                config.agent_prompt_collection_name, default_document
            )

        # 更新文档
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
        # 如果没有找到文档，设置默认值
        if not documents:
            documents = [
                {
                    "topic_requirements": "",
                    "relation": "",
                    "emotion": "You are happy.",
                    "personality": "Introversion",
                    "habits_and_preferences": "",
                    "is_store": False,
                }
            ]
        # 添加固定内容到每个文档
        fixed_content = {
            "topic_factor": "The topics should be related to the daily objectives, your current personality and profile.",
            "casual_topic": "Randomly add at most one casual topics. Try to combine the casual topic with the profile and personality. The casual topics could be, for example, weather, food, emotion, clothing, health condition, education, product prize.",
            "critical_topic": "Randomly discuss seriously or criticize others on at most one topic. The topic can be determined by your profile and personality. For example, discuss on others' lifestyle, emotion, habit, education, taste or attitidue towards certain event.",
            "start_check": "First summarize the topics of finished conversations. Then if you have talked about the same topic with the same person, you should not start this conversation.",
            "should_end": "Based on your profile, personality, the impression and the conversation history, determine whether the conversation shoud end. The relation in impression can influence the overall round of the conversation. For example, if two speakers are close friends, they may talk more rounds. If they are in bad relation, the conversation may end very soon.",
            "intimacy_mark": "The intimacy mark should be an integer ranging from -2 to 2. There are five levels with different marks: Very friendly and close is 2. Positive and polite, but not so close is 1. Neutral is 0. A bit negative is -1. Hate each other, about to quarrel is -2.",
            "impression_update": "Update impression, which contain four items: relation, emotion, personality, habits and preferences. In each item also include a brief description. Relation is the way other agent treates you. Emotion is decided by others tone. Personality is based on openness to experience, conscientiousness, extraversion, agreeableness, and neuroticism.habits and preferences are the other player's habit and taste. Also include things he dislike.",
        }

        for document in documents:
            document.update(fixed_content)

        return documents

    def update_conversation_prompt(self, characterId, update_fields):
        query = {"characterId": characterId}

        # 检查是否存在文档
        existing_documents = self.db_utils.find_documents(
            collection_name=config.conversation_prompt_collection_name,
            query=query,
        )

        # 如果没有找到文档，先插入默认值
        if not existing_documents:
            default_document = {
                "characterId": characterId,
                "topic_requirements": "",
                "relation": "",
                "emotion": "You are happy.",
                "personality": "Introversion",
                "habits_and_preferences": "",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.db_utils.insert_document(
                config.conversation_prompt_collection_name, default_document
            )

        # 更新文档
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

    def store_conversation(
        self,
        from_id,
        to_id,
        start_time,
        start_day,
        message,
        send_gametime,
        send_realtime,
    ):
        document = {
            "from_id": from_id,
            "to_id": to_id,
            "start_time": start_time,
            "start_day": start_day,
            "message": message,
            "send_gametime": send_gametime,
            "send_realtime": send_realtime,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.conversation_collection_name, document
        )
        return inserted_id

    def get_conversation(
        self,
        from_id=None,
        to_id=None,
        k=None,
        start_day=None,
        start_time=None,
        characterId=None,
    ):
        query = {}

        # 根据提供的参数构建查询条件
        if from_id is not None:
            query["from_id"] = from_id

        if to_id is not None:
            query["to_id"] = to_id

        if start_day is not None:
            query["start_day"] = start_day

        if start_time is not None:
            query["start_time"] = start_time

        if characterId is not None:
            query["$or"] = [{"from_id": characterId}, {"to_id": characterId}]

        # 执行查询
        documents = self.db_utils.find_documents(
            collection_name=config.conversation_collection_name,
            query=query,
            limit=k if k is not None else 0,  # 如果 k 为 None，则不限制数量
            sort=[("created_at", DESCENDING)] if k is not None else None,
        )
        return documents

    def get_conversation_by_list(self, characterIds, time=None, k=None):
        query = {
            "$or": [
                {"from_id": characterIds[0], "to_id": characterIds[1]},
                {"from_id": characterIds[1], "to_id": characterIds[0]},
            ]
        }
        if time is not None:
            query["send_realtime"] = {"$gt": time}  # 查询在指定时间之后的记录
        # 执行查询
        documents = self.db_utils.find_documents(
            collection_name=config.conversation_collection_name,
            query=query,
            limit=k if k is not None else 0,  # 如果 k 为 None，则不限制数量
            sort=[("send_realtime", DESCENDING)],  # 按创建时间降序排列
        )
        return documents

    def store_conversation_memory(
        self, characterId, day, topic_plan=None, time_list=None, started=None
    ):
        # 确保默认值为列表而不是 None
        topic_plan = topic_plan if topic_plan is not None else []
        time_list = time_list if time_list is not None else []
        started = started if started is not None else []

        document = {
            "characterId": characterId,
            "day": day,
            "topic_plan": topic_plan,
            "time_list": time_list,
            "started": started,
        }
        inserted_id = self.db_utils.insert_document(
            config.conversation_memory_collection_name, document
        )
        return inserted_id

    def get_conversation_memory(self, characterId, day=None):
        query = {"characterId": characterId}
        if day is not None:
            query["day"] = day

        documents = self.db_utils.find_documents(
            collection_name=config.conversation_memory_collection_name,
            query=query,
        )
        # 如果没有找到文档，返回默认值
        if not documents:
            return [
                {
                    "characterId": characterId,
                    "day": day,
                    "topic_plan": [],
                    "time_list": [],
                    "started": [],
                    "is_store": False,
                }
            ]

        return documents

    def get_memory(self, characterId, day, count=1):
        # 获取 conversation_memory
        conversation_memory = self.get_conversation_memory(characterId, day)
        if conversation_memory:
            conversation_memory = conversation_memory[0]  # 只获取第一个
        else:
            conversation_memory = {}

        # 获取 decision
        decision = self.get_decision(characterId, count)
        if decision:
            decision = decision[0]  # 只获取第一个
        else:
            decision = {}

        # 合并两个字典
        combined_memory = {**conversation_memory, **decision}

        return combined_memory

    def update_conversation_memory(
        self, characterId, day, update_fields=None, add_started=None
    ):
        # 确保 update_fields 和 add_started 不能同时存在
        if update_fields is not None and add_started is not None:
            raise ValueError("只能提供 update_fields 或 add_started 中的一个。")
        # 构建查询条件
        query = {"characterId": characterId, "day": day}
        # 检查是否存在文档
        existing_documents = self.db_utils.find_documents(
            collection_name=config.conversation_memory_collection_name,
            query=query,
        )
        # 如果没有找到文档，先插入默认值
        if not existing_documents:
            default_document = {
                "characterId": characterId,
                "day": day,
                "topic_plan": [],
                "time_list": [],
                "started": [],
            }
            self.db_utils.insert_document(
                config.conversation_memory_collection_name, default_document
            )
        # 构建更新操作
        update = {}
        if update_fields is not None:
            update = {"$set": update_fields}
        elif add_started is not None:
            update = {"$push": {"started": add_started}}
        else:
            raise ValueError("必须提供 update_fields 或 add_started。")
        # 执行更新操作
        result = self.db_utils.update_documents(
            collection_name=config.conversation_memory_collection_name,
            query=query,
            update=update,
        )
        return result

    def store_work_experience(self, characterId, jobid, start_date):
        document = {
            "characterId": characterId,
            "jobid": jobid,
            "start_date": start_date,
            "duration": 0,
            "total_work": 0,
            "total_salary": 0.0,
        }
        inserted_id = self.db_utils.insert_document(
            config.work_experience_collection_name, document
        )
        return inserted_id

    def get_all_work_experiences(self, characterId):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.work_experience_collection_name,
            query=query,
            sort=[("start_date", DESCENDING)],
        )
        return documents

    def get_current_work_experience(self, characterId):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.work_experience_collection_name,
            query=query,
            sort=[("start_date", DESCENDING)],
            limit=1,
        )
        return documents[0] if documents else None

    def update_work_experience(
        self, characterId, jobid, additional_work, additional_salary
    ):
        query = {"characterId": characterId, "jobid": jobid}
        update_data = {
            "$inc": {
                "total_work": additional_work,
                "total_salary": additional_salary,
            }
        }
        result = self.db_utils.update_documents(
            collection_name=config.work_experience_collection_name,
            query=query,
            update=update_data,
            upsert=False,
            multi=False,
        )
        return result

    def store_character_arc(
        self,
        characterId,
        belief=None,
        mood=None,
        values=None,
        habits=None,
        personality=None,
    ):
        document = {
            "characterId": characterId,
            "belief": belief,
            "mood": mood,
            "values": values,
            "habits": habits,
            "personality": personality,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        inserted_id = self.db_utils.insert_document(
            config.character_arc_collection_name, document
        )
        return inserted_id

    def get_character_arc(self, characterId, k=None):
        query = {"characterId": characterId}
        documents = self.db_utils.find_documents(
            collection_name=config.character_arc_collection_name,
            query=query,
            sort=[("created_at", DESCENDING)],  # 按创建时间降序排列
            limit=k if k is not None else 0,  # 如果 k 为 None，则不限制数量
        )
        return documents


if __name__ == "__main__":
    db_utils = MongoDBUtils()
    queries = DomainSpecificQueries(db_utils=db_utils)

if __name__ == "__main__":
    db_utils = MongoDBUtils()
    queries = DomainSpecificQueries(db_utils=db_utils)

    # # 插入测试数据
    # print("插入测试数据...")
    # sample_data = [
    #     {"characterId": "1", "location": "hospital", "gameTime": "1:08:15"},
    #     {"characterId": "2", "location": "school", "gameTime": "1:09:30"},
    #     {"characterId": "3", "location": "park", "gameTime": "1:10:45"},
    #     {"characterId": "4", "location": "hospital", "gameTime": "2:08:15"},
    #     {"characterId": "5", "location": "school", "gameTime": "2:09:30"},
    #     {"characterId": "6", "location": "park", "gameTime": "2:10:45"},
    #     {"characterId": "7", "location": "hospital", "gameTime": "2:11:15"},
    #     {"characterId": "8", "location": "park", "gameTime": "3:08:15"},
    #     {"characterId": "9", "location": "school", "gameTime": "3:09:30"},
    #     {"characterId": "10", "location": "hospital", "gameTime": "3:10:45"},
    # ]

    # for record in sample_data:
    #     inserted_id = queries.store_action(
    #         record["characterId"], record["location"], record["gameTime"]
    #     )
    #     print(f"插入成功: {record} -> ID: {inserted_id}")

    # # 按天数范围测试
    # print("\n按天数范围测试 (1 <= 天数 < 3)...")
    # from_time = "1:00:00"
    # to_time = "3:00:00"
    # day_result = queries.get_action_counts_in_time_range(from_time, to_time)
    # print(f"从 {from_time} 到 {to_time} 时间范围内，各地点人数统计: {day_result}")

    # # 按小时范围测试
    # print("\n按小时范围测试 (2:08:00 <= 时间 < 2:11:00)...")
    # from_time = "2:08:00"
    # to_time = "2:11:00"
    # hour_result = queries.get_action_counts_in_time_range(from_time, to_time)
    # print(f"从 {from_time} 到 {to_time} 时间范围内，各地点人数统计: {hour_result}")

    # # 按分钟范围测试
    # print("\n按分钟范围测试 (2:09:00 <= 时间 < 2:09:59)...")
    # from_time = "2:09:00"
    # to_time = "2:09:59"
    # minute_result = queries.get_action_counts_in_time_range(from_time, to_time)
    # print(f"从 {from_time} 到 {to_time} 时间范围内，各地点人数统计: {minute_result}")

    # # 获取最近7天的统计数据
    # print(queries.get_all_action_counts())

    # # 存储角色信息
    # print("存储角色信息...")
    # characters = [
    #     {"characterId": 100, "characterName": "Jack", "gender": "Male"},
    #     {"characterId": 200, "characterName": "Bella", "gender": "Female"},
    #     {"characterId": 300, "characterName": "Mark", "gender": "Male"},
    #     {"characterId": 400, "characterName": "Jelly", "gender": "Female"},
    # ]

    # for char in characters:
    #     inserted_id = queries.store_character(
    #         characterId=char["characterId"],
    #         characterName=char["characterName"],
    #         gender=char["gender"]
    #     )
    #     print(f"插入成功，角色 ID：{inserted_id}")

    # 测试 get_k

    # 插入数据：亲密度为 50，relationship 由系统自动计算
    print("插入数据...")
    inserted_id_1_2 = queries.store_intimacy(1, 2, intimacy_level=50)
    print(f"插入成功，文档 ID：{inserted_id_1_2}")

    queries.store_intimacy(2, 1, intimacy_level=10)

    # 再插入一些测试数据，方便观察关联结果
    inserted_id_1_3 = queries.store_intimacy(1, 3, intimacy_level=60)
    inserted_id_2_3 = queries.store_intimacy(2, 3, intimacy_level=70)
    queries.store_intimacy(3, 2, intimacy_level=20)
    inserted_id_2_4 = queries.store_intimacy(2, 4, intimacy_level=40)
    print("插入了额外测试数据")

    # 测试 get_knowledge_graph_data 方法
    print("测试 get_knowledge_graph_data 方法...")
    character_id = 1  # 替换为你想测试的角色ID
    knowledge_graph_data = queries.get_knowledge_graph_data(character_id)
    print("知识图谱数据：", knowledge_graph_data)

    # # 测试 store_character_arc 方法
    # print("存储 character_arc...")
    # characterId = 1
    # belief = "Believe in teamwork"
    # mood = "Happy"
    # values = "Honesty, Integrity"
    # habits = "Reading, Jogging"
    # personality = "Introverted"

    # inserted_id = queries.store_character_arc(
    #     characterId=characterId,
    #     belief=belief,
    #     mood=mood,
    #     values=values,
    #     habits=habits,
    #     personality=personality,
    # )
    # print(f"插入成功，文档 ID：{inserted_id}")

    # # 测试 get_character_arc 方法
    # print("\n获取 character_arc...")
    # k = 3  # 获取最新的3个文档
    # character_arcs = queries.get_character_arc(characterId=characterId, k=k)
    # print(f"获取的 character_arc 文档：{character_arcs}")

    # # 测试 get_conversation_by_list 方法
    # print("测试 get_conversation_by_list 方法...")
    # characterIds = [1, 2]  # 示例角色ID
    # time = "2023-10-01 12:00:00"  # 示例时间
    # conversations = queries.get_conversation_by_list(characterIds, time=time, k=5)
    # #    conversations = queries.get_conversation_by_list(character_ids, k=5)
    # #    conversations = queries.get_conversation_by_list(character_ids)
    # print(f"角色 {characterIds} 的对话记录：", conversations)

#     # 测试 get_conversation 函数
#    print("测试 get_conversation 函数...")
#    from_id = 1
#    conversations = queries.get_conversation(from_id=from_id)
#    print(f"从 ID 为 {from_id} 的对话记录：", conversations)

# # 测试 get_memory 函数
# print("测试 get_memory 函数...")
# characterId = 1
# day = 1
# count = 1

# # 假设已经有一些数据存储在数据库中
# combined_memory = queries.get_memory(characterId, day, count)
# print("合并后的 memory 数据：", combined_memory)

# # 测试存储多条工作经历
# print("存储多条工作经历...")
# characterId = 1
# job_entries = [
#     {"jobid": 101, "start_date": 20231001},
#     {"jobid": 102, "start_date": 20231101},
#     {"jobid": 103, "start_date": 20231201},
# ]

# for entry in job_entries:
#     inserted_id = queries.store_work_experience(
#         characterId, entry["jobid"], entry["start_date"]
#     )
#     print(f"插入成功，文档 ID：{inserted_id}")

# # 测试获取所有工作经历
# print("\n获取所有工作经历...")
# all_work_experiences = queries.get_all_work_experiences(characterId)
# print("所有工作经历：", all_work_experiences)

# # 测试获取当前工作经历
# print("\n获取当前工作经历...")
# current_work_experience = queries.get_current_work_experience(characterId)
# print("当前工作经历：", current_work_experience)

# # 测试更新当前工作经历
# print("\n更新当前工作经历...")
# if current_work_experience:
#     jobid = current_work_experience["jobid"]
#     additional_work = 8
#     additional_salary = 1500.0
#     update_result = queries.update_work_experience(
#         characterId, jobid, additional_work, additional_salary
#     )
#     print(f"更新成功，修改了 {update_result} 个文档。")

#     # 再次获取当前工作经历以验证更新
#     print("\n更新后的当前工作经历...")
#     updated_current_work_experience = queries.get_current_work_experience(
#         characterId
#     )
#     print("更新后的当前工作经历：", updated_current_work_experience)
# else:
#     print("没有找到当前工作经历进行更新。")

# # 测试存储 memory
# print("存储 memory...")
# characterId = 1
# day = 1
# topic_plan = [
#     "Talk about weather",
#     "Talk about food",
#     "Talk about clothing",
#     "Are you happy",
#     "How to study",
# ]
# time_list = ["09:00", "12:00", "15:00"]
# # started = [{"topic": "Talk about weather", "time": "10:00"}]
# # inserted_id = queries.store_memory(characterId, day, topic_plan, time_list, started)
# inserted_id = queries.store_conversation_memory(
#     characterId, day, topic_plan, time_list
# )
# print(f"插入成功，文档 ID：{inserted_id}")

# # 测试获取 memory
# print("\n获取 memory...")
# documents = queries.get_conversation_memory(characterId, day)
# print("获取的 memory 文档：", documents)

# # 测试更新 memory
# print("\n更新 memory...")
# # update_fields = {"topic_plan": ["更新后的计划讨论主题"]}
# add_started = {"topic": "Talk about weather", "time": "10:00"}
# update_result = queries.update_conversation_memory(
#     characterId, day, add_started=add_started
# )
# # update_result = queries.update_memory(characterId, day, update_fields)
# print(f"更新成功，修改了 {update_result} 个文档。")

# # 再次获取以验证更新
# print("\n更新后的 memory...")
# updated_documents = queries.get_conversation_memory(characterId, day)
# print("更新后的 memory 文档：", updated_documents)

# # 测试存储 current_pointer
# print("存储 current_pointer...")
# characterId = 1
# current_pointer = "pointer_1"
# inserted_id = queries.store_current_pointer(characterId, current_pointer)
# print(f"插入成功，文档 ID：{inserted_id}")

# # 测试获取 current_pointer
# print("\n获取 current_pointer...")
# documents = queries.get_current_pointer(characterId)
# print("获取的 current_pointer 文档：", documents)

# # 测试更新 current_pointer
# print("\n更新 current_pointer...")
# new_pointer = "pointer_2"
# update_result = queries.update_current_pointer(characterId, new_pointer)
# print(f"更新成功，修改了 {update_result} 个文档。")

# # 再次获取以验证更新
# print("\n更新后的 current_pointer...")
# updated_documents = queries.get_current_pointer(characterId)
# print("更新后的 current_pointer 文档：", updated_documents)

# # 测试删除 current_pointer
# print("\n删除 current_pointer...")
# delete_result = queries.delete_current_pointer(characterId)
# print(f"删除成功，删除了 {delete_result} 个文档。")

# # 验证删除
# print("\n验证删除后的 current_pointer...")
# deleted_documents = queries.get_current_pointer(characterId)
# print("删除后的 current_pointer 文档：", deleted_documents)

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
#     habits_and_preferences="Likes to talk about technology",
# )
# print(f"插入成功，文档 ID：{inserted_id}")

# # 测试 get_conversation_prompt 方法
# print("\n获取对话提示...")
# conversation_prompts = queries.get_conversation_prompt(characterId=1000)
# print("获取的对话提示：", conversation_prompts)

# # 测试 update_conversation_prompt 方法
# print("\n更新对话提示...")
# update_result = queries.update_conversation_prompt(
#     characterId=1111,
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
