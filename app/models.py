from typing import List

from pydantic import BaseModel


class AddTextDocumentRequest(BaseModel):
    text: str


class AddWebDocumentRequest(BaseModel):
    url: str
