from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.vector_store import collection


stored_data = collection.get(
    include=["documents", "metadatas"]
)


documents = []

for index, text in enumerate(stored_data["documents"]):
    document = {
        "text": text,
        "metadata": stored_data["metadatas"][index],
    }

    documents.append(document)


retriever = BM25Retriever(documents)


query = "How do computers learn from data?"


results = retriever.search(
    query=query,
    top_k=3,
)


print("Query:")
print(query)

print("\nBM25 Results:")

for index, result in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print("Document:", result["text"])
    print("Metadata:", result["metadata"])
    print("BM25 Score:", result["bm25_score"])