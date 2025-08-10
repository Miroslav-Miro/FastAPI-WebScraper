"""
SQLAlchemy ORM models defining database schema for the Web Scraper API.

Includes models for:
- ScrapedItem: Represents individual scraped data entries tied to a user.
- User: Represents registered users with authentication credentials.

Uses PostgreSQL UUID columns for primary keys and timestamps for creation time.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    func,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid
from app.core.database import Base
from sqlalchemy.orm import relationship


class ScrapedItem(Base):
    """
    Represents an item scraped by the user.

    Attributes:
        id (UUID): Primary key, unique identifier for the scraped item.
        title (str): Title of the scraped item.
        description (str): Optional detailed description.
        url (str): Unique URL of the scraped item.
        created_at (datetime): Timestamp of when the item was created.
        owner_id (UUID): Foreign key linking to the User who owns this item.
        owner (User): SQLAlchemy relationship to the owning User.
    """

    __tablename__ = "scraped_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    url = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", backref="items")

    __table_args__ = (UniqueConstraint("owner_id", "url", name="uq_owner_url"),)


class User(Base):
    """
    Represents a user of the web scraper application.

    Attributes:
        id (UUID): Primary key, unique identifier for the user.
        username (str): Unique username for login.
        hashed_password (str): Hashed password for authentication.
        created_at (datetime): Timestamp when the user was created.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
