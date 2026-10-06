from backend.app.processing.embedder import create_embeddings
from backend.app.retrieval.vector_store import add_documents, collection


text = "Machine learning allows computers to learn from data."


embedding = create_embeddings([text])[0]


add_documents(
    ids=["test_chunk_001"],
    texts=[text],
    embeddings=[embedding],
    metadatas=[
        {
            "source": "sample.pdf",
            "page": 1,
            "file_type": "pdf",
        }
    ],
)


print("Document added successfully.")
print("Current document count:", collection.count())