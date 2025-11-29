"""Draft model for invoice auto-save functionality."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class InvoiceDraft(Base):
    """Invoice draft model for auto-save and manual save functionality."""
    
    __tablename__ = "invoice_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Draft data (same structure as invoice request)
    draft_data = Column(JSONB, nullable=False)
    # Example: {"invoice_number": "INV-001", "customer_name_ar": "...", "line_items": [...]}

    # Metadata
    name = Column(String(100), nullable=True)  # Optional name for draft
    is_auto_saved = Column(Boolean, default=True)  # True for auto-saves, False for manual

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="drafts")
