from backend.app.llm.transformers_client import TransformersClient


print("Creating TransformersClient...")

client = TransformersClient(
    max_new_tokens=100
)

prompt = """
You are a document QA assistant.

Answer using only the information provided below.

Context:
Deep Learning is a type of Machine Learning that uses neural
networks with multiple layers.

Question:
What is Deep Learning?

Answer only the final answer. Do not provide reasoning.
"""

print("Generating answer...")

answer = client.generate(
    prompt=prompt,
    temperature=0.0,
)

print()
print("===== TRANSFORMERS CLIENT ANSWER =====")
print(answer)
print("===== END ANSWER =====")