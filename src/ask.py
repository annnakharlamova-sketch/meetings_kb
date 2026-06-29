import logging

from src.services.search_service import search

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

def main():

    while True:
        question = input("\nВаш вопрос: ")

        if question.lower() in ["exit", "quit"]:
            break

        result = search(question)

        if not result["results"]:
            print("\nНичего не найдено.")
            continue

        logger.info(
            "Найдено %d документов",
            len(result["results"])
        )

        for i, item in enumerate(result["results"], start=1):

            doc = item["doc"]

            logger.info(
                "[%d] final=%.3f sem=%.3f key=%d | %s",
                i,
                item["final_score"],
                item["semantic_score"],
                item["keyword_score"],
                doc.metadata.get("title"),
            )

        print("\nОтвет:")
        print(result["answer"])

        print("\nИсточники:")

        for source in result["sources"]:
            print(
                f'{source["ref"]} '
                f'{source["title"]} '
                f'({source["date"]})'
            )

        if result["related"]:
            print("\nСвязанные встречи:")
            for i, meta in enumerate(result["related"], start=1):
                project = meta.get("project") or "—"

                print(
                    f"{i}. "
                    f"{meta.get('title')} "
                    f"({meta.get('date')})"
                    f" — проект: {project}"
                )

if __name__ == "__main__":
    main()