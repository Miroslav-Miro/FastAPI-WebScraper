import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import requests

from app.database import get_db
from app.models import ScrapedItem, User
from app.schemas import ItemRead
from app.scraper import scrape_books
from app.services.ingest import ingest_items
from app.dependencies.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/scrape", response_model=dict)
def run_scraper(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # requires auth
):
    """
    Trigger the scraping process. Only authenticated users can run this.
    """
    logger.info("Scrape requested by user: %s", current_user.username)
    try:
        items = scrape_books()
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream site unavailable or request failed",
        )

    result = ingest_items(items, db)
    return result


@router.get("/items", response_model=list[ItemRead])
def list_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # protect listing if needed
):
    """List all scraped items."""
    logger.info("Items listed by user: %s", current_user.username)
    return db.query(ScrapedItem).all()


@router.get("/items/{item_id}", response_model=ItemRead)
def get_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # protect detail view
):
    item = db.query(ScrapedItem).filter(ScrapedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_id}")
def delete_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # protect deletion
):
    item = db.query(ScrapedItem).filter(ScrapedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    logger.info("Item %s deleted by user %s", item_id, current_user.username)
    return {"status": "deleted"}
