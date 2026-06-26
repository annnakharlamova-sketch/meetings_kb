from src.vectorstore import get_vectorstore
from src.llm import get_llm
from src.parsers.filters import build_filters_from_query
import re
import logging
from src.hybrid_search import hybrid_search

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

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

        results = hybrid_search(
            vectorstore,
            question,
            filters=query_filters
        )

        docs = []

        logger.info("Найдено %d документов", len(results))

        for i, item in enumerate(results, start=1):

            doc = item["doc"]

            logger.info(
                "[%d] final=%.3f sem=%.3f key=%d | %s",
                i,
                item["final_score"],
                item["semantic_score"],
                item["keyword_score"],
                doc.metadata.get("title"),
            )

            docs.append(doc)

        context_parts = []

        for i, doc in enumerate(docs, start=1):
            context_parts.append(
                f"""
        [DOC{i}]

        Название: {doc.metadata.get("title")}
        Дата: {doc.metadata.get("date")}
        Проект: {doc.metadata.get("project")}

        {doc.page_content}
        """
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
        Ты отвечаешь только по предоставленным документам.

        Каждый документ имеет идентификатор вида [DOC1], [DOC2] и т.д.

        Если используешь информацию из документа,
        обязательно после соответствующего предложения укажи ссылку
        в формате [DOC1].

        Если используются несколько документов —
        укажи несколько ссылок.

        Контекст:

        {context}

        Вопрос:

        {question}
        
        Если ответа нет в документах —
        так и скажи.
        """

        response = llm.invoke(prompt)

        print("\nОтвет:")
        print(response.content)

        used_docs = sorted(set(re.findall(r"\[DOC\d+\]", response.content)))

        print("\nИсточники:")

        if used_docs:
            for ref in used_docs:
                idx = int(ref[4:-1]) - 1
                doc = docs[idx]

                print(
                    f"{ref} "
                    f"{doc.metadata.get('title')} "
                    f"({doc.metadata.get('date')})"
                )
        else:
            print("Модель не сослалась ни на один документ.")

        print("\nИсточники:")

        for i, doc in enumerate(docs, start=1):
            print(
                f"[DOC{i}] "
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