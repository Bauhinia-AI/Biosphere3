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
    num_candidates=100,
):
    # Generate embedding for the search query
    query_embedding = get_embedding(query_text, model_name, base_url, api_key)

    # Connect to MongoDB collection
    collection = connect_to_mongo(
        db_name=db_name, collection_name=collection_name, mongo_uri=mongo_uri
    )

    # Sample vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "queryVector": query_embedding,
                "path": "text_embedding",
                "numCandidates": num_candidates,
                "limit": limit,
                "exact": False,  # 默认值为 False。False - 运行ANN搜索，近似最邻近，适合查询大型数据集，需要有numCandidates。True - 运行ENN搜索，精确最邻近，查询少于10000个文档，而不必调整要考虑的最近邻的数量。
            }
        },
        {
            "$project": {
                "_id": 0,  # 不要在结果中包含 _id 字段
                "API": 1,  # 包含 api 字段
                "text": 1,  # 包含 text 字段
                "score": {
                    "$meta": "vectorSearchScore"
                },  # 计算并返回每个结果文档与查询文本的相似度得分
            }
        },
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
    # model_name = "nomic-ai/nomic-embed-text-v1"
    model_name = "text-embedding-3-small"  # 调用OPEN AI的模型
    limit = 5
    num_dimensions = 1536
    similarity = "euclidean"

    query_text = "我要变更工作"

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
    )
    for result in results:
        print(result)
