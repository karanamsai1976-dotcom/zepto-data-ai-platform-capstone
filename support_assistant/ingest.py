"""Chunk the policy corpus, embed it, and store it in ChromaDB. Idempotent --
re-running this does not create duplicate chunks."""

import chromadb
from sentence_transformers import SentenceTransformer

from support_assistant.config import (
    CHROMA_PERSIST_DIR, COLLECTION_NAME, DOCS_DIR, EMBEDDING_MODEL_NAME, TOP_K,
)


def load_documents():
    """Each of the 8 short policy files is treated as a single chunk -- they
    are already paragraph-sized, so no further splitting is needed.
    utf-8-sig strips a leading BOM if present (PowerShell's Out-File -Encoding
    utf8 writes one); harmless if the file has no BOM."""
    documents = []
    for path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = path.read_text(encoding="utf-8-sig").strip()
        doc_id = path.stem  # e.g. "doc_01"
        documents.append({"id": f"{doc_id}#0", "text": text, "doc_id": doc_id})
    return documents


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def ingest():
    collection = get_collection()
    documents = load_documents()

    if collection.count() >= len(documents):
        print(f"Collection already has {collection.count()} chunks -- skipping ingestion.")
        return collection

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    embeddings = model.encode([d["text"] for d in documents]).tolist()

    collection.add(
        ids=[d["id"] for d in documents],
        embeddings=embeddings,
        documents=[d["text"] for d in documents],
        metadatas=[{"doc_id": d["doc_id"]} for d in documents],
    )
    print(f"Ingested {len(documents)} chunks into '{COLLECTION_NAME}'.")
    return collection


def retrieve(query, top_k=TOP_K):
    collection = get_collection()
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_embedding = model.encode([query]).tolist()

    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    return results


if __name__ == "__main__":
    collection = ingest()
    print(f"\nCollection count: {collection.count()}")

    print("\nTest query: 'delivery fee'")
    results = retrieve("delivery fee")
    for doc_id, distance, text in zip(
        results["ids"][0], results["distances"][0], results["documents"][0]
    ):
        print(f"  {doc_id} (distance={distance:.4f}): {text[:80]}...")
