# db/embeddings.py
from langchain.embeddings import HuggingFaceEmbeddings

class MiniLMEmbedder:
    def __init__(self):
        # all-MiniLM embeddings
        self.embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def embed_text(self, text: str):
        """Return embedding vector for a single string"""
        return self.embedder.embed_query(text)

    def embed_texts(self, texts: list[str]):
        """Return embedding vectors for a list of strings"""
        return self.embedder.embed_documents(texts)
