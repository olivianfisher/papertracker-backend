from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from . import crud, schemas, models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/papers", response_model=schemas.PaperResponse)
def create_paper(paper: schemas.PaperCreate, db: Session = Depends(get_db)):
    return crud.create_paper(db, paper)


@app.get("/papers", response_model=list[schemas.PaperResponse])
def read_papers(db: Session = Depends(get_db)):
    return crud.get_papers(db)


@app.get("/weekly-summary")
def weekly_summary(db: Session = Depends(get_db)):
    return {"summary": crud.get_weekly_summary(db)}


@app.get("/")
def root():
    return {"message": "PaperTracker API is running"}

@app.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    query: str | None = Query(None)
):
    if not query:
        query = crud.extract_keywords_from_library(db)

    arxiv = crud.fetch_arxiv_papers(query)
    biorxiv = crud.fetch_biorxiv_papers(query)
    pubmed = crud.fetch_pubmed_papers(query)

    combined = arxiv + biorxiv + pubmed

    return {
        "query_used": query,
        "recommendations": combined
    }

@app.delete("/papers/{paper_id}")
def soft_delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if paper:
        paper.is_deleted = True
        db.commit()
        return {"message": "Paper soft deleted"}
    return {"error": "Paper not found"}

@app.put("/papers/{paper_id}/restore")
def restore_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if paper:
        paper.is_deleted = False
        db.commit()
        return {"message": "Paper restored"}
    return {"error": "Paper not found"}

from datetime import datetime, timedelta

@app.get("/weekly-count")
def weekly_count(db: Session = Depends(get_db)):
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    count = db.query(models.Paper).filter(
        models.Paper.created_at >= one_week_ago,
        models.Paper.is_deleted == False
    ).count()
    return {"count": count}