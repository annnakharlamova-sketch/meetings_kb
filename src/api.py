from fastapi import FastAPI
from pydantic import BaseModel

from langchain_core.documents import Document

from src.parsers.meeting_parser import parse_meeting
from src.vectorstore import get_vectorstore
from src.llm import get_llm

app = FastAPI()

vectorstore = get_vectorstore()
llm = get_llm()

class MeetingRequest(BaseModel):
    text: str


@app.post("/upload")
def upload_meeting(request: MeetingRequest):

    meeting = parse_meeting(request.text)

    doc = Document(
        page_content=request.text,
        metadata={
            "title": meeting["title"],
            "project": meeting["project"],
            "date": meeting["date"],
            "participants": ",".join(
                meeting["participants"]
            ),
            "status": meeting["status"],
            "topics": ",".join(
                meeting["topics"]
            ),
            "tasks_count": len(
                meeting["tasks"]
            ),
            "decisions_count": len(
                meeting["decisions"]
            )
        }
    )

    vectorstore.add_documents([doc])

    return {
        "status": "success",
        "title": meeting["title"]
    }

@app.get("/search")
def search(q: str):

    results = vectorstore.similarity_search(
        q,
        k=5
    )

    context = "\n\n".join(
        doc.page_content
        for doc in results
    )

    prompt = f"""
Ответь на вопрос пользователя только на основе контекста.

Контекст:

{context}

Вопрос:

{q}

Если ответа нет в контексте, так и скажи.
"""

    response = llm.invoke(prompt)

    return {
        "question": q,
        "answer": response.content,
        "sources": [
            {
                "title": doc.metadata.get("title"),
                "date": doc.metadata.get("date"),
                "project": doc.metadata.get("project")
            }
            for doc in results
        ]
    }