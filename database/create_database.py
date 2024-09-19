from load_dataset import load_and_prepare_data
from create_vector_embeddings import create_embeddings
from save_to_atlas import save_to_mongo
from create_vector_index import create_vector_search_index
from mongo_utils import connect_to_mongo
import config
import time


class DatabaseSetupApp:
    def setup_cv_database(self):
        # Connect to MongoDB collection
        db = connect_to_mongo(
            db_name=config.db_name,
            mongo_uri=config.mongo_uri,
        )

        # 删除现有集合
        collection = db[config.cv_collection_name]
        collection.drop()
        print(f"Collection '{config.cv_collection_name}' deleted.")

        # 新建集合
        collection_name = config.cv_collection_name
        # 创建验证器
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["jobid", "userid", "username", "CV_content", "created_at"],
                "properties": {
                    "jobid": {
                        "bsonType": "int",
                        "description": "工作ID,必须为整数且为必填项",
                    },
                    "userid": {
                        "bsonType": "int",
                        "description": "用户ID,必须为整数且为必填项",
                    },
                    "username": {
                        "bsonType": "string",
                        "description": "用户名,必须为字符串且为必填项",
                    },
                    "CV_content": {
                        "bsonType": "string",
                        "description": "简历内容,必须为字符串且为必填项",
                    },
                    "created_at": {
                        "bsonType": "string",
                        "description": "创建时间,必须为字符串且为必填项",
                    },
                },
            }
        }
        # 创建带有验证器的集合
        db.create_collection(collection_name, validator=validator)
        CV_df = load_and_prepare_data("CV.json")
        print("CV Data loaded and prepared.")
        print(CV_df.head())

        save_to_mongo(
            CV_df, config.db_name, config.cv_collection_name, config.mongo_uri
        )
        print("CV Data saved to MongoDB Atlas.")

    def setup_npc_database(self):
        # Connect to MongoDB collection
        db = connect_to_mongo(
            db_name=config.db_name,
            mongo_uri=config.mongo_uri,
        )

        # 删除现有集合
        collection = db[config.npc_collection_name]
        collection.drop()
        print(f"Collection '{config.npc_collection_name}' deleted.")

        # 新建集合
        collection_name = config.npc_collection_name
        # 创建验证器
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "userid",
                    "username",
                    "gender",
                    "slogan",
                    "description",
                    "stats",
                    "role",
                    "task",
                    "created_at",
                ],
                "properties": {
                    "userid": {
                        "bsonType": "int",
                        "description": "NPC ID,必须为整数且为必填项",
                    },
                    "username": {
                        "bsonType": "string",
                        "description": "NPC 名字,必须为字符串且为必填项",
                    },
                    "gender": {
                        "bsonType": "string",
                        "description": "NPC 性别,必须为字符串且为必填项",
                    },
                    "slogan": {
                        "bsonType": "string",
                        "description": "NPC 标语,必须为字符串且为必填项",
                    },
                    "description": {
                        "bsonType": "string",
                        "description": "NPC 描述,必须为字符串且为必填项",
                    },
                    "stats": {
                        "bsonType": "object",
                        "required": [
                            "health",
                            "fullness",
                            "energy",
                            "knowledge",
                            "cash",
                        ],
                        "properties": {
                            "health": {"bsonType": "double"},
                            "fullness": {"bsonType": "double"},
                            "energy": {"bsonType": "double"},
                            "knowledge": {"bsonType": "double"},
                            "cash": {"bsonType": "double"},
                        },
                    },
                    "role": {
                        "bsonType": "string",
                        "description": "NPC 角色,必须为字符串且为必填项",
                    },
                    "task": {
                        "bsonType": "string",
                        "description": "NPC 任务,必须为字符串且为必填项",
                    },
                    "created_at": {
                        "bsonType": "string",
                        "description": "创建时间,必须为字符串且为必填项",
                    },
                },
            }
        }
        # 创建带有验证器的集合
        db.create_collection(collection_name, validator=validator)

        NPC_df = load_and_prepare_data("NPC.json")
        print("NPC Data loaded and prepared.")
        print(NPC_df.head())

        save_to_mongo(
            NPC_df, config.db_name, config.npc_collection_name, config.mongo_uri
        )
        print("NPC Data saved to MongoDB Atlas.")

    def setup_action_database(self):
        # Connect to MongoDB collection
        db = connect_to_mongo(
            db_name=config.db_name,
            mongo_uri=config.mongo_uri,
        )

        # 删除现有集合
        collection = db[config.action_collection_name]
        collection.drop()
        print(f"Collection '{config.action_collection_name}' deleted.")

        # 新建集合
        collection_name = config.action_collection_name
        # 创建验证器
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "userid",
                    "timestamp",
                    "meta_action",
                    "description",
                    "response",
                    "action_id",
                ],
                "properties": {
                    "userid": {
                        "bsonType": "int",
                        "description": "NPC ID,必须为整数且为必填项",
                    },
                    "timestamp": {
                        "bsonType": "string",
                        "description": "时间戳,必须为字符串且为必填项",
                    },
                    "meta_action": {
                        "bsonType": "string",
                        "description": "当前做的动作,必须为字符串且为必填项",
                    },
                    "description": {
                        "bsonType": "string",
                        "description": "大语言模型返回的结果,必须为字符串且为必填项",
                    },
                    "response": {
                        "bsonType": "bool",
                        "description": "执行是否成功,必须为布尔类型且为必填项",
                    },
                    "action_id": {
                        "bsonType": "int",
                        "description": "唯一的动作ID,必须为整数且为必填项",
                    },
                    "prev_action": {
                        "bsonType": "int",
                        "description": "前一个动作的action_id,必须为整数且为可选项",
                    },
                },
            }
        }
        # 创建带有验证器的集合
        db.create_collection(collection_name, validator=validator)

    def setup_impression_database(self):
        # Connect to MongoDB collection
        db = connect_to_mongo(
            db_name=config.db_name,
            mongo_uri=config.mongo_uri,
        )

        # 删除现有集合
        collection = db[config.impression_collection_name]
        collection.drop()
        print(f"Collection '{config.impression_collection_name}' deleted.")

        # 新建集合
        collection_name = config.impression_collection_name
        # 创建验证器
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["from_id", "to_id", "impression"],
                "properties": {
                    "from_id": {
                        "bsonType": "int",
                        "description": "表示印象来源的 NPC 的 ID,必须为整数且为必填项",
                    },
                    "to_id": {
                        "bsonType": "int",
                        "description": "表示印象指向的 NPC 的 ID,必须为整数且为必填项",
                    },
                    "impression": {
                        "bsonType": "array",
                        "description": "印象数组,必须为对象数组且为必填项",
                        "items": {
                            "bsonType": "object",
                            "required": ["content", "timestamp"],
                            "properties": {
                                "content": {
                                    "bsonType": "string",
                                    "description": "印象内容,必须为字符串且为必填项",
                                },
                                "timestamp": {
                                    "bsonType": "string",
                                    "description": "时间戳,必须为字符串且为必填项",
                                },
                            },
                        },
                    },
                },
            }
        }
        # 创建带有验证器的集合
        db.create_collection(collection_name, validator=validator)

    def setup_descriptor_database(self):
        # Connect to MongoDB collection
        db = connect_to_mongo(
            db_name=config.db_name,
            mongo_uri=config.mongo_uri,
        )

        # 删除现有集合
        collection = db[config.descriptor_collection_name]
        collection.drop()
        print(f"Collection '{config.descriptor_collection_name}' deleted.")

        # 新建集合
        collection_name = config.descriptor_collection_name
        # 创建验证器
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["failed_action", "action_id", "userid", "reflection"],
                "properties": {
                    "failed_action": {
                        "bsonType": "string",
                        "description": "执行失败的动作,必须为字符串且为必填项",
                    },
                    "action_id": {
                        "bsonType": "int",
                        "description": "失败动作的ID,必须为整数且为必填项",
                    },
                    "userid": {
                        "bsonType": "int",
                        "description": "NPC ID,必须为整数且为必填项",
                    },
                    "reflection": {
                        "bsonType": "string",
                        "description": "动作失败后的反思,必须为字符串且为必填项",
                    },
                },
            }
        }
        # 创建带有验证器的集合
        db.create_collection(collection_name, validator=validator)

    def setup_tool_database(self):
        # Connect to MongoDB collection
        db = connect_to_mongo(
            db_name=config.db_name,
            mongo_uri=config.mongo_uri,
        )

        # 删除现有集合
        collection = db[config.tool_collection_name]
        collection.drop_indexes()
        print(f"Indexes dropped for collection '{config.tool_collection_name}'.")

        try:
            collection.drop_search_index(config.index_name)
            while list(collection.list_search_indexes()):
                print("Atlas is deleting the index. Waiting...")
                time.sleep(5)
            print(
                f"Search indexes dropped for collection '{config.tool_collection_name}'."
            )
        except Exception as e:
            print(f"Search indexes not exist.")

        # Delete existing collection
        collection.drop()
        print(f"Collection '{config.tool_collection_name}' deleted.")

        # Load and prepare data
        API_df = load_and_prepare_data("API.json")
        print("API Data loaded and prepared.")

        # Create embeddings
        API_df = create_embeddings(
            API_df,
            "text",
            config.model_name,
            config.base_url,
            config.api_key,
        )
        print(API_df.head())
        print("API Embeddings created.")

        # Save embeddings to MongoDB Atlas
        save_to_mongo(
            API_df, config.db_name, config.tool_collection_name, config.mongo_uri
        )
        print("API Embeddings saved to MongoDB Atlas.")

        # Create vector search index
        create_vector_search_index(
            config.db_name,
            config.tool_collection_name,
            config.mongo_uri,
            config.index_name,
            config.num_dimensions,
            config.similarity,
        )

        while True:
            cursor = collection.list_search_indexes()
            index_info = list(cursor)[0]

            if index_info["status"] == "READY":
                print("Vector search index is ready.")
                break
            else:
                print("Vector search index is not ready. Waiting...")
                time.sleep(5)


if __name__ == "__main__":
    app = DatabaseSetupApp()
    app.setup_cv_database()
    app.setup_npc_database()
    app.setup_action_database()
    app.setup_impression_database()
    app.setup_descriptor_database()
    app.setup_tool_database()
