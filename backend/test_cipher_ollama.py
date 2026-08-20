from ollama_agent import answer_question

result = answer_question(
    "Find phenotypes related to diabetes"
)

print("\nACTION:")
print(result["action"])

print("\nANSWER:")
print(result["answer"])