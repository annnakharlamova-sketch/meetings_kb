from pathlib import Path

from langchain_chroma import Chroma

from embeddings import get_embeddings


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "chroma_db"


def get_vectorstore():
    return Chroma(
        persist_directory=str(DB_DIR),
        embedding_function=get_embeddings()
    )