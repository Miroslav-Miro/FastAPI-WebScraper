from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database.models import ScrapedItem
import uuid


def ingest_items(items, db, owner_id):
    rows = []
    for it in items:
        rows.append(
            {
                "id": uuid.uuid4(),
                "title": it["title"],
                "description": it.get("description", ""),
                "url": it["url"],
                "owner_id": owner_id,
            }
        )

    stmt = (
        pg_insert(ScrapedItem)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["owner_id", "url"])
    )

    result = db.execute(stmt)
    db.commit()
    return {"inserted": result.rowcount}
