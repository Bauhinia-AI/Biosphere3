# 设置向量搜索索引：在数据库中创建索引，以便对存储的嵌入进行高效查询

from pymongo.operations import SearchIndexModel
from mongo_utils import connect_to_mongo


def create_vector_search_index(
    db_name, collection_name, mongo_uri, index_name, num_dimensions, similarity
):
    collection = connect_to_mongo(
        db_name=db_name, collection_name=collection_name, mongo_uri=mongo_uri
    )
    search_index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": "text_embedding",  # 要为其创建索引的字段名称。
                    "numDimensions": num_dimensions,  # 在索引时和查询时强制执行的向量维数
                    "similarity": similarity,  # 用于搜索前 K 个最近邻的向量相似度函数：euclidean — 测量向量两端之间的距离；cosine — 根据向量之间的角度衡量相似度；dotProduct — 与cosine类似的度量，但考虑了向量的幅度。
                }
            ]
        },
        name=index_name,
        type="vectorSearch",
    )
    collection.create_search_index(model=search_index_model)


if __name__ == "__main__":
    db_name = "biosphere3_test"
    collection_name = "api"
    mongo_uri = "mongodb+srv://bauhiniaai:nb666@biosphere3.e1px8.mongodb.net/"
    index_name = "vector_index"
    num_dimensions = 1536
    similarity = "euclidean"

    create_vector_search_index(
        db_name, collection_name, mongo_uri, index_name, num_dimensions, similarity
    )
