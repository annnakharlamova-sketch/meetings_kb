from vectorstore import get_vectorstore
from llm import get_llm
from filters import parse_filter

def main():
    vectorstore = get_vectorstore()
    llm = get_llm()

    while True:
        question = input("\nВаш вопрос: ")

        metadata_filter = parse_filter(question)

        if question.lower() in ["exit", "quit"]:
            break

        if metadata_filter:

            results = vectorstore.similarity_search_with_score(
                question,
                k=5,
                filter=metadata_filter
            )

        else:

            results = vectorstore.similarity_search_with_score(
                question,
                k=5
            )

        docs = []

        print("\nНайденные документы:")

        for i, (doc, score) in enumerate(results, start=1):

            meta = doc.metadata

            print(f"""
        --- Документ {i} ---
        Название: {meta.get('title')}
        Проект: {meta.get('project')}
        Дата: {meta.get('date')}
        Статус: {meta.get('status')}
        Score: {score:.3f}
        """)

            docs.append(doc)

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        prompt = f"""
Ответь на вопрос пользователя только на основе контекста.

Контекст:

{context}

Вопрос:

{question}

Если ответа нет в контексте, так и скажи.
"""

        response = llm.invoke(prompt)

        print("\nОтвет:")
        print(response.content)

        print("\nИсточники:")

        for i, doc in enumerate(docs, start=1):

            print(
                f"{i}. "
                f"{doc.metadata.get('title')} "
                f"({doc.metadata.get('date')})"
            )


if __name__ == "__main__":
    main()