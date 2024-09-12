from mongo_utils import connect_to_mongo


def save_to_mongo(df, db_name, collection_name, mongo_uri):
    collection = connect_to_mongo(
        db_name=db_name, collection_name=collection_name, mongo_uri=mongo_uri
    )
    documents = df.to_dict("records")
    collection.insert_many(documents)
    # print(list(collection.find()))
