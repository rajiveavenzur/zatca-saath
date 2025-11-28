"""Invoice schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class InvoiceHistoryResponse(BaseModel):
    """Schema for invoice history response."""
    id: UUID
    invoice_number: str
    invoice_date: datetime
    customer_name: str
    customer_vat_number: Optional[str]
    subtotal: Decimal
    total_vat: Decimal
    total_amount: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceDetailResponse(BaseModel):
    """Schema for detailed invoice response including PDF."""
    id: UUID
    invoice_number: str
    invoice_date: datetime
    customer_name: str
    customer_vat_number: Optional[str]
    customer_address: str
    subtotal: Decimal
    total_vat: Decimal
    total_amount: Decimal
    line_items: List[dict]
    qr_code_data: str
    pdf_base64: str
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Schema for paginated invoice list."""
    total: int
    page: int
    page_size: int
    invoices: List[InvoiceHistoryResponse]
