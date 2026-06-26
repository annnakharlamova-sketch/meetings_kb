from src.vectorstore import get_vectorstore
from langchain_core.documents import Document

def keyword_search(query: str, filters=None):
    vectorstore = get_vectorstore()

    collection = vectorstore._collection

    data = collection.get(
        include=["documents", "metadatas"]
    )

    query = query.lower()

    results = []

    for document, metadata in zip(
            data["documents"],
            data["metadatas"]
    ):

        if filters:
            matched = True

            for key, value in filters.items():

                if isinstance(value, dict):
                    if "$in" in value:
                        doc_value = metadata.get(key, "")

                        if not any(v in doc_value for v in value["$in"]):
                            matched = False
                            break
                else:
                    if metadata.get(key) != value:
                        matched = False
                        break

            if not matched:
                continue

        score = document.lower().count(query)

        if score > 0:
            results.append(
                (score, Document(page_content=document, metadata=metadata))
            )

    results.sort(key=lambda x: x[0], reverse=True)

    return results