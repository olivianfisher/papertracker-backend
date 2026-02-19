from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaperCreate(BaseModel):
    title: str
    authors: str
    abstract: str
    notes: Optional[str] = None


class PaperResponse(BaseModel):
    id: int
    title: str
    authors: str
    abstract: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True