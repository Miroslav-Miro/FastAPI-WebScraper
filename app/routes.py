from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import ScrapedItem
from app.schemas import ItemRead
from app.scraper import scrape_books


router = APIRouter()


@router.get("/items", response_model=list[ItemRead])
def list_items(db: Session = Depends(get_db)):
    return db.query(ScrapedItem).all()


@router.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    item = db.query(ScrapedItem).filter(ScrapedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_id}")
def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    item = db.query(ScrapedItem).filter(ScrapedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}


@router.post("/scrape")
def run_scraper(db: Session = Depends(get_db)):
    added = scrape_books(db, limit=10)
    return {"added": added}
