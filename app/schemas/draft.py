"""Draft schemas for invoice auto-save functionality."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class DraftCreate(BaseModel):
    """Schema for creating or updating draft."""
    draft_data: dict  # Same structure as InvoiceRequest
    name: Optional[str] = None
    is_auto_saved: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "draft_data": {
                    "invoice_number": "INV-001",
                    "customer_name_ar": "مؤسسة التجارة",
                    "customer_address_ar": "الرياض",
                    "line_items": [
                        {
                            "description": "استشارات تقنية",
                            "quantity": 10,
                            "unit_price": 500.00,
                            "vat_rate": 15.0
                        }
                    ]
                },
                "name": None,
                "is_auto_saved": True
            }
        }


class DraftResponse(BaseModel):
    """Schema for draft response."""
    id: UUID
    draft_data: dict
    name: Optional[str]
    is_auto_saved: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "draft_data": {
                    "invoice_number": "INV-001",
                    "customer_name_ar": "مؤسسة التجارة",
                    "line_items": []
                },
                "name": None,
                "is_auto_saved": True,
                "created_at": "2024-11-25T10:00:00Z",
                "updated_at": "2024-11-25T10:05:00Z"
            }
        }
