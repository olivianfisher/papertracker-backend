from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from . import crud, schemas
from fastapi import Query

Base.metadata.create_all(bind=engine)

app = FastAPI()


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
def get_recommendations(query: str = Query("machine learning")): 
    papers = crud.fetch_arxiv_papers(query=query) 
    return {"recommendations": papers}