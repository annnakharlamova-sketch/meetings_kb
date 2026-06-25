from vectorstore import get_vectorstore
from llm import get_llm
from parsers.filters import build_filters_from_query

def _get_doc_identity(doc):
    return doc.metadata.get("source") or doc.metadata.get("title") or ""


def _find_related_meetings(vectorstore, base_doc, exclude_sources=None, k=3):
    if base_doc is None:
        return []

    source_values = set(exclude_sources or [])
    if not base_doc.page_content:
        return []

    filters = {}
    project = base_doc.metadata.get("project")
    participants = base_doc.metadata.get("participants")
    topics = base_doc.metadata.get("topics")

    if project:
        filters["project"] = project
    elif participants:
        filters["participants"] = participants
    elif topics:
        filters["topics"] = topics
    else:
        return []

    results = vectorstore.similarity_search_with_score(
        base_doc.page_content,
        k=10,
        filter=filters
    )

    related = []
    for doc, _score in results:
        identity = _get_doc_identity(doc)
        if identity in source_values:
            continue
        source_values.add(identity)
        related.append(doc)
        if len(related) >= k:
            break

    return related


def main():
    vectorstore = get_vectorstore()
    llm = get_llm()

    while True:
        question = input("\nВаш вопрос: ")

        if question.lower() in ["exit", "quit"]:
            break

        query_filters = build_filters_from_query(question)

        print("\nФильтры:")
        print(query_filters)

        results = vectorstore.similarity_search_with_score(
            question,
            k=5,
            filter=query_filters if query_filters else None
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

        related_docs = _find_related_meetings(
            vectorstore,
            docs[0] if docs else None,
            exclude_sources=[_get_doc_identity(doc) for doc in docs],
            k=3,
        )

        if related_docs:
            print("\nСвязанные встречи:")
            for i, doc in enumerate(related_docs, start=1):
                print(
                    f"{i}. "
                    f"{doc.metadata.get('title')} "
                    f"({doc.metadata.get('date')})"
                    f" — проект: {doc.metadata.get('project')}"
                )


if __name__ == "__main__":
    main()