# database/mongo_utils.py
import sys
import os
import logging

from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from pprint import pprint

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import config
from database.utils import connect_to_mongo, embed_text
from bson import ObjectId

# Get project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create logs directory in project root
log_directory = os.path.join(project_root, "logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "database_utils.log")),
        logging.StreamHandler(),
    ],
)


class MongoDBUtils:
    def __init__(self, db_name=config.db_name):
        try:
            self.db = connect_to_mongo(db_name=db_name)
            logging.info(f"Initialized MongoDBUtils with DB '{db_name}'.")
        except Exception as e:
            logging.critical(f"Failed to initialize MongoDBUtils: {e}")
            raise

    def insert_document(self, collection_name, document):
        try:
            collection = self.db[collection_name]

            # Check if collection needs embedding
            if collection_name in config.RAG_COLLECTIONS:
                field_to_embed = config.RAG_COLLECTIONS[collection_name]
                if field_to_embed in document:
                    text = document[field_to_embed]
                    # Generate embedding vector
                    embedding = embed_text(
                        text,
                        config.model_name,
                        config.base_url,
                        config.api_key,
                    )
                    # Add embedding to document
                    document["text_embedding"] = embedding
                    logging.info(
                        f"Embedding added to document for collection '{collection_name}'."
                    )
                else:
                    logging.warning(
                        f"Field '{field_to_embed}' not found in document for embedding."
                    )

            result = collection.insert_one(document)
            logging.info(f"Document inserted with ID: {result.inserted_id}")
            return result.inserted_id
        except PyMongoError as e:
            logging.error(f"Error inserting document into '{collection_name}': {e}")
            raise
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during document insertion: {e}"
            )
            raise

    def update_documents(
        self, collection_name, query, update, upsert=False, multi=False
    ):
        try:
            collection = self.db[collection_name]
            if multi:
                result = collection.update_many(query, update, upsert=upsert)
                logging.info(
                    f"Updated {result.modified_count} documents in '{collection_name}'."
                )
            else:
                result = collection.update_one(query, update, upsert=upsert)
                logging.info(
                    f"Updated {result.modified_count} document in '{collection_name}'."
                )
            return result.modified_count
        except PyMongoError as e:
            logging.error(f"Error updating documents in '{collection_name}': {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred during document update: {e}")
            raise

    def delete_document(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(query)
            logging.info(
                f"Deleted {result.deleted_count} document from '{collection_name}'."
            )
            return result.deleted_count
        except PyMongoError as e:
            logging.error(f"Error deleting document from '{collection_name}': {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred during document deletion: {e}")
            raise

    def delete_documents(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            result = collection.delete_many(query)
            logging.info(
                f"Deleted {result.deleted_count} documents from '{collection_name}'."
            )
            return result.deleted_count
        except PyMongoError as e:
            logging.error(f"Error deleting documents from '{collection_name}': {e}")
            raise
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during documents deletion: {e}"
            )
            raise

    def find_documents(
        self,
        collection_name,
        query={},
        projection=None,
        limit=0,
        sort=None,
        include_id=False,
    ):
        try:
            collection = self.db[collection_name]
            # Exclude text_embedding field if collection is in RAG_COLLECTIONS
            if collection_name in config.RAG_COLLECTIONS:
                if projection is None:
                    projection = {}
                projection["text_embedding"] = 0

            if sort is None:
                sort = [("created_at", DESCENDING)]
            cursor = collection.find(query, projection).sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)

            # Ensure _id is converted or removed based on include_id
            documents = []
            for doc in cursor:
                if not include_id:
                    doc.pop(
                        "_id", None
                    )  # Remove _id to avoid JSON serialization issues
                documents.append(doc)

            logging.info(
                f"Retrieved {len(documents)} documents from '{collection_name}'."
            )
            return documents
        except PyMongoError as e:
            logging.error(f"Error finding documents in '{collection_name}': {e}")
            raise
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during document retrieval: {e}"
            )
            raise

    def print_collection(self, collection_name):
        try:
            collection = self.db[collection_name]
            documents = collection.find()
            for document in documents:
                pprint(document)
                print()
            logging.info(f"Printed all documents from '{collection_name}'.")
        except PyMongoError as e:
            logging.error(f"Error printing documents from '{collection_name}': {e}")
            raise
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while printing collection: {e}"
            )
            raise


if __name__ == "__main__":
    try:
        mongodbutils = MongoDBUtils()
        documents = mongodbutils.find_documents(
            collection_name=config.conversation_collection_name,
            query={"characterIds": [1, 5]},
            limit=1,
        )
        pprint(documents)
    except Exception as e:
        logging.critical(f"An error occurred in the main execution: {e}")
