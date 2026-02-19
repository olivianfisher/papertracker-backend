from sqlalchemy.orm import Session
from . import models, schemas
import feedparser 
import requests


def create_paper(db: Session, paper: schemas.PaperCreate):
    db_paper = models.Paper(**paper.dict())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper


def get_papers(db: Session):
    return db.query(models.Paper).filter(models.Paper.is_deleted == False).all()


def get_weekly_summary(db: Session):
    papers = db.query(models.Paper).all()

    if not papers:
        return "You didn't read any papers this week."

    summary = "Weekly Learning Summary:\n\n"

    for p in papers:
        summary += f"• {p.title} — Key idea: {p.abstract[:150]}...\n"

    summary += "\nKeep building knowledge!"

    return summary

import urllib.parse

def fetch_arxiv_papers(query: str = "machine learning", max_results: int = 5):
    try:
        encoded_query = urllib.parse.quote(query)

        url = (
            f"http://export.arxiv.org/api/query?"
            f"search_query=all:{encoded_query}"
            f"&start=0"
            f"&max_results={max_results}"
            f"&sortBy=submittedDate"
            f"&sortOrder=descending"
        )

        feed = feedparser.parse(url)

        papers = []

        for entry in feed.entries:
            authors = ", ".join(
                author.name for author in getattr(entry, "authors", [])
            )

            papers.append({
                "title": getattr(entry, "title", "No title"),
                "authors": authors,
                "summary": getattr(entry, "summary", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", "")
            })

        return papers

    except Exception as e:
        print("ARXIV ERROR:", e)
        return []