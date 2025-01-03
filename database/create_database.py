import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.utils import (
    load_and_prepare_data,
    embed_dataframe,
    save_to_mongo,
    connect_to_mongo,
)
from database import config


import time
from pymongo.operations import SearchIndexModel
import os
from pymongo import ASCENDING
from loguru import logger

# Import validators from validators.py
from schema import validators
import logging

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
        logging.FileHandler(os.path.join(log_directory, "create_database.log")),
        logging.StreamHandler(),
    ],
)


class ValidatorFactory:
    @staticmethod
    def get_validator(collection_name):
        if collection_name in validators:
            return validators[collection_name]
        else:
            raise ValueError(f"Unknown collection name: {collection_name}")


class DatabaseSetupApp:
    def __init__(self):
        # Initialize the database connection
        self.db = connect_to_mongo(db_name=config.db_name)
        self.collections = []

    def drop_indexes(self, collection_name):
        collection = self.db[collection_name]
        collection.drop_indexes()
        print(f"Indexes dropped for collection '{collection_name}'.")

        try:
            collection.drop_search_index(config.index_name)
            while list(collection.list_search_indexes()):
                print(
                    f"Atlas is deleting the index for collection '{collection_name}'. Waiting..."
                )
                time.sleep(5)
            print(f"Search indexes dropped for collection '{collection_name}'.")
        except Exception as e:
            print(f"Search indexes do not exist for collection '{collection_name}'.")

    def delete_and_create_collection(self, collection_name):
        # Delete existing collection if it exists
        collection = self.db[collection_name]
        if collection_name in config.RAG_COLLECTIONS:
            self.drop_indexes(collection_name)
        if collection_name in self.db.list_collection_names():
            collection.drop()
            logger.info(f"Collection '{collection_name}' deleted.")
        # Create new collection with validator
        validator = ValidatorFactory.get_validator(collection_name)
        self.db.create_collection(collection_name, validator=validator)
        logger.info(f"Collection '{collection_name}' created with validator.")
        return self.db[collection_name]

    def load_and_prepare_data(self, file_name):
        # Load and prepare data from a JSON file
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(current_dir, "data", file_name)

        # 检查文件路径是否存在
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = load_and_prepare_data(file_path)
        print(f"Data from '{file_name}' loaded and prepared.")
        return df

    def create_embeddings(self, df, text_column):
        # Create embeddings and return the updated dataframe
        df = embed_dataframe(
            df,
            text_column,
            config.model_name,
            config.base_url,
            config.api_key,
        )
        print(f"Embeddings created for column '{text_column}'.")
        return df

    def create_vector_search_index(self, collection_name):
        # Create vector search index
        db = connect_to_mongo(db_name=config.db_name)
        collection = db[collection_name]
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": "text_embedding",
                        "numDimensions": config.num_dimensions,
                        "similarity": config.similarity,
                    }
                ]
            },
            name=config.index_name,
            type="vectorSearch",
        )
        collection.create_search_index(model=search_index_model)
        print(f"Vector search index created for collection '{collection_name}'.")

        # Wait until the index is ready
        while True:
            cursor = collection.list_search_indexes()
            index_info = list(cursor)[0]

            if index_info["status"] == "READY":
                print(
                    f"Vector search index is ready for collection '{collection_name}'."
                )
                break
            else:
                print(
                    f"Vector search index is not ready for collection '{collection_name}'. Waiting..."
                )
                time.sleep(5)

    def setup_database(self, collection_name, unique_index_fields=None):
        collection = self.delete_and_create_collection(collection_name)
        if unique_index_fields:
            collection.create_index(
                [(field, ASCENDING) for field in unique_index_fields], unique=True
            )
            print(
                f"Unique index created on {unique_index_fields} for collection '{collection_name}'."
            )

        if collection_name in config.RAG_COLLECTIONS:
            self.create_vector_search_index(collection_name)

    def import_data_into_collection(self, collection_name, data_file):
        # Load and prepare data
        df = self.load_and_prepare_data(data_file)
        print(df.head())
        if collection_name in config.RAG_COLLECTIONS:
            text_column = config.RAG_COLLECTIONS[collection_name]
            # Create embeddings
            df = self.create_embeddings(df, text_column)

        # Save the dataframe to MongoDB
        save_to_mongo(df, config.db_name, collection_name, config.mongo_uri)
        print(f"Data saved to MongoDB Atlas for collection '{collection_name}'.")


if __name__ == "__main__":
    app = DatabaseSetupApp()

    # # Setup collections
    # app.setup_database(config.cv_collection_name)
    # app.setup_database(
    #     config.agent_profile_collection_name, unique_index_fields=["characterId"]
    # )
    # app.setup_database(config.action_collection_name)
    # app.setup_database(config.impression_collection_name)
    app.setup_database(config.conversation_collection_name)
    app.setup_database(
        config.encounter_count_collection_name, unique_index_fields=["from_id", "to_id"]
    )
    app.setup_database(
        config.intimacy_collection_name, unique_index_fields=["from_id", "to_id"]
    )
    app.setup_database(config.knowledge_collection_name)
    app.setup_database(config.character_arc_collection_name)
    app.setup_database(config.profile_sample_collection_name)
    app.setup_database(
        config.agent_prompt_collection_name, unique_index_fields=["characterId"]
    )
    app.setup_database(
        config.conversation_prompt_collection_name, unique_index_fields=["characterId"]
    )
    app.setup_database(config.decision_collection_name)
    app.setup_database(config.current_pointer_collection_name)
    app.setup_database(config.conversation_memory_collection_name)

    # # Import data
    # app.import_data_into_collection(
    #     config.cv_collection_name,
    #     "CV.json",
    # )
    # app.import_data_into_collection(
    #     config.agent_profile_collection_name,
    #     "AGENT_PROFILE.json",
    # )
    # app.import_data_into_collection(
    #     config.conversation_collection_name,
    #     "CONVERSATION.json",
    # )
    app.import_data_into_collection(
        config.profile_sample_collection_name,
        "PROFILE_SAMPLE_en.json",
    )
