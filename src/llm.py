from langchain_ollama import ChatOllama


def get_llm():
    return ChatOllama(
        model="qwen3.5:9b",
        reasoning=False
    )