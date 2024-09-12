from vector_search import vector_search
import config


class VectorSearchApp:
    def perform_vector_search(self, query_text):
        print(f"Performing vector search for query: '{query_text}'")

        results = vector_search(
            config.db_name,
            config.tool_collection_name,
            config.mongo_uri,
            query_text,
            config.index_name,
            config.limit,
            config.model_name,
            config.base_url,
            config.api_key,
        )
        for result in results:
            print(result)


if __name__ == "__main__":
    app = VectorSearchApp()
    app.perform_vector_search("我要换工作")
