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

def _intersection_count(a, b):
    if not a or not b:
        return 0

    set1 = {
        x.strip().lower()
        for x in a.split(",")
        if x.strip()
    }

    set2 = {
        x.strip().lower()
        for x in b.split(",")
        if x.strip()
    }

    return len(set1 & set2)

def _find_related_meetings(
    vectorstore,
    base_doc,
    exclude_sources=None,
    k=3
):
    if base_doc is None:
        return []

    data = vectorstore._collection.get(
        include=["documents", "metadatas"]
    )

    exclude = set(exclude_sources or [])

    related = []

    base = base_doc.metadata

    for document, meta in zip(
        data["documents"],
        data["metadatas"]
    ):

        identity = meta.get("source") or meta.get("title")

        if identity in exclude:
            continue

        score = 0

        # проект
        if (
            base.get("project")
            and base.get("project") == meta.get("project")
        ):
            score += 5

        # участники
        score += (
            _intersection_count(
                base.get("participants", ""),
                meta.get("participants", "")
            ) * 3
        )

        # исполнители
        score += (
            _intersection_count(
                base.get("assignees", ""),
                meta.get("assignees", "")
            ) * 2
        )

        # темы
        score += (
            _intersection_count(
                base.get("topics", ""),
                meta.get("topics", "")
            ) * 2
        )

        # решения
        if (
            base.get("decisions")
            and meta.get("decisions")
            and any(
                d in meta["decisions"]
                for d in base["decisions"].split("|")
            )
        ):
            score += 2

        # поручения
        if (
            base.get("tasks")
            and meta.get("tasks")
            and any(
                t in meta["tasks"]
                for t in base["tasks"].split("|")
            )
        ):
            score += 2

        if score == 0:
            continue

        related.append(
            (
                score,
                meta
            )
        )

    related.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        x[1]
        for x in related[:k]
    ]


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

        related_docs = _find_related_meetings(
            vectorstore,
            docs[0] if docs else None,
            exclude_sources=[_get_doc_identity(doc) for doc in docs],
            k=3,
        )

        if related_docs:
            print("\nСвязанные встречи:")
            for i, meta in enumerate(related_docs, start=1):
                print(
                    f"{i}. "
                    f"{meta.get('title')} "
                    f"({meta.get('date')})"
                    f" — проект: {meta.get('project')}"
                )

if __name__ == "__main__":
    main()