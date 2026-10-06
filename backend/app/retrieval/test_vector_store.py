from backend.app.retrieval.vector_store import collection


print("Collection name:", collection.name)
print("Current document count:", collection.count())