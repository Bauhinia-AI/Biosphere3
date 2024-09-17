import os
import openai
from sentence_transformers import SentenceTransformer


def get_embedding(text, model_name, base_url, api_key):
    """Generates vector embeddings for the given text."""
    if model_name == "text-embedding-3-small":
        openai_client = openai.Client(base_url=base_url, api_key=api_key)
        embeddings = (
            openai_client.embeddings.create(input=[text], model=model_name)
            .data[0]
            .embedding
        )
        return embeddings
    else:
        model = SentenceTransformer(model_name, trust_remote_code=True)
        embedding = model.encode(text)
        return embedding.tolist()


def create_embeddings(df, text_column, model_name, base_url, api_key):
    """Generates vector embeddings for the given DataFrame."""
    if model_name == "text-embedding-3-small":
        openai_client = openai.Client(base_url=base_url, api_key=api_key)
        embeddings = openai_client.embeddings.create(
            input=df[text_column].tolist(), model=model_name
        ).data
        df["text_embedding"] = [embedding.embedding for embedding in embeddings]
    else:
        model = SentenceTransformer(model_name, trust_remote_code=True)
        embeddings = model.encode(df[text_column].tolist())
        df["text_embedding"] = embeddings.tolist()
    return df
