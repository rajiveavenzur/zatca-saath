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


class InvoiceLabels(BaseModel):
    """Labels for invoice in specific language."""
    company_name: str = Field(default="Company Name")
    vat_number: str = Field(default="VAT Number")
    invoice_number: str = Field(default="Invoice Number")
    date: str = Field(default="Date")
    customer_info: str = Field(default="Customer Information")
    description: str = Field(default="Description")
    quantity: str = Field(default="Qty")
    amount: str = Field(default="Amount")
    vat: str = Field(default="VAT")
    total: str = Field(default="Total")
    subtotal: str = Field(default="Subtotal")
    vat_total: str = Field(default="VAT (15%)")
    grand_total: str = Field(default="Total")
    qr_code: str = Field(default="QR Code")
    notes: str = Field(default="Notes")


class InvoiceRequest(BaseModel):
    """Schema for invoice generation request."""
    # Customer information (Arabic is MANDATORY per ZATCA regulations)
    customer_name_ar: str = Field(..., min_length=1, max_length=200, description="Customer name in Arabic (MANDATORY)")
    customer_name_en: Optional[str] = Field(None, max_length=200, description="Customer name in English (optional)")
    customer_address_ar: str = Field(..., min_length=1, max_length=500, description="Customer address in Arabic (MANDATORY)")
    customer_address_en: Optional[str] = Field(None, max_length=500, description="Customer address in English (optional)")
    customer_vat_number: Optional[str] = Field(None, pattern=r"^3\d{14}$")

    # Invoice details
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: datetime = Field(default_factory=datetime.now)

    # Line items
    line_items: List[InvoiceLineItem] = Field(..., min_length=1, max_length=100)

    # Optional fields
    notes: Optional[str] = Field(None, max_length=1000)
    
    # Language and labels
    language: str = Field(default="ar", pattern=r"^(ar|en)$")
    labels: Optional[InvoiceLabels] = Field(default=None)

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
                "customer_name_ar": "مؤسسة التجارة المتطورة",
                "customer_name_en": "Advanced Trading Establishment",
                "customer_address_ar": "الرياض، المملكة العربية السعودية",
                "customer_address_en": "Riyadh, Saudi Arabia",
                "customer_vat_number": "310122393500003",
                "invoice_number": "INV-2024-001",
                "language": "ar",
                "labels": {
                    "company_name": "اسم الشركة",
                    "vat_number": "الرقم الضريبي",
                    "invoice_number": "رقم الفاتورة",
                    "date": "التاريخ",
                    "customer_info": "معلومات العميل",
                    "description": "الوصف",
                    "quantity": "الكمية",
                    "amount": "المبلغ",
                    "vat": "ض.ق.م",
                    "total": "الإجمالي",
                    "subtotal": "المجموع الفرعي",
                    "vat_total": "ضريبة القيمة المضافة (15%)",
                    "grand_total": "الإجمالي",
                    "qr_code": "رمز الاستجابة السريعة",
                    "notes": "ملاحظات"
                },
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
