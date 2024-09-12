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
        collection = connect_to_mongo(
            db_name=config.db_name,
            collection_name=config.cv_collection_name,
            mongo_uri=config.mongo_uri,
        )

        # Delete existing collection
        collection.drop()
        print(f"Collection '{config.cv_collection_name}' deleted.")

        CV_df = load_and_prepare_data("CV.json")
        print("CV Data loaded and prepared.")
        print(CV_df.head())

        save_to_mongo(
            CV_df, config.db_name, config.cv_collection_name, config.mongo_uri
        )
        print("CV Data saved to MongoDB Atlas.")

    def setup_tool_database(self):
        # Connect to MongoDB collection
        collection = connect_to_mongo(
            db_name=config.db_name,
            collection_name=config.tool_collection_name,
            mongo_uri=config.mongo_uri,
        )

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
    app.setup_tool_database()
