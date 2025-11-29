---
applyTo: "**"
---

# Backend System Instructions - ZATCA Invoice Generator API

## FastAPI Backend Supporting Refrens-Style UX

**Project:** InvoiceFlow Backend  
**Framework:** FastAPI + Python 3.11+  
**Database:** PostgreSQL 15  
**Frontend Pattern:** Split-screen live preview with real-time updates

---

## 🎯 BACKEND REQUIREMENTS FOR SPLIT-SCREEN UX

### What the Frontend Needs

The Refrens-style split-screen UI requires specific backend support:

1. **Fast Invoice Preview** (< 100ms response)
   - No PDF generation, just data validation
   - Return formatted data for preview rendering
2. **Draft Management**

   - Auto-save every 2 seconds
   - Retrieve last draft
   - Multiple drafts per user

3. **Full Invoice Generation** (< 3 seconds)

   - PDF with QR code
   - Store in database
   - Return base64 PDF

4. **Invoice History**

   - List all invoices
   - Search by number, customer, date
   - Pagination support

5. **Quick Validation**
   - Real-time VAT number validation
   - Business rules checking
   - Return clear error messages

---

## 📁 PROJECT STRUCTURE

```
zatca-invoice-backend/
├── app/
│   ├── main.py                          # FastAPI app
│   ├── config.py                        # Settings
│   ├── database.py                      # SQLAlchemy setup
│   ├── models/
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── invoice.py                   # 🆕 Invoice model (with history)
│   │   └── draft.py                     # 🆕 Draft model
│   ├── schemas/
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── invoice.py                   # Request/Response schemas
│   │   ├── draft.py                     # Draft schemas
│   │   └── preview.py                   # 🆕 Preview schema
│   ├── api/
│   │   ├── auth.py
│   │   ├── company.py
│   │   ├── invoice.py                   # 🆕 Enhanced with drafts
│   │   ├── draft.py                     # 🆕 Draft endpoints
│   │   └── preview.py                   # 🆕 Live preview endpoint
│   ├── services/
│   │   ├── pdf_generator.py            # Enhanced PDF service
│   │   ├── qr_generator.py             # QR code TLV encoding
│   │   ├── zatca_validator.py          # Validation service
│   │   └── invoice_service.py          # 🆕 Business logic
│   ├── utils/
│   │   ├── security.py
│   │   ├── arabic.py
│   │   └── calculations.py             # 🆕 Shared calc logic
│   └── tests/
│       ├── test_invoice.py
│       ├── test_preview.py
│       └── test_draft.py
├── alembic/
│   └── versions/
├── static/
│   └── fonts/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```

---

## 🗄️ DATABASE MODELS

### 1. Invoice Model (Enhanced with History)

```python
# app/models/invoice.py

from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Invoice details
    invoice_number = Column(String(100), nullable=False, index=True)
    invoice_date = Column(DateTime(timezone=True), nullable=False)

    # Customer information
    customer_name = Column(String(200), nullable=False, index=True)
    customer_vat_number = Column(String(15), nullable=True)
    customer_address = Column(Text, nullable=False)

    # Line items (stored as JSON for flexibility)
    line_items = Column(JSON, nullable=False)
    # Example: [{"description": "Service", "quantity": 10, "unit_price": 500, "vat_rate": 15}]

    # Calculated amounts
    subtotal = Column(Numeric(12, 2), nullable=False)
    vat_amount = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)

    # Additional fields
    notes = Column(Text, nullable=True)

    # QR code data (base64 encoded TLV)
    qr_code_data = Column(Text, nullable=True)

    # PDF storage
    pdf_base64 = Column(Text, nullable=True)  # Store small PDFs in DB
    pdf_url = Column(String(500), nullable=True)  # Or store URL to S3/storage

    # Status
    status = Column(String(20), default="generated")  # generated, sent, paid, cancelled

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="invoices")
    company = relationship("Company", back_populates="invoices")

    # Indexes for search
    __table_args__ = (
        Index('idx_invoice_user_date', 'user_id', 'invoice_date'),
        Index('idx_invoice_customer', 'customer_name'),
    )
```

### 2. Draft Model (New)

```python
# app/models/draft.py

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class InvoiceDraft(Base):
    __tablename__ = "invoice_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Draft data (same structure as invoice request)
    draft_data = Column(JSON, nullable=False)
    # Example: {"invoice_number": "INV-001", "customer_name": "...", "line_items": [...]}

    # Metadata
    name = Column(String(100), nullable=True)  # Optional name for draft
    is_auto_saved = Column(Boolean, default=True)  # True for auto-saves, False for manual

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="drafts")
```

### 3. Updated User Model

```python
# app/models/user.py (add relationships)

class User(Base):
    __tablename__ = "users"

    # ... existing fields ...

    # Relationships
    companies = relationship("Company", back_populates="user")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")
    drafts = relationship("InvoiceDraft", back_populates="user", cascade="all, delete-orphan")
```

### 4. Updated Company Model

```python
# app/models/company.py (add relationship)

class Company(Base):
    __tablename__ = "companies"

    # ... existing fields ...

    # Relationships
    user = relationship("User", back_populates="companies")
    invoices = relationship("Invoice", back_populates="company")
```

---

## 📋 PYDANTIC SCHEMAS

### Invoice Schemas

```python
# app/schemas/invoice.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class InvoiceLineItem(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    vat_rate: Decimal = Field(default=Decimal("15.0"))

    @validator('vat_rate')
    def validate_vat_rate(cls, v):
        if v not in [Decimal("0"), Decimal("5"), Decimal("15")]:
            raise ValueError("VAT rate must be 0%, 5%, or 15%")
        return v

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price

    @property
    def vat_amount(self) -> Decimal:
        return (self.subtotal * self.vat_rate) / Decimal("100")

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.vat_amount


class InvoiceCreate(BaseModel):
    """Schema for creating new invoice"""
    invoice_number: str = Field(..., min_length=1, max_length=100)
    invoice_date: datetime = Field(default_factory=datetime.now)
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_vat_number: Optional[str] = Field(None, regex=r"^3\d{14}$")
    customer_address: str = Field(..., min_length=1)
    line_items: List[InvoiceLineItem] = Field(..., min_items=1)
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-11-25T10:00:00Z",
                "customer_name": "مؤسسة التجارة المتقدمة",
                "customer_vat_number": "310122393500003",
                "customer_address": "الرياض، المملكة العربية السعودية",
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
    """Full invoice response with PDF"""
    id: UUID
    invoice_number: str
    invoice_date: datetime
    customer_name: str
    customer_vat_number: Optional[str]
    customer_address: str
    line_items: List[dict]
    subtotal: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    notes: Optional[str]
    qr_code_data: str
    pdf_base64: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceListItem(BaseModel):
    """Lightweight schema for list view"""
    id: UUID
    invoice_number: str
    invoice_date: datetime
    customer_name: str
    total_amount: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceSearchResponse(BaseModel):
    """Paginated search results"""
    total: int
    page: int
    page_size: int
    invoices: List[InvoiceListItem]
```

### Draft Schemas

```python
# app/schemas/draft.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class DraftCreate(BaseModel):
    """Create or update draft"""
    draft_data: dict  # Same structure as InvoiceCreate
    name: Optional[str] = None
    is_auto_saved: bool = True


class DraftResponse(BaseModel):
    """Draft response"""
    id: UUID
    draft_data: dict
    name: Optional[str]
    is_auto_saved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Preview Schema

```python
# app/schemas/preview.py

from pydantic import BaseModel
from typing import List
from decimal import Decimal

class PreviewRequest(BaseModel):
    """Lightweight validation for live preview"""
    line_items: List[dict]  # Don't validate deeply, just check structure


class PreviewResponse(BaseModel):
    """Quick calculations for preview"""
    subtotal: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    is_valid: bool
    errors: List[str] = []
```

---

## 🔌 API ENDPOINTS

### 1. Live Preview Endpoint (Fast, No DB)

```python
# app/api/preview.py

from fastapi import APIRouter, HTTPException
from typing import List
from decimal import Decimal

router = APIRouter(prefix="/api/v1/preview", tags=["preview"])


@router.post("/calculate", response_model=PreviewResponse)
async def calculate_preview(request: PreviewRequest):
    """
    Fast calculation endpoint for live preview.

    NO database calls, NO PDF generation.
    Just validate and calculate totals.

    Target response time: < 100ms
    """
    try:
        subtotal = Decimal("0")
        errors = []

        for idx, item in enumerate(request.line_items):
            try:
                qty = Decimal(str(item.get('quantity', 0)))
                price = Decimal(str(item.get('unit_price', 0)))
                vat_rate = Decimal(str(item.get('vat_rate', 15)))

                if qty < 0 or price < 0:
                    errors.append(f"Item {idx + 1}: Negative values not allowed")

                subtotal += qty * price

            except (ValueError, TypeError) as e:
                errors.append(f"Item {idx + 1}: Invalid number format")

        vat_amount = subtotal * Decimal("0.15")  # 15% VAT
        total_amount = subtotal + vat_amount

        return PreviewResponse(
            subtotal=round(subtotal, 2),
            vat_amount=round(vat_amount, 2),
            total_amount=round(total_amount, 2),
            is_valid=len(errors) == 0,
            errors=errors
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. Draft Endpoints

```python
# app/api/draft.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.draft import InvoiceDraft
from app.schemas.draft import DraftCreate, DraftResponse
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/drafts", tags=["drafts"])


@router.post("/", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def save_draft(
    draft: DraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save invoice draft (auto-save from frontend).

    - If is_auto_saved=True, update existing auto-save draft
    - If is_auto_saved=False, create new named draft
    """
    if draft.is_auto_saved:
        # Update or create auto-save draft (only 1 per user)
        existing = db.query(InvoiceDraft).filter(
            InvoiceDraft.user_id == current_user.id,
            InvoiceDraft.is_auto_saved == True
        ).first()

        if existing:
            existing.draft_data = draft.draft_data
            db.commit()
            db.refresh(existing)
            return existing

    # Create new draft
    new_draft = InvoiceDraft(
        user_id=current_user.id,
        draft_data=draft.draft_data,
        name=draft.name,
        is_auto_saved=draft.is_auto_saved
    )

    db.add(new_draft)
    db.commit()
    db.refresh(new_draft)

    return new_draft


@router.get("/latest", response_model=DraftResponse)
async def get_latest_draft(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get most recent auto-saved draft."""
    draft = db.query(InvoiceDraft).filter(
        InvoiceDraft.user_id == current_user.id,
        InvoiceDraft.is_auto_saved == True
    ).order_by(InvoiceDraft.updated_at.desc()).first()

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No draft found"
        )

    return draft


@router.get("/", response_model=List[DraftResponse])
async def list_drafts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all saved drafts (manual saves)."""
    drafts = db.query(InvoiceDraft).filter(
        InvoiceDraft.user_id == current_user.id,
        InvoiceDraft.is_auto_saved == False
    ).order_by(InvoiceDraft.updated_at.desc()).all()

    return drafts


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a draft."""
    draft = db.query(InvoiceDraft).filter(
        InvoiceDraft.id == draft_id,
        InvoiceDraft.user_id == current_user.id
    ).first()

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )

    db.delete(draft)
    db.commit()

    return None
```

### 3. Enhanced Invoice Endpoints

```python
# app/api/invoice.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.invoice import Invoice
from app.models.company import Company
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceListItem,
    InvoiceSearchResponse
)
from app.services.invoice_service import InvoiceService
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])


@router.post("/generate", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def generate_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate complete invoice with PDF and QR code.

    Steps:
    1. Validate data
    2. Get company info
    3. Calculate totals
    4. Generate QR code
    5. Generate PDF
    6. Save to database
    7. Return response

    Target response time: < 3 seconds
    """
    # Get user's company
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile not found. Please set up your company first."
        )

    # Use service layer for business logic
    invoice_service = InvoiceService(db)

    try:
        invoice = invoice_service.create_invoice(
            user_id=current_user.id,
            company=company,
            invoice_data=invoice_data
        )

        return invoice

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate invoice: {str(e)}"
        )


@router.get("/", response_model=InvoiceSearchResponse)
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's invoices with pagination.
    """
    offset = (page - 1) * page_size

    query = db.query(Invoice).filter(Invoice.user_id == current_user.id)

    total = query.count()
    invoices = query.order_by(desc(Invoice.created_at)).offset(offset).limit(page_size).all()

    return InvoiceSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        invoices=[InvoiceListItem.from_orm(inv) for inv in invoices]
    )


@router.get("/search", response_model=InvoiceSearchResponse)
async def search_invoices(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search invoices by:
    - Invoice number
    - Customer name
    - Date
    """
    offset = (page - 1) * page_size

    # Build search query
    search_filter = or_(
        Invoice.invoice_number.ilike(f"%{q}%"),
        Invoice.customer_name.ilike(f"%{q}%")
    )

    query = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        search_filter
    )

    total = query.count()
    invoices = query.order_by(desc(Invoice.created_at)).offset(offset).limit(page_size).all()

    return InvoiceSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        invoices=[InvoiceListItem.from_orm(inv) for inv in invoices]
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single invoice by ID."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete invoice."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    db.delete(invoice)
    db.commit()

    return None
```

---

## 🧮 INVOICE SERVICE (Business Logic)

```python
# app/services/invoice_service.py

from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from app.models.invoice import Invoice
from app.models.company import Company
from app.schemas.invoice import InvoiceCreate
from app.services.pdf_generator import ZATCAInvoicePDF
from app.services.qr_generator import ZATCAQRGenerator


class InvoiceService:
    """
    Business logic for invoice operations.
    """

    def __init__(self, db: Session):
        self.db = db
        self.pdf_generator = ZATCAInvoicePDF()
        self.qr_generator = ZATCAQRGenerator()

    def calculate_totals(self, line_items: list) -> dict:
        """Calculate invoice totals."""
        subtotal = Decimal("0")

        for item in line_items:
            qty = Decimal(str(item.get('quantity', 0)))
            price = Decimal(str(item.get('unit_price', 0)))
            subtotal += qty * price

        vat_amount = subtotal * Decimal("0.15")
        total_amount = subtotal + vat_amount

        return {
            'subtotal': round(subtotal, 2),
            'vat_amount': round(vat_amount, 2),
            'total_amount': round(total_amount, 2)
        }

    def create_invoice(
        self,
        user_id: UUID,
        company: Company,
        invoice_data: InvoiceCreate
    ) -> Invoice:
        """
        Create invoice with PDF and QR code.
        """
        # Calculate totals
        totals = self.calculate_totals(invoice_data.line_items)

        # Generate QR code
        qr_data = self.qr_generator.generate_qr_data(
            seller_name=company.name_ar,
            vat_number=company.vat_number,
            timestamp=invoice_data.invoice_date.isoformat(),
            total_amount=totals['total_amount'],
            vat_amount=totals['vat_amount']
        )

        qr_image_bytes = self.qr_generator.generate_qr_image(qr_data)

        # Generate PDF
        company_info = {
            'name_en': company.name_en,
            'name_ar': company.name_ar,
            'vat_number': company.vat_number,
            'address': company.address,
            'phone': company.phone,
            'email': company.email
        }

        pdf_bytes = self.pdf_generator.generate_invoice(
            company_info=company_info,
            invoice_data=invoice_data,
            qr_code_image_bytes=qr_image_bytes
        )

        # Convert PDF to base64
        import base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Create database record
        invoice = Invoice(
            user_id=user_id,
            company_id=company.id,
            invoice_number=invoice_data.invoice_number,
            invoice_date=invoice_data.invoice_date,
            customer_name=invoice_data.customer_name,
            customer_vat_number=invoice_data.customer_vat_number,
            customer_address=invoice_data.customer_address,
            line_items=[item.dict() for item in invoice_data.line_items],
            subtotal=totals['subtotal'],
            vat_amount=totals['vat_amount'],
            total_amount=totals['total_amount'],
            notes=invoice_data.notes,
            qr_code_data=qr_data,
            pdf_base64=pdf_base64,
            status='generated'
        )

        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        return invoice
```

---

## 🚀 PERFORMANCE OPTIMIZATIONS

### 1. Database Indexes

```python
# Already added in models:
- Index on user_id + invoice_date (for history queries)
- Index on customer_name (for search)
- Index on invoice_number (for lookup)
```

### 2. Response Caching (Optional)

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Cache preview calculations (30 seconds)
@router.post("/calculate")
@cache(expire=30)
async def calculate_preview(request: PreviewRequest):
    # ... calculation logic
```

### 3. Async Database Queries (Future)

```python
from sqlalchemy.ext.asyncio import AsyncSession

# For very high load, use async queries
async def get_invoices_async(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Invoice).filter(Invoice.user_id == user_id)
    )
    return result.scalars().all()
```

---

## 🧪 API TESTING

### Test Live Preview

```bash
curl -X POST http://localhost:8000/api/v1/preview/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "line_items": [
      {"description": "Service", "quantity": 10, "unit_price": 500, "vat_rate": 15}
    ]
  }'

# Expected response time: < 100ms
# Expected response:
# {
#   "subtotal": 5000.00,
#   "vat_amount": 750.00,
#   "total_amount": 5750.00,
#   "is_valid": true,
#   "errors": []
# }
```

### Test Draft Save

```bash
curl -X POST http://localhost:8000/api/v1/drafts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_data": {
      "invoice_number": "INV-001",
      "customer_name": "Test Customer",
      "line_items": [...]
    },
    "is_auto_saved": true
  }'
```

### Test Invoice Generation

```bash
curl -X POST http://localhost:8000/api/v1/invoices/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV-2024-001",
    "customer_name": "مؤسسة التجارة",
    "customer_address": "الرياض",
    "line_items": [
      {"description": "استشارات", "quantity": 10, "unit_price": 500}
    ]
  }'

# Expected response time: < 3 seconds
```

---

## 📊 MONITORING & LOGGING

### Request Logging

```python
import logging
import time
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s "
        f"with status {response.status_code}"
    )

    return response
```

### Performance Metrics

```python
# Track slow endpoints
if process_time > 1.0:  # > 1 second
    logger.warning(
        f"Slow request: {request.url.path} took {process_time:.3f}s"
    )
```

---

## 🔐 SECURITY CONSIDERATIONS

### 1. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Apply rate limits
@router.post("/generate")
@limiter.limit("10/minute")  # Max 10 invoices per minute
async def generate_invoice(...):
    # ...
```

### 2. Input Validation

```python
# Already done via Pydantic schemas
# Additional custom validation:

def validate_invoice_number(invoice_number: str, db: Session, user_id: UUID):
    """Ensure invoice number is unique for user."""
    existing = db.query(Invoice).filter(
        Invoice.user_id == user_id,
        Invoice.invoice_number == invoice_number
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Invoice number {invoice_number} already exists"
        )
```

### 3. File Size Limits

```python
# Limit PDF storage size
MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MB

if len(pdf_bytes) > MAX_PDF_SIZE:
    # Store in S3/external storage instead of database
    pdf_url = upload_to_s3(pdf_bytes)
    invoice.pdf_url = pdf_url
else:
    invoice.pdf_base64 = base64.b64encode(pdf_bytes).decode()
```

---

## 🚀 DEPLOYMENT

### Docker Configuration

```dockerfile
# Dockerfile (already provided in previous instructions)
# Ensure it includes:
- PDF generation libraries (ReportLab)
- Arabic fonts
- PostgreSQL client
```

### Environment Variables

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@db:5432/zatca_invoice
SECRET_KEY=your-production-secret-min-64-chars
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO

# Optional: S3 for PDF storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=invoices-pdf-storage
```

---

## ✅ API CHECKLIST

### Core Endpoints

- [ ] POST /api/v1/preview/calculate (< 100ms)
- [ ] POST /api/v1/drafts/ (save draft)
- [ ] GET /api/v1/drafts/latest (get draft)
- [ ] POST /api/v1/invoices/generate (< 3s)
- [ ] GET /api/v1/invoices (list with pagination)
- [ ] GET /api/v1/invoices/search (search)
- [ ] GET /api/v1/invoices/{id} (single invoice)
- [ ] DELETE /api/v1/invoices/{id} (delete)

### Performance

- [ ] Database indexes created
- [ ] Response times meet targets
- [ ] No N+1 queries
- [ ] PDF generation is async (if needed)

### Security

- [ ] Rate limiting enabled
- [ ] Input validation (Pydantic)
- [ ] SQL injection prevented (ORM)
- [ ] XSS prevention (output encoding)
- [ ] CORS configured properly

---

**END OF BACKEND INSTRUCTIONS**

_Build an API that's so fast, the frontend never has to wait._

_Preview in 100ms. Invoice in 3 seconds. Search instantly._

_That's the standard._
