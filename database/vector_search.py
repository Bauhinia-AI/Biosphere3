from create_vector_embeddings import get_embedding
from mongo_utils import connect_to_mongo


def vector_search(
    db_name,
    collection_name,
    mongo_uri,
    query_text,
    index_name,
    limit,
    model_name,
    base_url,
    api_key,
    fields_to_return,  # List of fields to return
    num_candidates=100,
):
    # Generate embedding for the search query
    query_embedding = get_embedding(query_text, model_name, base_url, api_key)

    # Connect to MongoDB collection
    collection = connect_to_mongo(
        db_name=db_name, collection_name=collection_name, mongo_uri=mongo_uri
    )

    # Prepare projection based on the fields to return
    projection = {field: 1 for field in fields_to_return}
    projection["_id"] = 0  # Don't return the _id field
    projection["score"] = {"$meta": "vectorSearchScore"}  # Include the similarity score

    # Sample vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "queryVector": query_embedding,
                "path": "text_embedding",
                "numCandidates": num_candidates,
                "limit": limit,
                "exact": False,  # ANN search for larger datasets
            }
        },
        {"$project": projection},  # Dynamically project the required fields
    ]

    # Execute the search
    results = collection.aggregate(pipeline)

    return results


if __name__ == "__main__":
    db_name = "biosphere3_test"
    collection_name = "api"
    mongo_uri = "mongodb+srv://bauhiniaai:nb666@biosphere3.e1px8.mongodb.net/"
    index_name = "vector_index"
    api_key = "sk-tejMSVz1e3ziu6nB0yP2wLiaCUp2jR4Jtf4uaAoXNro6YXmh"
    base_url = "https://api.aiproxy.io/v1"
    model_name = "text-embedding-3-small"  # Using OpenAI model
    limit = 5

    query_text = "我要变更工作"
    fields_to_return = ["API", "text"]  # Specify fields to return

    results = vector_search(
        db_name,
        collection_name,
        mongo_uri,
        query_text,
        index_name,
        limit,
        model_name,
        base_url,
        api_key,
        fields_to_return,
    )
    for result in results:
        print(result)
