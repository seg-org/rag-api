from pydantic import BaseModel


class RecordMessageRequest(BaseModel):
    message: str


class AddTextDocumentRequest(BaseModel):
    text: str


class AddWebDocumentRequest(BaseModel):
    url: str

class AddBorrowMoneyRequest(BaseModel):
    borrower: str
    lender: str
    amount: float

class AddSplitBillRequest(BaseModel):
    payer: str
    participants: str
    amount: float

class AskDebtSummaryRequest(BaseModel):
    person: str