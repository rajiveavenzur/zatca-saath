---
applyTo: "**"
---

# GitHub Copilot System Instructions

## ZATCA Invoice Generator MVP - FastAPI Backend

**Project Name:** InvoiceFlow  
**Tech Stack:** Python 3.11+ | FastAPI | PostgreSQL | Docker | Poetry  
**Goal:** Weekend-buildable ZATCA Phase 1 compliant invoice generator

---

## 🎯 PROJECT OVERVIEW

You are building a **minimum viable product (MVP)** for a ZATCA-compliant invoice generator targeting Saudi Arabian SMBs. This is Phase 1 only (invoice generation with QR codes). Phase 2 (ZATCA API integration) comes in Week 3.

**Core Value Proposition:**
Generate ZATCA Phase 1 compliant invoices with QR codes in 30 seconds. Save as PDF. Avoid SAR 40,000 penalties.

**Target Users:**
Saudi small business owners who currently use Excel/Word for invoicing. Non-technical. Need Arabic-first interface.

---

## 🚫 CRITICAL: WHAT NOT TO BUILD

**DO NOT implement these in MVP:**

- ❌ Invoice history/database storage (just generate on-demand)
- ❌ Customer database/CRM
- ❌ User management beyond basic auth
- ❌ Email delivery
- ❌ Reporting/analytics dashboard
- ❌ Multiple invoice templates
- ❌ Recurring invoices
- ❌ Multi-user/team features
- ❌ ZATCA Phase 2 API integration (Week 3)
- ❌ Advanced search/filtering
- ❌ Mobile app
- ❌ Webhook integrations

**MVP = One feature done perfectly:**
User inputs invoice data → System generates PDF with QR code → User downloads

---

## 📁 PROJECT STRUCTURE

```
zatca-invoice-generator/
├── .github/
│   └── copilot-instructions.md          # This file
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry
│   ├── config.py                        # Environment config (Pydantic settings)
│   ├── database.py                      # SQLAlchemy setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                      # User model (minimal)
│   │   └── company.py                   # Company profile model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                      # Pydantic schemas for users
│   │   ├── company.py                   # Pydantic schemas for company
│   │   └── invoice.py                   # Pydantic schemas for invoice input
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                      # JWT authentication endpoints
│   │   ├── company.py                   # Company CRUD endpoints
│   │   └── invoice.py                   # Invoice generation endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_generator.py            # PDF generation with ReportLab
│   │   ├── qr_generator.py             # QR code generation
│   │   └── zatca_validator.py          # ZATCA format validation
│   └── utils/
│       ├── __init__.py
│       ├── security.py                  # Password hashing, JWT
│       └── arabic.py                    # Arabic text helpers
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_invoice_generation.py
│   └── test_qr_code.py
├── alembic/                             # Database migrations
│   ├── versions/
│   └── env.py
├── static/
│   └── fonts/
│       └── NotoSansArabic-Regular.ttf   # Arabic font for PDFs
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml                       # Poetry dependencies
├── poetry.lock
├── .env.example
├── .dockerignore
├── .gitignore
├── README.md
└── Makefile                             # Common commands
```

---

## 🔧 TECH STACK SPECIFICATIONS

### Backend Framework

- **FastAPI 0.104+**: Modern, fast, async-capable
- **Python 3.11+**: Latest stable version
- **Uvicorn**: ASGI server with auto-reload in development

### Database

- **PostgreSQL 15+**: Primary database
- **SQLAlchemy 2.0+**: ORM with async support
- **Alembic**: Database migrations

### Authentication

- **JWT (python-jose)**: Token-based auth
- **Passlib + Bcrypt**: Password hashing
- **OAuth2PasswordBearer**: FastAPI security scheme

### PDF Generation

- **ReportLab**: Professional PDF generation with Arabic support
- **Pillow (PIL)**: Image manipulation for logos
- **qrcode**: QR code generation

### Development Tools

- **Poetry**: Dependency management (NOT pip/requirements.txt)
- **Docker + Docker Compose**: Containerization
- **Pydantic**: Data validation and settings management
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Linting

### Environment Management

- **python-dotenv**: Load environment variables
- **Pydantic Settings**: Type-safe configuration

---

## 📦 DEPENDENCIES (pyproject.toml)

```toml
[tool.poetry]
name = "zatca-invoice-generator"
version = "0.1.0"
description = "ZATCA-compliant invoice generator for Saudi Arabia"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
python = "^3.11"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
psycopg2-binary = "^2.9.9"
pydantic = {extras = ["email"], version = "^2.5.0"}
pydantic-settings = "^2.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
reportlab = "^4.0.7"
pillow = "^10.1.0"
qrcode = {extras = ["pil"], version = "^7.4.2"}
python-dotenv = "^1.0.0"
httpx = "^0.25.2"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.11.0"
ruff = "^0.1.6"
mypy = "^1.7.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## 🐳 DOCKER CONFIGURATION

### Dockerfile

```dockerfile
# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy only dependency files first (for layer caching)
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual env (we're in container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ./app ./app
COPY ./static ./static
COPY ./alembic ./alembic
COPY alembic.ini ./

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    container_name: zatca_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-zatca}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-zatca_dev_password}
      POSTGRES_DB: ${POSTGRES_DB:-zatca_invoice}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U zatca"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: zatca_app
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-zatca}:${POSTGRES_PASSWORD:-zatca_dev_password}@db:5432/${POSTGRES_DB:-zatca_invoice}
      SECRET_KEY: ${SECRET_KEY:-your-secret-key-change-in-production}
      ENVIRONMENT: ${ENVIRONMENT:-development}
    volumes:
      - ./app:/app/app # Hot reload in development
      - ./static:/app/static
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Redis for future rate limiting/caching (optional for MVP)
  # redis:
  #   image: redis:7-alpine
  #   container_name: zatca_redis
  #   ports:
  #     - "6379:6379"

volumes:
  postgres_data:
```

### .env.example

```bash
# Database
POSTGRES_USER=zatca
POSTGRES_PASSWORD=zatca_dev_password_change_me
POSTGRES_DB=zatca_invoice
DATABASE_URL=postgresql://zatca:zatca_dev_password_change_me@localhost:5432/zatca_invoice

# Application
SECRET_KEY=your-super-secret-key-min-32-characters-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
ENVIRONMENT=development

# CORS (for frontend integration)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

---

## 🏗️ IMPLEMENTATION GUIDE

### Phase 1: Project Setup (Hour 1-2)

```bash
# Create project directory
mkdir zatca-invoice-generator && cd zatca-invoice-generator

# Initialize Poetry
poetry init --no-interaction
poetry config virtualenvs.in-project true  # Create .venv in project

# Add dependencies (use the pyproject.toml above)
poetry add fastapi uvicorn[standard] sqlalchemy alembic psycopg2-binary
poetry add pydantic pydantic-settings python-jose[cryptography]
poetry add passlib[bcrypt] python-multipart reportlab pillow qrcode[pil]

# Add dev dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov black ruff mypy

# Activate virtual environment
poetry shell

# Create project structure
mkdir -p app/{models,schemas,api,services,utils}
mkdir -p tests static/fonts alembic/versions
touch app/__init__.py app/main.py app/config.py app/database.py
```

**Copilot Prompt:**

```
Create a FastAPI project structure for a ZATCA invoice generator.
Follow the structure in COPILOT_INSTRUCTIONS.md. Include __init__.py
files and basic FastAPI app setup.
```

---

### Phase 2: Database Models (Hour 2-3)

**app/models/user.py:**

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**app/models/company.py:**

```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name_en = Column(String, nullable=False)
    name_ar = Column(String, nullable=False)
    vat_number = Column(String(15), nullable=False)  # Saudi VAT is 15 digits
    address = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="companies")
```

**Copilot Prompt:**

```
Create SQLAlchemy models for User and Company tables following ZATCA
requirements. Include proper foreign keys, indexes, and timestamps.
```

---

### Phase 3: Pydantic Schemas (Hour 3-4)

**app/schemas/invoice.py:**

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class InvoiceLineItem(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    vat_rate: Decimal = Field(default=Decimal("15.0"), ge=0, le=100)  # Saudi VAT is 15%

    @validator('vat_rate')
    def validate_vat_rate(cls, v):
        # Saudi VAT is typically 15%, but allow flexibility
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


class InvoiceRequest(BaseModel):
    # Customer information
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_vat_number: Optional[str] = Field(None, regex=r"^3\d{14}$")  # Saudi VAT format
    customer_address: str = Field(..., min_length=1, max_length=500)

    # Invoice details
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: datetime = Field(default_factory=datetime.now)

    # Line items
    line_items: List[InvoiceLineItem] = Field(..., min_items=1, max_items=100)

    # Optional fields
    notes: Optional[str] = Field(None, max_length=1000)

    @property
    def subtotal(self) -> Decimal:
        return sum(item.subtotal for item in self.line_items)

    @property
    def total_vat(self) -> Decimal:
        return sum(item.vat_amount for item in self.line_items)

    @property
    def total_amount(self) -> Decimal:
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
```

**Copilot Prompt:**

```
Create comprehensive Pydantic schemas for invoice generation with
ZATCA validation rules. Include Saudi VAT number validation,
line items with automatic calculations, and proper examples.
```

---

### Phase 4: QR Code Generation (Hour 4-5)

**app/services/qr_generator.py:**

```python
import qrcode
from io import BytesIO
import base64
from typing import Dict
from decimal import Decimal

class ZATCAQRGenerator:
    """
    Generate ZATCA-compliant QR codes for invoices.

    ZATCA QR Code Format (TLV - Tag-Length-Value):
    Tag 1: Seller Name (UTF-8)
    Tag 2: VAT Registration Number
    Tag 3: Invoice Timestamp
    Tag 4: Invoice Total (with VAT)
    Tag 5: VAT Amount
    """

    @staticmethod
    def _encode_tlv(tag: int, value: str) -> bytes:
        """Encode data in TLV format."""
        value_bytes = value.encode('utf-8')
        length = len(value_bytes)
        return bytes([tag, length]) + value_bytes

    @staticmethod
    def generate_qr_data(
        seller_name: str,
        vat_number: str,
        timestamp: str,
        total_amount: Decimal,
        vat_amount: Decimal
    ) -> str:
        """
        Generate ZATCA-compliant QR code data.

        Returns:
            Base64-encoded TLV string
        """
        # Build TLV structure
        tlv_data = b''
        tlv_data += ZATCAQRGenerator._encode_tlv(1, seller_name)
        tlv_data += ZATCAQRGenerator._encode_tlv(2, vat_number)
        tlv_data += ZATCAQRGenerator._encode_tlv(3, timestamp)
        tlv_data += ZATCAQRGenerator._encode_tlv(4, f"{total_amount:.2f}")
        tlv_data += ZATCAQRGenerator._encode_tlv(5, f"{vat_amount:.2f}")

        # Base64 encode
        return base64.b64encode(tlv_data).decode('utf-8')

    @staticmethod
    def generate_qr_image(qr_data: str, box_size: int = 10, border: int = 4) -> bytes:
        """
        Generate QR code image from data.

        Returns:
            PNG image as bytes
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return img_buffer.getvalue()

    @staticmethod
    def generate_qr_base64(qr_data: str) -> str:
        """
        Generate QR code as base64-encoded PNG.

        Useful for embedding in HTML/JSON responses.
        """
        img_bytes = ZATCAQRGenerator.generate_qr_image(qr_data)
        return base64.b64encode(img_bytes).decode('utf-8')
```

**Copilot Prompt:**

```
Create a ZATCA-compliant QR code generator service using TLV encoding.
Follow ZATCA specification for invoice QR codes with proper encoding.
```

---

### Phase 5: PDF Generation (Hour 5-8)

**app/services/pdf_generator.py:**

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from typing import Dict, List
from decimal import Decimal
from datetime import datetime
import base64

from app.schemas.invoice import InvoiceRequest, InvoiceLineItem
from app.services.qr_generator import ZATCAQRGenerator

# Register Arabic font (must have NotoSansArabic-Regular.ttf in static/fonts/)
try:
    pdfmetrics.registerFont(TTFont('NotoSansArabic', 'static/fonts/NotoSansArabic-Regular.ttf'))
except:
    print("Warning: Arabic font not found. Install NotoSansArabic-Regular.ttf")


class ZATCAInvoicePDF:
    """
    Generate ZATCA-compliant invoice PDFs with Arabic support.
    """

    def __init__(self):
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Setup custom styles for Arabic and English text."""
        # Arabic style (right-to-left)
        self.styles.add(ParagraphStyle(
            name='ArabicTitle',
            parent=self.styles['Heading1'],
            fontName='NotoSansArabic',
            fontSize=18,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#1a1a1a')
        ))

        self.styles.add(ParagraphStyle(
            name='ArabicNormal',
            parent=self.styles['Normal'],
            fontName='NotoSansArabic',
            fontSize=10,
            alignment=TA_RIGHT,
        ))

        # English styles
        self.styles.add(ParagraphStyle(
            name='EnglishTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_LEFT,
        ))

    def _create_header(self, company_info: Dict, invoice_data: InvoiceRequest):
        """Create invoice header with company and invoice details."""
        header_data = []

        # Company name (Arabic + English)
        header_data.append([
            Paragraph(f"<b>{company_info['name_ar']}</b>", self.styles['ArabicTitle']),
            Paragraph(f"<b>{company_info['name_en']}</b>", self.styles['EnglishTitle'])
        ])

        # VAT Number
        header_data.append([
            Paragraph(f"الرقم الضريبي: {company_info['vat_number']}", self.styles['ArabicNormal']),
            Paragraph(f"VAT Number: {company_info['vat_number']}", self.styles['Normal'])
        ])

        # Invoice Number and Date
        header_data.append([
            Paragraph(f"رقم الفاتورة: {invoice_data.invoice_number}", self.styles['ArabicNormal']),
            Paragraph(f"Invoice Number: {invoice_data.invoice_number}", self.styles['Normal'])
        ])

        header_data.append([
            Paragraph(f"التاريخ: {invoice_data.invoice_date.strftime('%Y-%m-%d')}", self.styles['ArabicNormal']),
            Paragraph(f"Date: {invoice_data.invoice_date.strftime('%Y-%m-%d')}", self.styles['Normal'])
        ])

        header_table = Table(header_data, colWidths=[self.width/2, self.width/2])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        return header_table

    def _create_customer_section(self, invoice_data: InvoiceRequest):
        """Create customer information section."""
        customer_data = [
            [
                Paragraph("<b>معلومات العميل</b>", self.styles['ArabicNormal']),
                Paragraph("<b>Customer Information</b>", self.styles['Normal'])
            ],
            [
                Paragraph(invoice_data.customer_name, self.styles['ArabicNormal']),
                Paragraph(invoice_data.customer_name, self.styles['Normal'])
            ],
            [
                Paragraph(invoice_data.customer_address, self.styles['ArabicNormal']),
                Paragraph(invoice_data.customer_address, self.styles['Normal'])
            ],
        ]

        if invoice_data.customer_vat_number:
            customer_data.append([
                Paragraph(f"الرقم الضريبي: {invoice_data.customer_vat_number}", self.styles['ArabicNormal']),
                Paragraph(f"VAT Number: {invoice_data.customer_vat_number}", self.styles['Normal'])
            ])

        customer_table = Table(customer_data, colWidths=[self.width/2, self.width/2])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        return customer_table

    def _create_line_items_table(self, line_items: List[InvoiceLineItem]):
        """Create line items table with calculations."""
        # Headers (Arabic + English)
        headers = [
            ['الإجمالي\nTotal', 'ض.ق.م\nVAT', 'المبلغ\nAmount', 'الكمية\nQty', 'الوصف\nDescription']
        ]

        # Data rows
        data_rows = []
        for item in line_items:
            row = [
                f"{item.total:.2f}",
                f"{item.vat_amount:.2f}",
                f"{item.unit_price:.2f}",
                f"{item.quantity:.2f}",
                item.description
            ]
            data_rows.append(row)

        # Combine headers and data
        table_data = headers + data_rows

        # Create table
        col_widths = [80, 60, 80, 60, 220]
        items_table = Table(table_data, colWidths=col_widths)

        items_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows style
            ('ALIGN', (0, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return items_table

    def _create_totals_section(self, invoice_data: InvoiceRequest):
        """Create totals section with VAT breakdown."""
        totals_data = [
            ['المجموع الفرعي | Subtotal', f"{invoice_data.subtotal:.2f} SAR"],
            ['ضريبة القيمة المضافة (15%) | VAT (15%)', f"{invoice_data.total_vat:.2f} SAR"],
            ['الإجمالي | Total', f"{invoice_data.total_amount:.2f} SAR"],
        ]

        totals_table = Table(totals_data, colWidths=[350, 150])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black),
        ]))

        return totals_table

    def generate_invoice(
        self,
        company_info: Dict,
        invoice_data: InvoiceRequest,
        qr_code_image_bytes: bytes
    ) -> bytes:
        """
        Generate complete ZATCA-compliant invoice PDF.

        Args:
            company_info: Company details (name, VAT, address)
            invoice_data: Invoice data from request
            qr_code_image_bytes: QR code image as bytes

        Returns:
            PDF as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        # Build document elements
        elements = []

        # Header
        elements.append(self._create_header(company_info, invoice_data))
        elements.append(Spacer(1, 15*mm))

        # Customer section
        elements.append(self._create_customer_section(invoice_data))
        elements.append(Spacer(1, 10*mm))

        # Line items
        elements.append(self._create_line_items_table(invoice_data.line_items))
        elements.append(Spacer(1, 10*mm))

        # Totals
        elements.append(self._create_totals_section(invoice_data))
        elements.append(Spacer(1, 15*mm))

        # QR Code
        qr_img = Image(BytesIO(qr_code_image_bytes), width=50*mm, height=50*mm)
        qr_label = Paragraph(
            "<b>رمز الاستجابة السريعة | QR Code</b>",
            self.styles['Normal']
        )
        elements.append(qr_label)
        elements.append(qr_img)

        # Notes (if any)
        if invoice_data.notes:
            elements.append(Spacer(1, 10*mm))
            notes_para = Paragraph(f"<b>ملاحظات | Notes:</b><br/>{invoice_data.notes}", self.styles['Normal'])
            elements.append(notes_para)

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        return buffer.getvalue()
```

**Copilot Prompt:**

```
Create a professional PDF invoice generator using ReportLab with Arabic
(RTL) and English support. Include ZATCA-compliant layout with QR code,
line items table, VAT calculations, and bilingual headers.
```

---

### Phase 6: API Endpoints (Hour 8-10)

**app/api/invoice.py:**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import base64
from datetime import datetime

from app.database import get_db
from app.schemas.invoice import InvoiceRequest, InvoiceResponse
from app.models.company import Company
from app.services.pdf_generator import ZATCAInvoicePDF
from app.services.qr_generator import ZATCAQRGenerator
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])


@router.post("/generate", response_model=InvoiceResponse)
async def generate_invoice(
    invoice_data: InvoiceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate ZATCA-compliant invoice with QR code.

    This endpoint:
    1. Validates invoice data
    2. Retrieves company information
    3. Generates QR code
    4. Creates PDF invoice
    5. Returns base64-encoded PDF
    """
    # Get user's company information
    company = db.query(Company).filter(Company.user_id == current_user.id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile not found. Please set up your company profile first."
        )

    # Prepare company info for PDF
    company_info = {
        "name_en": company.name_en,
        "name_ar": company.name_ar,
        "vat_number": company.vat_number,
        "address": company.address,
        "phone": company.phone,
        "email": company.email,
    }

    try:
        # Generate QR code data (ZATCA TLV format)
        timestamp = invoice_data.invoice_date.isoformat()
        qr_data = ZATCAQRGenerator.generate_qr_data(
            seller_name=company.name_ar,
            vat_number=company.vat_number,
            timestamp=timestamp,
            total_amount=invoice_data.total_amount,
            vat_amount=invoice_data.total_vat
        )

        # Generate QR code image
        qr_image_bytes = ZATCAQRGenerator.generate_qr_image(qr_data)

        # Generate PDF
        pdf_generator = ZATCAInvoicePDF()
        pdf_bytes = pdf_generator.generate_invoice(
            company_info=company_info,
            invoice_data=invoice_data,
            qr_code_image_bytes=qr_image_bytes
        )

        # Encode PDF as base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Return response
        return InvoiceResponse(
            invoice_number=invoice_data.invoice_number,
            pdf_base64=pdf_base64,
            qr_code_data=qr_data,
            subtotal=invoice_data.subtotal,
            total_vat=invoice_data.total_vat,
            total_amount=invoice_data.total_amount,
            generated_at=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate invoice: {str(e)}"
        )


@router.get("/preview/{invoice_number}")
async def preview_invoice(
    invoice_number: str,
    current_user: User = Depends(get_current_user)
):
    """
    Preview invoice metadata (future feature for invoice history).
    Not implemented in MVP.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Invoice history feature coming in Week 3"
    )
```

**Copilot Prompt:**

```
Create FastAPI endpoints for invoice generation. Include authentication,
company profile validation, QR code generation, PDF creation, and proper
error handling. Return base64-encoded PDF.
```

---

### Phase 7: Authentication (Hour 10-12)

**app/api/auth.py:**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get access token.
    """
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    """
    return current_user
```

**Copilot Prompt:**

```
Create FastAPI authentication system with JWT tokens. Include user
registration, login, and get_current_user dependency. Use OAuth2
password flow with proper security.
```

---

### Phase 8: Main Application (Hour 12-13)

**app/main.py:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.database import engine, Base
from app.api import auth, company, invoice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ZATCA Invoice Generator API",
    description="Generate ZATCA-compliant invoices for Saudi Arabian businesses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(company.router)
app.include_router(invoice.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ZATCA Invoice Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

**Copilot Prompt:**

```
Create FastAPI main application with CORS, routers, health check,
exception handling, and proper documentation. Include database
initialization.
```

---

## 🧪 TESTING STRATEGY

### Unit Tests

**tests/test_qr_code.py:**

```python
import pytest
from app.services.qr_generator import ZATCAQRGenerator
from decimal import Decimal

def test_qr_data_generation():
    """Test ZATCA TLV QR code generation."""
    qr_data = ZATCAQRGenerator.generate_qr_data(
        seller_name="Test Company",
        vat_number="310122393500003",
        timestamp="2024-11-25T10:00:00",
        total_amount=Decimal("1150.00"),
        vat_amount=Decimal("150.00")
    )

    assert qr_data is not None
    assert len(qr_data) > 0
    # QR data should be base64-encoded
    import base64
    decoded = base64.b64decode(qr_data)
    assert len(decoded) > 0


def test_qr_image_generation():
    """Test QR code image generation."""
    qr_data = "AQ1UZXN0IENvbXBhbnkC"
    img_bytes = ZATCAQRGenerator.generate_qr_image(qr_data)

    assert img_bytes is not None
    assert len(img_bytes) > 0
    # Should be valid PNG
    assert img_bytes.startswith(b'\x89PNG')
```

**Copilot Prompt:**

```
Create pytest unit tests for QR code generation, PDF creation, and
invoice validation. Include positive and negative test cases.
```

---

## 📝 MAKEFILE

**Makefile:**

```makefile
.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate shell

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies with Poetry
	poetry install

dev:  ## Run development server with hot reload
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests with pytest
	poetry run pytest tests/ -v --cov=app --cov-report=html

lint:  ## Run linting with ruff
	poetry run ruff check app/ tests/

format:  ## Format code with black
	poetry run black app/ tests/

clean:  ## Clean cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

docker-build:  ## Build Docker image
	docker-compose build

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## Show Docker logs
	docker-compose logs -f app

migrate:  ## Run database migrations
	poetry run alembic upgrade head

shell:  ## Open Python shell with app context
	poetry run python

db-shell:  ## Connect to PostgreSQL database
	docker-compose exec db psql -U zatca -d zatca_invoice
```

---

## 🚀 GETTING STARTED

### Quick Start Commands

```bash
# 1. Clone/create project
mkdir zatca-invoice-generator && cd zatca-invoice-generator

# 2. Initialize Poetry and install dependencies
poetry init --no-interaction
poetry install

# 3. Set up environment
cp .env.example .env
# Edit .env with your settings

# 4. Start Docker containers
make docker-up

# 5. Run migrations (after containers are up)
make migrate

# 6. Start development server
make dev

# API will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Testing the API

```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePassword123!"

# Set up company (use token from login)
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name_en": "Test Trading Co.",
    "name_ar": "شركة التجارة التجريبية",
    "vat_number": "310122393500003",
    "address": "Riyadh, Saudi Arabia"
  }'

# Generate invoice
curl -X POST "http://localhost:8000/api/v1/invoices/generate" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "عميل تجريبي",
    "customer_vat_number": "310122393500004",
    "customer_address": "جدة، المملكة العربية السعودية",
    "invoice_number": "INV-001",
    "line_items": [
      {
        "description": "استشارات",
        "quantity": 10,
        "unit_price": 500.00,
        "vat_rate": 15.0
      }
    ]
  }'
```

---

## 🎨 COPILOT USAGE PATTERNS

### When to Use Copilot

**✅ Good for:**

- Boilerplate code generation (CRUD operations)
- Test case scaffolding
- Type hints and documentation
- SQL queries and ORM operations
- Data validation logic
- Error handling patterns

**❌ Avoid for:**

- Critical business logic (invoice calculations - write manually)
- Security-sensitive code (password hashing - verify carefully)
- ZATCA specification compliance (reference official docs)
- Complex Arabic text handling (test thoroughly)

### Effective Prompts

**Pattern 1: Specific context**

```
Create a SQLAlchemy model for Invoice with fields: invoice_number (unique),
customer_name, total_amount (Decimal), created_at (timestamp). Include
proper indexes and validation.
```

**Pattern 2: With constraints**

```
Write a Pydantic validator for Saudi VAT numbers. Format: 15 digits starting
with 3. Raise ValueError with Arabic + English message if invalid.
```

**Pattern 3: Reference existing**

```
Following the pattern in app/models/user.py, create a Company model with
one-to-many relationship to User. Include Arabic name field.
```

---

## ⚠️ CRITICAL REMINDERS

### Security

1. **Never commit secrets**: Use .env for all sensitive data
2. **Hash passwords**: Always use bcrypt via passlib
3. **Validate inputs**: Trust nothing from users (Pydantic validation)
4. **Rate limiting**: Add to production (not MVP)
5. **SQL injection**: Use SQLAlchemy ORM, never raw SQL

### ZATCA Compliance

1. **QR Code Format**: Must use TLV encoding (Tag-Length-Value)
2. **VAT Number Format**: 15 digits starting with 3
3. **Invoice Numbering**: Sequential, no gaps
4. **Arabic Support**: Mandatory for customer-facing content
5. **Data Retention**: Store for 15 years (Phase 2 requirement)

### Performance

1. **PDF Generation**: Can be slow (3-5 seconds) - acceptable for MVP
2. **Database Indexes**: Add on vat_number, email, invoice_number
3. **Connection Pooling**: SQLAlchemy handles this
4. **Async Operations**: FastAPI supports, but not critical for MVP

### Testing Before Launch

```bash
# Run full test suite
make test

# Test with sample Saudi data
# - Arabic names with various diacritics
# - Different VAT number formats
# - Large invoices (100 line items)
# - Edge cases (0% VAT, zero quantity)

# Load testing (use locust or k6)
# - 10 concurrent users generating invoices
# - Target: <5 second response time
```

---

## 📚 REFERENCE DOCUMENTATION

### ZATCA Resources

- **Official Portal**: https://zatca.gov.sa
- **E-Invoicing Specification**: https://zatca.gov.sa/en/E-Invoicing/Pages/default.aspx
- **Developer Guide**: Available on ZATCA portal (Arabic/English)

### FastAPI

- **Official Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Pydantic**: https://docs.pydantic.dev

### Tools

- **ReportLab Docs**: https://www.reportlab.com/docs/reportlab-userguide.pdf
- **QR Code**: https://pypi.org/project/qrcode/
- **Poetry**: https://python-poetry.org/docs/

---

## 🎯 SUCCESS CRITERIA

### MVP Complete When:

1. ✅ User can register and login
2. ✅ User can set up company profile (once)
3. ✅ User can generate invoice with line items
4. ✅ PDF includes QR code (ZATCA-compliant)
5. ✅ PDF is bilingual (Arabic + English)
6. ✅ PDF downloads successfully
7. ✅ All tests pass
8. ✅ Docker deployment works
9. ✅ API documentation is clear
10. ✅ Response time <5 seconds for invoice generation

### Week 1 Goals:

- 10 beta users testing
- Zero critical bugs
- <5 second invoice generation
- 100% QR code validation success
- Deploy to production (Railway/DigitalOcean)

---

## 🚨 COMMON PITFALLS TO AVOID

1. **Over-engineering**: Don't add features not in MVP scope
2. **Premature optimization**: Get it working first, optimize later
3. **Skipping tests**: Write tests as you go, not after
4. **Ignoring Arabic**: Test with real Arabic text from day 1
5. **Poor error messages**: Always include helpful error details
6. **No logging**: Add logging for debugging production issues
7. **Hardcoded values**: Use environment variables
8. **Complex database**: Keep schema simple for MVP

---

## 📞 GETTING HELP

If stuck, check in this order:

1. **This document**: Most answers are here
2. **FastAPI docs**: For framework-specific questions
3. **ZATCA portal**: For compliance requirements
4. **GitHub Issues**: For library-specific problems
5. **Stack Overflow**: For common patterns

**Remember**: The goal is a working MVP in 48 hours. When in doubt, choose the simpler solution. Polish comes later.

---

**END OF COPILOT INSTRUCTIONS**

_Last Updated: 2024-11-25_
_Version: 1.0_
_Status: Ready for Weekend Build_
