import datetime
from pymongo import MongoClient
import sys
import os
from pprint import pprint

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import config


def connect_to_mongo(db_name, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db


def print_collection(collection_name):
    # Connect to the MongoDB collection
    db = connect_to_mongo(
        db_name=config.db_name,
        mongo_uri=config.mongo_uri,
    )
    collection = db[collection_name]

    # Find all documents in the collection
    documents = collection.find()

    # Print each document
    for document in documents:
        pprint(document)
        print()  # Print an empty line for separation


def get_candidates_from_mongo():
    # Connect to the MongoDB collection
    db = connect_to_mongo(
        db_name=config.db_name,
        mongo_uri=config.mongo_uri,
    )
    collection = db[config.cv_collection_name]

    # Calculate the date one week ago from now
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

    # Query to find candidates created within the last week
    candidates = list(
        collection.find(
            {"created_at": {"$gte": one_week_ago.strftime("%Y-%m-%d %H:%M:%S")}},
            {"_id": 0, "jobid": 1, "username": 1, "userid": 1},
        )
    )
    return candidates


def update_document(collection_name, query, update):
    # Connect to the MongoDB collection
    db = connect_to_mongo(
        db_name=config.db_name,
        mongo_uri=config.mongo_uri,
    )
    collection = db[collection_name]

    # Update the document that matches the query
    result = collection.update_one(query, update)

    return result.modified_count


if __name__ == "__main__":

    # 获取候选人
    print(get_candidates_from_mongo())

    # 更新 npc 集合中 userid 为 0 的文档的 stats.health 字段
    modified_count = update_document(
        config.npc_collection_name, {"userid": 0}, {"$set": {"stats.health": 8.5}}
    )
    print(f"Updated {modified_count} document(s)")
    print_collection(config.npc_collection_name)

    # 更新 cv 集合中 username 为 "Vitalik Buterin" 的文档的 CV_content 字段
    modified_count = update_document(
        config.cv_collection_name,
        {"username": "Vitalik Buterin"},
        {"$set": {"CV_content": "Updated CV content"}},
    )
    print(f"Updated {modified_count} document(s)")
    print_collection(config.cv_collection_name)
