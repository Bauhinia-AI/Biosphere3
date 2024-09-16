import datetime
from pymongo import MongoClient
import config


def connect_to_mongo(db_name, mongo_uri):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db


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


if __name__ == "__main__":
    print(get_candidates_from_mongo())
