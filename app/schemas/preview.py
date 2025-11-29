"""Preview schemas for live preview functionality."""
from pydantic import BaseModel
from typing import List
from decimal import Decimal


class PreviewRequest(BaseModel):
    """Schema for lightweight validation in live preview."""
    line_items: List[dict]  # Don't validate deeply, just check structure

    class Config:
        json_schema_extra = {
            "example": {
                "line_items": [
                    {
                        "description": "Service",
                        "quantity": 10,
                        "unit_price": 500,
                        "vat_rate": 15
                    }
                ]
            }
        }


class PreviewResponse(BaseModel):
    """Schema for quick calculations in preview."""
    subtotal: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    is_valid: bool
    errors: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "subtotal": 5000.00,
                "vat_amount": 750.00,
                "total_amount": 5750.00,
                "is_valid": True,
                "errors": []
            }
        }
