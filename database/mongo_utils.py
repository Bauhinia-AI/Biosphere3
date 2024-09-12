from pymongo import MongoClient
from . import config


def connect_to_mongo(db_name, collection_name, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection


def get_candidates_from_mongo():
    collection = connect_to_mongo(
        db_name=config.db_name,
        collection_name=config.cv_collection_name,
        mongo_uri=config.mongo_uri,
    )
    candidates = list(
        collection.find({}, {"_id": 0, "jobid": 1, "username": 1, "userid": 1})
    )
    return candidates
