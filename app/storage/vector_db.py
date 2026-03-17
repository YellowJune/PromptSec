"""Vector database integration for prompt embedding storage and similarity search."""

from typing import List, Dict, Any, Optional, Tuple

import numpy as np

from app.core.logging import logger

# In-memory vector store (can be replaced with FAISS or pgvector)
_embeddings: Dict[str, np.ndarray] = {}
_metadata: Dict[str, Dict[str, Any]] = {}


async def init_vector_db() -> None:
    """Initialize vector database."""
    logger.info("Vector DB initialized (in-memory store).")


async def store_embedding(
    prompt_id: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Store a prompt embedding with optional metadata."""
    _embeddings[prompt_id] = np.array(embedding, dtype=np.float32)
    if metadata:
        _metadata[prompt_id] = metadata


async def search_similar(
    query_embedding: List[float], top_k: int = 5
) -> List[Tuple[str, float]]:
    """Search for similar embeddings using cosine similarity."""
    if not _embeddings:
        return []

    query = np.array(query_embedding, dtype=np.float32)
    query_norm = np.linalg.norm(query)
    if query_norm == 0:
        return []

    similarities: List[Tuple[str, float]] = []
    for prompt_id, stored_emb in _embeddings.items():
        stored_norm = np.linalg.norm(stored_emb)
        if stored_norm == 0:
            continue
        cosine_sim = float(np.dot(query, stored_emb) / (query_norm * stored_norm))
        similarities.append((prompt_id, cosine_sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


async def get_embedding(prompt_id: str) -> Optional[List[float]]:
    """Retrieve a stored embedding by prompt ID."""
    if prompt_id in _embeddings:
        return _embeddings[prompt_id].tolist()
    return None
