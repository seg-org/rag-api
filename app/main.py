import uvicorn
from config import config
from fastapi import FastAPI
from llm import LLM
from models import AddTextRequest, CompleteChatRequest

app = FastAPI()
llm = LLM()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/complete-chat")
def complete_chat(request: CompleteChatRequest):
    reply = llm.complete_chat(request.text)

    return {"reply": reply}


@app.post("/add-text")
def add_text(request: AddTextRequest):
    reply = llm.embed(request.text)

    return {"reply": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.app.port)
