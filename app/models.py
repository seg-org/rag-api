from typing import List

from pydantic import BaseModel


class CompleteChatRequest(BaseModel):
    text: str


class AddTextRequest(BaseModel):
    text: str
