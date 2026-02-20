from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaperCreate(BaseModel):
    title: str
    authors: str
    abstract: str
    notes: Optional[str] = None
    link: Optional[str] = None   # <-- add this



class PaperResponse(BaseModel):
    id: int
    title: str
    authors: str
    abstract: str
    notes: Optional[str]
    link: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True