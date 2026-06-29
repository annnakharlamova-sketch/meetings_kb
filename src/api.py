from fastapi import FastAPI
from pydantic import BaseModel

from langchain_core.documents import Document
from src.vectorstore import get_vectorstore
from src.parsers.meeting_parser import parse_meeting
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from src.services.search_service import search as kb_search

templates = Jinja2Templates(directory="src/templates")

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="src/static"),
    name="static"
)

class MeetingRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    q: str | None = None
):
    context = {}

    if q:
        result = kb_search(q)

        context = {
            "question": q,
            "answer": result["answer"],
            "sources": result["sources"],
            "related": result["related"],
        }

    context["request"] = request

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context
    )

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
            "tasks": " | ".join(
                f'{task["assignee"]}: {task["task"]}'
                for task in meeting["tasks"]
            ),

            "decisions": " | ".join(
                meeting["decisions"]
            ),

            "assignees": ",".join(
                task["assignee"]
                for task in meeting["tasks"]
            ),
            "tasks_count": len(
                meeting["tasks"]
            ),
            "decisions_count": len(
                meeting["decisions"]
            )
        }
    )
    
    vectorstore = get_vectorstore()

    vectorstore.add_documents([doc])

    return {
        "status": "success",
        "title": meeting["title"]
    }

@app.get("/search")
def search(q: str):

    result = kb_search(q)

    return {
        "question": q,
        "answer": result["answer"],
        "sources": result["sources"],
        "related": result["related"]
    }