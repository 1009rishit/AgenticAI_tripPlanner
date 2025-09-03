# db/memory_store.py
import redis
import json

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def add_memory(session_id: str, doc_id: str, text: str, metadata: dict, ttl: int = 3600):
    """Store memory for a specific session in Redis with TTL (auto-delete)."""
    key = f"{session_id}:{doc_id}"
    data = {
        "text": text,
        "metadata": metadata
    }
    r.setex(key, ttl, json.dumps(data))  # auto-delete after ttl
    r.lpush(f"{session_id}:memories", key)
    r.expire(f"{session_id}:memories", ttl)  # expire the list too




def query_memory(session_id: str, top_k: int = 3):
    """Retrieve last `top_k` memories for a session."""
    doc_ids = r.lrange(f"{session_id}:memories", 0, top_k - 1)
    documents, metadatas = [], []

    for doc_id in doc_ids:
        raw = r.get(doc_id)
        if raw:
            data = json.loads(raw)
            documents.append(data["text"])
            metadatas.append(data["metadata"])

    return {"documents": [documents], "metadatas": [metadatas]}

def clear_session(session_id: str):
    """Delete all memory for a session manually."""
    doc_ids = r.lrange(f"{session_id}:memories", 0, -1)
    for doc_id in doc_ids:
        r.delete(doc_id)
    r.delete(f"{session_id}:memories")

