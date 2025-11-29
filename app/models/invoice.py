"""Invoice model for storing generated invoices."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Invoice(Base):
    """Invoice model for storing invoice history."""
    
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), nullable=False, index=True, unique=True)
    invoice_date = Column(DateTime(timezone=True), nullable=False)
    
    # Customer information (Arabic is MANDATORY per ZATCA)
    customer_name_ar = Column(String(200), nullable=False)
    customer_name_en = Column(String(200), nullable=True)
    customer_address_ar = Column(String(500), nullable=False)
    customer_address_en = Column(String(500), nullable=True)
    customer_vat_number = Column(String(15), nullable=True)
    
    # Financial details
    subtotal = Column(Numeric(precision=10, scale=2), nullable=False)
    total_vat = Column(Numeric(precision=10, scale=2), nullable=False)
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    
    # Line items stored as JSON
    line_items = Column(JSONB, nullable=False)
    
    # QR code data
    qr_code_data = Column(Text, nullable=False)
    
    # PDF storage (base64 encoded)
    pdf_data = Column(Text, nullable=False)
    
    # Optional notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
