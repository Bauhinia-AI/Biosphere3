from create_vector_embeddings import create_embeddings
from save_to_atlas import save_to_mongo
from create_vector_index import create_vector_search_index
from mongo_utils import connect_to_mongo
import config
import time
from loguru import logger

# Import validators from validators.py
from schema import validators

# 设置日志
logger.add("logs/db/create_database.log")

SURE_DELELE = False
class ValidatorFactory:
    @staticmethod
    def get_validator(collection_type):
        if collection_type in validators:
            return validators[collection_type]
        else:
            raise ValueError(f"Unknown collection type: {collection_type}")


class DatabaseSetupApp:
    def setup_database(self, collection_type, collection_name, data_processing_func=None):
        validator = ValidatorFactory.get_validator(collection_type)

        # Connect to MongoDB collection
        db = connect_to_mongo(
            db_name=config.db_name,
            mongo_uri=config.mongo_uri,
        )
        if SURE_DELELE:
            # Delete existing collection
            collection = db[collection_name]
            collection.drop()
            logger.info(f"Collection '{collection_name}' deleted.")

        # Create new collection with validator
        db.create_collection(collection_name, validator=validator)
        logger.info(f"Collection '{collection_name}' created with validator.")

        # If additional steps are needed, such as loading data, embeddings, etc.
        if data_processing_func is not None:
            data_processing_func(db, collection_name)


def process_cv_data(db, collection_name):
    # CV_df = load_and_prepare_data("CV.json")
    # logger.info("CV Data loaded and prepared.")
    # print(CV_df.head())

    # save_to_mongo(
    #     CV_df, config.db_name, collection_name, config.mongo_uri
    # )
    # print("CV Data saved to MongoDB Atlas.")
    pass


def process_tool_data(db, collection_name):
    collection = db[collection_name]
    collection.drop_indexes()
    print(f"Indexes dropped for collection '{collection_name}'.")

    try:
        collection.drop_search_index(config.index_name)
        while list(collection.list_search_indexes()):
            print("Atlas is deleting the index. Waiting...")
            time.sleep(5)
        print(f"Search indexes dropped for collection '{collection_name}'.")
    except Exception:
        print("Search indexes do not exist.")

    # Load and prepare data
    # API_df = load_and_prepare_data("API.json")
    # print("API Data loaded and prepared.")

    # # Create embeddings
    # API_df = create_embeddings(
    #     API_df,
    #     "text",
    #     config.model_name,
    #     config.base_url,
    #     config.api_key,
    # )
    # print(API_df.head())
    print("API Embeddings created.")

    # Save embeddings to MongoDB Atlas
    # save_to_mongo(
    #     API_df, config.db_name, collection_name, config.mongo_uri
    # )
    print("API Embeddings saved to MongoDB Atlas.")

    # Create vector search index
    create_vector_search_index(
        config.db_name,
        collection_name,
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
    # Setup CV database
    #app.setup_database('cv', config.cv_collection_name, data_processing_func=process_cv_data)
    # Setup NPC database
    app.setup_database('npc', config.npc_collection_name)
    # Setup Action database
    #app.setup_database('action', config.action_collection_name)
    # Setup Tool database with additional processing
    #app.setup_database('tool', config.tool_collection_name, data_processing_func=process_tool_data)