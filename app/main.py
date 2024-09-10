import uvicorn
from config import config
from db import DB
from fastapi import APIRouter, FastAPI
from llm import LLM
from logger import logger
from models import AddTextRequest

app = FastAPI()
router = APIRouter(prefix="/api/v1")
llm = LLM()
db = DB(log=logger)


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/add-text")
async def root():
    db.add_text("Hello, how are you?")
    return {"message": "Added text"}


@router.get("/get-all-text")
async def root():
    return db.get_all()


@router.get("/complete-chat")
def complete_chat(text: str = None):
    reply = llm.complete_chat(text)

    return {"reply": reply}


@router.post("/add-text")
def add_text(request: AddTextRequest):
    reply = llm.embed(request.text)

    return {"reply": reply}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=config.app.port)
