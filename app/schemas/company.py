"""Company schemas for request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class CompanyBase(BaseModel):
    """Base company schema."""
    name_en: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    vat_number: str = Field(..., min_length=15, max_length=15)
    address: str = Field(..., min_length=1, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    
    @field_validator('vat_number')
    @classmethod
    def validate_vat_number(cls, v: str) -> str:
        """Validate Saudi VAT number format (15 digits starting with 3)."""
        if not re.match(r'^3\d{14}$', v):
            raise ValueError(
                'VAT number must be 15 digits starting with 3 | '
                'رقم الضريبة يجب أن يكون 15 رقماً يبدأ بـ 3'
            )
        return v


class CompanyCreate(CompanyBase):
    """Schema for creating company profile."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating company profile."""
    name_en: Optional[str] = Field(None, min_length=1, max_length=200)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    vat_number: Optional[str] = Field(None, min_length=15, max_length=15)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    
    @field_validator('vat_number')
    @classmethod
    def validate_vat_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate Saudi VAT number format if provided."""
        if v and not re.match(r'^3\d{14}$', v):
            raise ValueError(
                'VAT number must be 15 digits starting with 3 | '
                'رقم الضريبة يجب أن يكون 15 رقماً يبدأ بـ 3'
            )
        return v


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
