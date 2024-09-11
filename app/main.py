import uvicorn
from config import config
from db import DB
from fastapi import APIRouter, FastAPI
from llm import LLM
from logger import logger
from models import AddTextDocumentRequest, AddWebDocumentRequest

app = FastAPI()
router = APIRouter(prefix="/api/v1")
db = DB(log=logger)
llm = LLM(retriever=db.retriever)


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/documents")
async def docs_get_all():
    return db.get_all()


@router.get("/documents/relevant")
async def docs_get_relevant(text: str = None):
    return db.get_relevant_text(text)


@router.post("/documents/text")
async def docs_add_text(request: AddTextDocumentRequest):
    reply = db.add_text(request.text)

    return {"reply": reply}


@router.post("/documents/web")
async def docs_add_web(request: AddWebDocumentRequest):
    reply = db.add_web(request.url)

    return {"reply": reply}


@router.get("/complete-chat")
async def complete_chat(text: str = None):
    reply = llm.complete_chat(text)

    return {"reply": reply}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=config.app.port)
