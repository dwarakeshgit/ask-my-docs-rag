from backend.app.retrieval.retriever import search_documents


query = "How do computers learn from data?"


results = search_documents(
    query=query,
    top_k=3,
)


print("Query:")
print(query)

print("\nRetrieved documents:")

for index, document in enumerate(results["documents"][0], start=1):
    print(f"\n--- Result {index} ---")
    print(document)

    metadata = results["metadatas"][0][index - 1]
    print("Metadata:", metadata)

    distance = results["distances"][0][index - 1]
    print("Distance:", distance)