"""See how the following FastAPI app behaves under load and correct the behaviour if not optimal
o	You have the following fast api application in app.py
"""

"""
- uvicorn app:app –port 8001
- python loadtest.py hhttp://localhost:8001/ask 20
- curl -s localhost:8001/ask -H ‘content-type: application/json’\
-  -d ‘{“text”:”what is the refund policy”}’
"""
from fastapi import FastAPI
from pydantic import BaseModel
import time
import hashlib
import numpy as np

app = FastAPI()

K = 15  # bumped from 5 last week

DIM = 64
_EMBED_LATENCY_S = 0.05
_LLM_LATENCY_S = 0.50


class Question(BaseModel):
    text: str


def _deterministic_vec(text: str) -> np.ndarray:
    # Stable pseudo-embedding: same text -> same vector.
    h = hashlib.sha256(text.encode()).digest()
    seed = int.from_bytes(h[:8], "big")
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(DIM).astype(np.float32)
    v /= np.linalg.norm(v) + 1e-9
    return v


def embed(text: str) -> np.ndarray:
    time.sleep(_EMBED_LATENCY_S)
    return _deterministic_vec(text)


def llm(prompt: str, n_context_chunks: int) -> str:
    time.sleep(_LLM_LATENCY_S)
    return (
        f"[answer generated from {n_context_chunks} context chunks; "
        f"prompt was {len(prompt)} chars]"
    )


class VectorStore:
    def __init__(self, n_docs: int = 5000):
        rng = np.random.default_rng(0)
        self._emb = rng.standard_normal((n_docs, DIM)).astype(np.float32)
        self._emb /= np.linalg.norm(self._emb, axis=1, keepdims=True) + 1e-9
        self._chunks = [
            f"policy-doc#{i}: lorem ipsum dolor sit amet ..." for i in range(n_docs)
        ]

    def search(self, query_vec: np.ndarray, k: int):
        # cosine similarity (vectors normalized) -> top-k
        sims = self._emb @ query_vec
        idx = np.argsort(-sims)[:k]
        return [(float(sims[i]), self._chunks[i]) for i in idx]


STORE = VectorStore()


@app.post("/ask")
async def ask(q: Question):
    emb = embed(q.text)  # blocking network call
    rows = STORE.search(emb, K)  # pgvector: ORDER BY embedding <-> q LIMIT 15
    context = "\n".join(chunk for _score, chunk in rows)
    prompt = f"Answer the question.\nQuestion: {q.text}\nContext:\n{context}"
    answer = llm(prompt, n_context_chunks=len(rows))  # blocking network call
    return {"answer": answer, "k": K}
