# ZATCA Invoice Generator

Generate ZATCA-compliant invoices for Saudi Arabian businesses with QR codes in 30 seconds.

## 🎯 Overview

A weekend-buildable MVP for ZATCA Phase 1 compliant invoice generation. This is a FastAPI backend that generates professional invoices with Arabic support and ZATCA-compliant QR codes.

**Core Features:**

- ✅ User authentication (JWT)
- ✅ Company profile management
- ✅ ZATCA-compliant invoice generation
- ✅ Bilingual PDF output (Arabic + English)
- ✅ QR code generation (TLV format)
- ✅ RESTful API with Swagger docs

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Docker & Docker Compose
- PostgreSQL 15+

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd zatca-invoice-generator

# Install dependencies
poetry install

# Copy environment variables
cp .env.example .env
# Edit .env with your settings

# Start Docker containers (database)
docker-compose up -d

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload
```

The API will be available at:

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Using Make Commands

```bash
# Install dependencies
make install

# Run development server
make dev

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Start Docker containers
make docker-up

# Stop Docker containers
make docker-down

# Run migrations
make migrate

# Create new migration
make migration msg="add new table"
```

## 📚 API Usage

### 1. Register User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePassword123!"
```

Response:

```json
{
	"access_token": "eyJhbGc...",
	"token_type": "bearer"
}
```

### 3. Create Company Profile

```bash
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name_en": "Test Trading Co.",
    "name_ar": "شركة التجارة التجريبية",
    "vat_number": "310122393500003",
    "address": "Riyadh, Saudi Arabia",
    "phone": "+966501234567",
    "email": "info@testtrading.sa"
  }'
```

### 4. Generate Invoice

```bash
curl -X POST "http://localhost:8000/api/v1/invoices/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "عميل تجريبي",
    "customer_vat_number": "310122393500004",
    "customer_address": "جدة، المملكة العربية السعودية",
    "invoice_number": "INV-001",
    "line_items": [
      {
        "description": "استشارات تقنية",
        "quantity": 10,
        "unit_price": 500.00,
        "vat_rate": 15.0
      }
    ],
    "notes": "شكراً لتعاملكم معنا"
  }'
```

Response includes base64-encoded PDF and QR code data.

## 🏗️ Project Structure

```
zatca-invoice-generator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── database.py             # Database setup
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   └── company.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── company.py
│   │   └── invoice.py
│   ├── api/                    # API endpoints
│   │   ├── auth.py
│   │   ├── company.py
│   │   └── invoice.py
│   ├── services/               # Business logic
│   │   ├── pdf_generator.py
│   │   ├── qr_generator.py
│   │   └── zatca_validator.py
│   └── utils/                  # Utilities
│       ├── security.py
│       └── arabic.py
├── tests/                      # Tests
├── alembic/                    # Database migrations
├── static/                     # Static files (fonts, etc.)
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── Makefile
└── README.md
```

## 🔧 Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **ReportLab** - PDF generation
- **QRCode** - QR code generation
- **JWT** - Authentication
- **Docker** - Containerization

## 📖 ZATCA Compliance

This application generates Phase 1 compliant invoices:

- ✅ **QR Code Format**: TLV (Tag-Length-Value) encoding
- ✅ **VAT Number**: 15 digits starting with 3
- ✅ **Arabic Support**: Bilingual invoices (Arabic + English)
- ✅ **Invoice Elements**: All required fields included
- ✅ **Calculations**: Automatic VAT calculations

### QR Code Data (TLV Format)

1. **Tag 1**: Seller Name (UTF-8)
2. **Tag 2**: VAT Registration Number
3. **Tag 3**: Invoice Timestamp (ISO format)
4. **Tag 4**: Invoice Total (with VAT)
5. **Tag 5**: VAT Amount

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
poetry run pytest tests/test_auth.py -v

# Run with coverage
poetry run pytest --cov=app --cov-report=html
```

## 🐳 Docker Deployment

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop containers
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

## 🔐 Security

- **Password Hashing**: Bcrypt
- **JWT Tokens**: 24-hour expiration
- **Environment Variables**: All secrets in `.env`
- **CORS**: Configurable origins
- **Input Validation**: Pydantic schemas

## 📝 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🌍 Arabic Font Setup

For proper Arabic text rendering in PDFs, download and place `NotoSansArabic-Regular.ttf` in `static/fonts/`:

```bash
# Download Noto Sans Arabic font
wget https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf -O static/fonts/NotoSansArabic-Regular.ttf
```

## 🚧 Roadmap

### Phase 1 (MVP - Current)

- ✅ User authentication
- ✅ Company profiles
- ✅ Invoice generation
- ✅ QR codes
- ✅ PDF output

### Phase 2 (Week 3)

- ⏳ ZATCA API integration
- ⏳ Invoice history/storage
- ⏳ Email delivery
- ⏳ Recurring invoices

### Phase 3 (Future)

- ⏳ Customer database
- ⏳ Reporting/analytics
- ⏳ Multi-user support
- ⏳ Mobile app

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🔗 Resources

- [ZATCA E-Invoicing Portal](https://zatca.gov.sa/en/E-Invoicing/Pages/default.aspx)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

**Built with ❤️ for Saudi Arabian SMBs**
