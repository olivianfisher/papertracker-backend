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
import requests
from datetime import datetime, timedelta


def fetch_biorxiv_papers(query: str, max_results: int = 5):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        url = f"https://api.biorxiv.org/details/biorxiv/{start_date.date()}/{end_date.date()}"

        response = requests.get(url)
        data = response.json()

        papers = []

        for item in data.get("collection", []):
            if query.lower() in item.get("title", "").lower():
                papers.append({
                    "title": item.get("title"),
                    "authors": item.get("authors"),
                    "summary": item.get("abstract"),
                    "link": f"https://www.biorxiv.org/content/{item.get('doi')}",
                    "published": item.get("date"),
                    "source": "bioRxiv"
                })

        return papers[:max_results]

    except Exception as e:
        print("BIORXIV ERROR:", e)
        return []
def fetch_pubmed_papers(query: str, max_results: int = 5):
    try:
        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=pubmed&term={query}&retmax={max_results}&retmode=json"
        )

        search_res = requests.get(search_url).json()
        ids = search_res["esearchresult"]["idlist"]

        if not ids:
            return []

        fetch_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            f"?db=pubmed&id={','.join(ids)}&retmode=json"
        )

        fetch_res = requests.get(fetch_url).json()

        papers = []

        for pid in ids:
            item = fetch_res["result"][pid]

            papers.append({
                "title": item.get("title"),
                "authors": ", ".join(a["name"] for a in item.get("authors", [])),
                "summary": "",
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                "published": item.get("pubdate"),
                "source": "PubMed"
            })

        return papers

    except Exception as e:
        print("PUBMED ERROR:", e)
        return []
import re
from collections import Counter

def extract_keywords_from_library(db):
    papers = db.query(models.Paper).filter(
        models.Paper.is_deleted == False
    ).all()

    if not papers:
        return "machine learning"

    text = " ".join(
        (p.title or "") + " " + (p.abstract or "")
        for p in papers
    ).lower()

    words = re.findall(r"\b[a-zA-Z]{5,}\b", text)

    stopwords = {
        "paper", "study", "results", "using",
        "analysis", "based", "approach",
        "method", "methods"
    }

    filtered = [w for w in words if w not in stopwords]

    most_common = Counter(filtered).most_common(3)

    if not most_common:
        return "machine learning"

    return " ".join(word for word, _ in most_common)
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