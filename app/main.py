import uvicorn
from config import config
from db import DB
from fastapi import APIRouter, Depends, FastAPI
from llm import LLM
from logger import logger
from middleware import verify_api_key
from models import AddTextDocumentRequest, AddWebDocumentRequest, RecordMessageRequest, AddBorrowMoneyRequest, AskDebtSummaryRequest

app = FastAPI()
router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])
db = DB(log=logger)
llm = LLM(db=db, log=logger)


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/guild/{guild_id}/toggle-web-search")
async def toggle_web_search(guild_id: str = None):
    reply = llm.toggle_web_search(guild_id)

    return {"reply": reply}


@router.get("/guild/{guild_id}/documents")
async def docs_get_all(guild_id: str = None):
    reply = db.get_all_docs(guild_id)

    return {"reply": reply}


@router.post("/guild/{guild_id}/documents/text")
async def docs_add_text(request: AddTextDocumentRequest, guild_id: str = None):
    reply = db.add_text(request.text, guild_id)

    return {"reply": reply}


@router.post("/guild/{guild_id}/documents/web")
async def docs_add_web(request: AddWebDocumentRequest, guild_id: str = None):
    reply = db.add_web(request.url, guild_id)

    return {"reply": reply}

@router.post("/guild/{guild_id}/debt/add-borrow-money")
async def debt_add_borrow_money(request: AddBorrowMoneyRequest, guild_id: str = None):
    reply = db.add_borrow_money(request.borrower, request.lender, request.amount, guild_id)

    return {"reply": reply}

@router.post("/guild/{guild_id}/debt/ask-debt-summary")
async def debt_use_debt_sum(request: AskDebtSummaryRequest, guild_id: str = None):
    reply = llm.complete_chat(request.person, guild_id, True)

    return {"reply": reply}

@router.get("/guild/{guild_id}/complete-chat")
async def complete_chat(text: str = None, guild_id: str = None):
    reply = llm.complete_chat(text, guild_id)

    return {"reply": reply}

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.app.port)
