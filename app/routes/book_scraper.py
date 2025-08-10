"""
Book scraper API routes for the Web Scraper application.

Endpoints:
- POST /scrape: Trigger the book scraping process for authenticated users.
- GET /items: List all scraped items owned by the authenticated user.
- GET /items/{item_id}: Get details of a specific scraped item by ID.
- DELETE /items/{item_id}: Delete a specific scraped item by ID.

Includes authorization checks to ensure users can only access their own data.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import requests

from app.core.database import get_db
from app.database.models import ScrapedItem, User
from app.schemas import ItemRead
from app.services.scraper_service import scrape_books
from app.services.ingest import ingest_items
from app.services.auth_service import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/scrape", response_model=dict)
def run_scraper(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger the scraping process to fetch new items.

    Only authenticated users may trigger this endpoint.
    Calls the scraper service to get new book data and ingests the items into the database
    associated with the current user.

    Args:
        db (Session): SQLAlchemy database session dependency.
        current_user (User): Currently authenticated user.

    Returns:
        dict: Result summary of the ingestion process.

    Raises:
        HTTPException: 502 Bad Gateway if the scraping upstream site is unavailable or request fails.
    """
    logger.info("Items requested by user: %s", current_user.username)
    try:
        items = scrape_books()
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream site unavailable or request failed",
        )

    result = ingest_items(items, db, owner_id=current_user.id)
    return result


@router.get("/items", response_model=list[ItemRead])
def list_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a list of scraped items owned by the current user.

    Args:
        db (Session): SQLAlchemy database session dependency.
        current_user (User): Currently authenticated user.

    Returns:
        List[ItemRead]: List of scraped items.
    """
    logger.info("Items listed by user: %s", current_user.username)
    return db.query(ScrapedItem).filter(ScrapedItem.owner_id == current_user.id).all()


@router.get("/items/{item_id}", response_model=ItemRead)
def get_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific scraped item by its ID if it belongs to the current user.

    Args:
        item_id (UUID): The UUID of the item to retrieve.
        db (Session): SQLAlchemy database session dependency.
        current_user (User): Currently authenticated user.

    Returns:
        ItemRead: The scraped item details.

    Raises:
        HTTPException: 404 Not Found if the item does not exist or does not belong to the user.
    """
    item = (
        db.query(ScrapedItem)
        .filter(ScrapedItem.id == item_id, ScrapedItem.owner_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_id}")
def delete_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a specific scraped item by its ID if it belongs to the current user.

    Args:
        item_id (UUID): The UUID of the item to delete.
        db (Session): SQLAlchemy database session dependency.
        current_user (User): Currently authenticated user.

    Returns:
        dict: Status message indicating deletion success.

    Raises:
        HTTPException: 404 Not Found if the item does not exist or does not belong to the user.
    """
    item = (
        db.query(ScrapedItem)
        .filter(ScrapedItem.id == item_id, ScrapedItem.owner_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    logger.info("Item %s deleted by user %s", item_id, current_user.username)
    return {"status": "deleted"}
