# database/utils.py
import os
import pandas as pd
import json
import openai
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import time
import logging
from database import config  # Import config to access mongo_uri

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
        logging.FileHandler(os.path.join(log_directory, "utils.log")),
        logging.StreamHandler(),
    ],
)

# Create a single MongoClient instance
mongo_client = MongoClient(
    config.mongo_uri,
    maxPoolSize=100,  # Set maximum connections
    minPoolSize=10,  # Maintain minimum connections to avoid frequent reconnections
    connectTimeoutMS=30000,  # Extend connection timeout
    socketTimeoutMS=60000,  # Increase socket timeout to prevent interruption during long operations
)


def get_mongo_client():
    return mongo_client


def connect_to_mongo(db_name):
    client = get_mongo_client()
    db = client[db_name]
    return db


def load_and_prepare_data(file_path):
    """Loads and prepares data from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        df = pd.DataFrame(data)
        logging.info(f"Data loaded successfully from {file_path}.")
        return df
    except FileNotFoundError:
        logging.error(f"The file {file_path} was not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from the file {file_path}: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading data: {e}")
        raise


def save_to_mongo(df, db_name, collection_name, mongo_uri):
    """Saves a DataFrame to a MongoDB collection."""
    try:
        db = connect_to_mongo(db_name=db_name)
        collection = db[collection_name]
        documents = df.to_dict("records")
        if documents:
            collection.insert_many(documents)
            logging.info(
                f"Inserted {len(documents)} documents into '{collection_name}' collection."
            )
        else:
            logging.warning("No documents to insert.")
    except PyMongoError as e:
        logging.error(f"An error occurred while inserting documents into MongoDB: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while saving to MongoDB: {e}")
        raise


def embed_text(text, model_name, base_url, api_key):
    """Generates vector embeddings for the given text."""
    try:
        if model_name == "text-embedding-3-small":
            openai_client = openai.Client(base_url=base_url, api_key=api_key)
            response = openai_client.embeddings.create(input=[text], model=model_name)
            embeddings = response.data[0].embedding
            logging.debug("Generated embedding using OpenAI API.")
            return embeddings
        else:
            model = SentenceTransformer(model_name, trust_remote_code=True)
            embedding = model.encode(text)
            logging.debug("Generated embedding using SentenceTransformer.")
            return embedding.tolist()
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred while generating embeddings: {e}")
        raise


def embed_dataframe(df, text_column, model_name, base_url, api_key):
    """Generates vector embeddings for the given DataFrame."""
    try:
        df["text_embedding"] = df[text_column].apply(
            lambda x: embed_text(x, model_name, base_url, api_key)
        )
        logging.info("Embeddings added to DataFrame.")
        return df
    except KeyError:
        logging.error(f"Column '{text_column}' does not exist in the DataFrame.")
        raise
    except Exception as e:
        logging.error(f"An error occurred while embedding DataFrame: {e}")
        raise
