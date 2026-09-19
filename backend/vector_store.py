import chromadb
from embedding import model
import uuid

client = chromadb.PersistentClient(path="../data/chroma_db")

collection = client.get_or_create_collection(name="documents")

def add_documents(chunks, embeddings, document_id):
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings,
    metadatas=[
        {"document_id": document_id}
        for _ in chunks
    ]
)
    return len(chunks)

def search_documents(query, document_id, n_results=3):
    query_embedding = model.encode([query])

    results = collection.query(
    query_embeddings=query_embedding.tolist(),
    n_results=n_results,
    where={"document_id": document_id}
    )

    return results["documents"][0]