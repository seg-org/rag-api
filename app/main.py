import uvicorn
from config import config
from fastapi import APIRouter, FastAPI
from llm import LLM
from models import AddTextRequest, CompleteChatRequest

app = FastAPI()
router = APIRouter(prefix="/api/v1")
llm = LLM()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/complete-chat")
def complete_chat(request: CompleteChatRequest):
    reply = llm.complete_chat(request.text)

    return {"reply": reply}


@router.post("/add-text")
def add_text(request: AddTextRequest):
    reply = llm.embed(request.text)

    return {"reply": reply}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=config.app.port)
