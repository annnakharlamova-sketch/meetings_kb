from src.keyword_search import keyword_search
import logging

logger = logging.getLogger(__name__)


def get_identity(doc):
    return doc.metadata.get("source") or doc.metadata.get("title")


def hybrid_search(
    vectorstore,
    query,
    filters=None,
    k_semantic=5,
    k_keyword=5,
):
    semantic = vectorstore.similarity_search_with_score(
        query,
        k=k_semantic,
        filter=filters if filters else None
    )

    keyword = keyword_search(
        query,
        filters=filters
    )[:k_keyword]

    results = {}

    for doc, score in semantic:

        identity = get_identity(doc)

        results[identity] = {
            "doc": doc,
            "semantic_score": 1 / (1 + score),
            "keyword_score": 0,
        }

    for score, doc in keyword:

        identity = get_identity(doc)

        if identity in results:

            results[identity]["keyword_score"] = score

        else:

            results[identity] = {
                "doc": doc,
                "semantic_score": 0,
                "keyword_score": score,
            }
    
    results = list(results.values())

    for item in results:
        item["final_score"] = (
            item["semantic_score"] +
            item["keyword_score"] * 0.2
        )
    
    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )
    
    logger.info("Hybrid results : %d", len(results))

    for item in results:

        logger.info(
            "FINAL %.3f | SEM %.3f | KEY %d | %s",
            item["final_score"],
            item["semantic_score"],
            item["keyword_score"],
            item["doc"].metadata.get("title"),
        )

    return results