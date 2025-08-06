from typing import Iterable, Dict
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import ScrapedItem

logger = logging.getLogger(__name__)


def ingest_items(items: Iterable[Dict], db: Session) -> dict:
    """
    Save scraped items into the DB.
    Skips duplicates by URL (unique constraint) and returns counts.
    """
    added = 0
    skipped = 0

    for i in items:
        obj = ScrapedItem(
            title=i["title"],
            description=i.get("description"),
            url=i["url"],
        )
        try:
            db.add(obj)
            db.commit()
            added += 1
        except IntegrityError:
            db.rollback()
            skipped += 1
            logger.info("Duplicate (by URL) skipped: %s", i["url"])
        except Exception:
            db.rollback()
            logger.exception("DB error while inserting: %s", i)

    result = {"added": added, "skipped_duplicates": skipped}
    logger.info("Scrape import result: %s", result)
    return result
