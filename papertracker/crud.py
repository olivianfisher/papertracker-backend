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
    return db.query(models.Paper).all()


def get_weekly_summary(db: Session):
    papers = db.query(models.Paper).all()

    if not papers:
        return "You didn't read any papers this week."

    summary = "Weekly Learning Summary:\n\n"

    for p in papers:
        summary += f"• {p.title} — Key idea: {p.abstract[:150]}...\n"

    summary += "\nKeep building knowledge!"

    return summary

def fetch_arxiv_papers(query: str = "machine learning", max_results: int = 5):
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query=all:{query}&start=0&max_results={max_results}"
    )

    feed = feedparser.parse(url)

    papers = []

    for entry in feed.entries:
        papers.append({
            "title": entry.title,
            "authors": ", ".join(author.name for author in entry.authors),
            "summary": entry.summary,
            "link": entry.link,
            "published": entry.published
        })

    return papers