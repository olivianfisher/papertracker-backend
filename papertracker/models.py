from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base


from sqlalchemy import Boolean

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(String)
    abstract = Column(Text)
    notes = Column(Text)
    link = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)