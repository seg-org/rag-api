from typing import List

from pydantic import BaseModel


class AddTextRequest(BaseModel):
    text: str
