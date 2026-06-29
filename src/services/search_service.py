import re

from src.vectorstore import get_vectorstore
from src.llm import get_llm
from src.hybrid_search import hybrid_search
from src.parsers.filters import build_filters_from_query
from functools import lru_cache

@lru_cache(maxsize=1)
def get_services():
    vectorstore = get_vectorstore()
    llm = get_llm()
    return vectorstore, llm

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

def search(question: str):

    vectorstore, llm = get_services()

    filters = build_filters_from_query(question)

    results = hybrid_search(
        vectorstore,
        question,
        filters=filters
    )

    docs = [item["doc"] for item in results]

    context = "\n\n".join(
        f"""
[DOC{i}]

Название: {doc.metadata.get("title")}
Дата: {doc.metadata.get("date")}
Проект: {doc.metadata.get("project")}

{doc.page_content}
"""
        for i, doc in enumerate(docs, start=1)
    )

    prompt = f"""
Ты отвечаешь только по предоставленным документам.

Каждый документ имеет идентификатор [DOC1], [DOC2] ...

Если используешь информацию —
обязательно указывай ссылки.

Контекст:

{context}

Вопрос:

{question}
"""

    response = llm.invoke(prompt)

    used_docs = sorted(set(re.findall(r"\[DOC\d+\]", response.content)))

    sources = []

    for ref in used_docs:

        idx = int(ref[4:-1]) - 1

        sources.append(
            {
                "ref": ref,
                "title": docs[idx].metadata.get("title"),
                "date": docs[idx].metadata.get("date"),
                "project": docs[idx].metadata.get("project")
            }
        )

    related = _find_related_meetings(
        vectorstore,
        docs[0] if docs else None,
        exclude_sources=[
            _get_doc_identity(doc)
            for doc in docs
        ],
        k=3
    )

    return {
        "answer": response.content,
        "sources": sources,
        "docs": docs,
        "related": related,
        "results": results
    }