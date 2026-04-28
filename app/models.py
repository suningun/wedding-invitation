"""SQLAlchemy models for the Wedding Management Dashboard."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


def generate_uuid() -> str:
    """Generate a new UUID4 string for unique IDs across system."""
    return str(uuid.uuid4())

class User(UserMixin, db.Model):
    """Registered organizer who manages their own wedding."""

    __tablename__ = "user"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    wedding = db.relationship(
        "WeddingEvent", backref="organizer", uselist=False, lazy=True
    )

    # Encrypt password using PBKDF2:SHA256 for secure storage
    def set_password(self, password: str) -> None:
        """Hash and store a plaintext password using PBKDF2:SHA256 encryption."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    # Verify user password during login
    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class WeddingEvent(db.Model):
    """A wedding managed by a single organizer.

    Multilingual fields (bride_name, groom_name, venue_name, venue_address,
    welcome_message) are stored as JSON with keys "en" and "km".
    """

    __tablename__ = "wedding_event"

    wedding_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)

    template = db.Column(db.String(50), nullable=False, default="classic")

    wedding_date = db.Column(db.Date, nullable=True)
    ceremony_time = db.Column(db.Time, nullable=True)
    reception_time = db.Column(db.Time, nullable=True)
    venue_map_url = db.Column(db.String(500), nullable=True)
    organizer_phone = db.Column(db.String(50), nullable=True)

    bride_name = db.Column(db.JSON, default=lambda: {"en": "", "km": ""})
    groom_name = db.Column(db.JSON, default=lambda: {"en": "", "km": ""})
    venue_name = db.Column(db.JSON, default=lambda: {"en": "", "km": ""})
    venue_address = db.Column(db.JSON, default=lambda: {"en": "", "km": ""})
    welcome_message = db.Column(db.JSON, default=lambda: {"en": "", "km": ""})

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    guests = db.relationship("Guest", backref="wedding", lazy=True)

    def __repr__(self) -> str:
        return f"<WeddingEvent {self.wedding_id}>"


class Guest(db.Model):
    """A wedding guest with invitation tracking and check-in state."""

    __tablename__ = "guest"

    guest_id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    wedding_id = db.Column(
        db.String(36), db.ForeignKey("wedding_event.wedding_id"), nullable=False
    )

    full_name = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    side = db.Column(db.String(10), nullable=False, default="bride")
    language = db.Column(db.String(2), nullable=False, default="en")

    invitation_token = db.Column(
        db.String(36), unique=True, nullable=False, default=generate_uuid
    )
    invitation_shared = db.Column(db.Boolean, default=False)

    checked_in = db.Column(db.Boolean, default=False)
    check_in_time = db.Column(db.DateTime, nullable=True)

    gift_amount = db.Column(db.Numeric(12, 2), default=Decimal("0.00"))
    gift_currency = db.Column(db.String(3), default="USD")
    gift_note = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Guest {self.full_name}>"
