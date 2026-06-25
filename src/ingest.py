from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma
from parsers.meeting_parser import parse_meeting
from embeddings import get_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"

def load_documents():
    documents = []

    for file in DATA_DIR.glob("*.txt"):

        loader = TextLoader(
            str(file),
            encoding="utf-8"
        )

        docs = loader.load()

        text = docs[0].page_content

        meeting = parse_meeting(text)

        print(
            meeting["title"],
            "|",
            meeting["project"]
        )

        for doc in docs:

            doc.metadata["date"] = meeting["date"]

            doc.metadata["participants"] = ",".join(
                meeting["participants"]
            )

            doc.metadata["title"] = meeting["title"]

            doc.metadata["project"] = meeting["project"]

            doc.metadata["status"] = meeting["status"]

            doc.metadata["topics"] = ",".join(
                meeting["topics"]
            )

            doc.metadata["tasks_count"] = len(
                meeting["tasks"]
            )

            doc.metadata["decisions_count"] = len(
                meeting["decisions"]
            )

        documents.extend(docs)

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50
    )

    return splitter.split_documents(documents)


def main():
    print("Загрузка документов...")

    documents = load_documents()

    print(f"Документов найдено: {len(documents)}")

    chunks = documents

    print(f"Документов для индексации: {len(chunks)}")
    print("\nМетаданные первого чанка:")
    print(chunks[0].metadata)

    embeddings = get_embeddings()

    if not chunks:
        print("Нет документов для индексации")
        return
    
    print("\nЗагруженные документы:")

    for doc in documents:
        print(doc.metadata["source"])

    print("Создание ChromaDB...")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )

    print("Готово!")

if __name__ == "__main__":
    main()