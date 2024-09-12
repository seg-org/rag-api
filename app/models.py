from typing import List

from pydantic import BaseModel


class RecordMessageRequest(BaseModel):
    message: str


class AddTextDocumentRequest(BaseModel):
    text: str


class AddWebDocumentRequest(BaseModel):
    url: str
