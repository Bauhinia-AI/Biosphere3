from pymongo import MongoClient


def connect_to_mongo(db_name, collection_name, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection
