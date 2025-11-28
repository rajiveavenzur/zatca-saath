"""Invoice schemas for request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import re


class InvoiceLineItem(BaseModel):
    """Schema for invoice line item."""
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    vat_rate: Decimal = Field(default=Decimal("15.0"), ge=0, le=100)

    @field_validator('vat_rate')
    @classmethod
    def validate_vat_rate(cls, v: Decimal) -> Decimal:
        """Validate VAT rate (Saudi VAT is typically 15%)."""
        if v not in [Decimal("0"), Decimal("5"), Decimal("15")]:
            raise ValueError("VAT rate must be 0%, 5%, or 15%")
        return v

    @property
    def subtotal(self) -> Decimal:
        """Calculate line item subtotal."""
        return self.quantity * self.unit_price

    @property
    def vat_amount(self) -> Decimal:
        """Calculate VAT amount."""
        return (self.subtotal * self.vat_rate) / Decimal("100")

    @property
    def total(self) -> Decimal:
        """Calculate line item total with VAT."""
        return self.subtotal + self.vat_amount


class InvoiceRequest(BaseModel):
    """Schema for invoice generation request."""
    # Customer information
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_vat_number: Optional[str] = Field(None, pattern=r"^3\d{14}$")
    customer_address: str = Field(..., min_length=1, max_length=500)

    # Invoice details
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: datetime = Field(default_factory=datetime.now)

    # Line items
    line_items: List[InvoiceLineItem] = Field(..., min_length=1, max_length=100)

    # Optional fields
    notes: Optional[str] = Field(None, max_length=1000)

    @property
    def subtotal(self) -> Decimal:
        """Calculate invoice subtotal."""
        return sum((item.subtotal for item in self.line_items), Decimal("0"))

    @property
    def total_vat(self) -> Decimal:
        """Calculate total VAT amount."""
        return sum((item.vat_amount for item in self.line_items), Decimal("0"))

    @property
    def total_amount(self) -> Decimal:
        """Calculate invoice total amount."""
        return self.subtotal + self.total_vat

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "مؤسسة التجارة المتطورة",
                "customer_vat_number": "310122393500003",
                "customer_address": "الرياض، المملكة العربية السعودية",
                "invoice_number": "INV-2024-001",
                "line_items": [
                    {
                        "description": "استشارات تقنية",
                        "quantity": 10,
                        "unit_price": 500.00,
                        "vat_rate": 15.0
                    }
                ],
                "notes": "شكراً لتعاملكم معنا"
            }
        }


class InvoiceResponse(BaseModel):
    """Schema for invoice generation response."""
    invoice_number: str
    pdf_base64: str  # Base64-encoded PDF
    qr_code_data: str
    subtotal: Decimal
    total_vat: Decimal
    total_amount: Decimal
    generated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "INV-2024-001",
                "pdf_base64": "JVBERi0xLjQK...",
                "qr_code_data": "AQ1aYXRjYSBkZW1v...",
                "subtotal": 5000.00,
                "total_vat": 750.00,
                "total_amount": 5750.00,
                "generated_at": "2024-11-25T10:30:00Z"
            }
        }
