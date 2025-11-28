# 🚀 ZATCA Invoice Generator - Quick Start Guide

## ✅ Current Status

**The API is running successfully!** 🎉

- Server URL: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Database: PostgreSQL on port 5433

## 🔧 Fixed Issues

### 1. QR Generator Service

- ✅ Fixed `qrcode.constants.ERROR_CORRECT_L` → `qrcode.ERROR_CORRECT_L`
- ✅ Verified QR code generation works correctly
- ✅ Tested ZATCA TLV encoding
- ⚠️ Two remaining type checker warnings (harmless - code works fine):
  - Import "qrcode" could not be resolved (package is installed, just missing type stubs)
  - PIL Image.save() format parameter (false positive - method accepts it)

### 2. Server Status

- ✅ FastAPI server running on http://0.0.0.0:8000
- ✅ Auto-reload enabled for development
- ✅ Health endpoint responding correctly
- ✅ API documentation available at /docs

## 🧪 Testing

### Verified Working:

```bash
# QR Code Generation
✅ TLV encoding works
✅ Base64 encoding works
✅ PNG image generation works (976 bytes)
✅ ZATCA-compliant format verified

# API Endpoints
✅ GET / returns {"message":"ZATCA Invoice Generator API","version":"1.0.0","docs":"/docs"}
✅ GET /health returns {"status":"healthy"}
```

## 📋 Next Steps

### 1. Test Complete Workflow

```bash
# 1. Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# 2. Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=SecurePassword123!"

# Save the access_token from response

# 3. Create company profile
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name_en": "Test Trading Co.",
    "name_ar": "شركة التجارة التجريبية",
    "vat_number": "310122393500003",
    "address": "Riyadh, Saudi Arabia",
    "phone": "+966501234567",
    "email": "info@testtrading.sa"
  }'

# 4. Generate invoice
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
        "description": "استشارات تقنية",
        "quantity": 10,
        "unit_price": 500.00,
        "vat_rate": 15.0
      }
    ],
    "notes": "شكراً لتعاملكم معنا"
  }'
```

### 2. Download Arabic Font (Optional but Recommended)

```bash
# Download Noto Sans Arabic for PDF generation
curl -L https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Regular.ttf \
  -o static/fonts/NotoSansArabic-Regular.ttf
```

Without this font, Arabic text in PDFs will fall back to default fonts.

### 3. Access API Documentation

Open in your browser:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Interactive API testing available in Swagger UI!

### 4. Run Tests

```bash
# Run all tests
make test

# Or with poetry directly
poetry run pytest tests/ -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🐳 Docker Commands

```bash
# View logs
make docker-logs

# Stop containers
make docker-down

# Restart containers
make docker-down && make docker-up

# Access database
make db-shell
```

## 📊 Project Structure

```
✅ Database models (User, Company)
✅ API endpoints (Auth, Company, Invoice)
✅ Services (QR Generator, PDF Generator, ZATCA Validator)
✅ Authentication (JWT with bcrypt)
✅ Docker setup (PostgreSQL on port 5433)
✅ Alembic migrations
✅ Tests scaffolding
```

## ⚠️ Known Limitations (MVP)

As per design:

- ❌ No invoice history/storage (generate on-demand only)
- ❌ No customer database
- ❌ No email delivery
- ❌ No ZATCA Phase 2 API integration (Week 3)
- ❌ Single user per company

## 🔒 Security Notes

- ✅ JWT authentication implemented
- ✅ Password hashing with bcrypt
- ✅ Pydantic validation on all inputs
- ✅ CORS configured
- ⚠️ Change `SECRET_KEY` in .env before production!
- ⚠️ Use strong passwords in production

## 📝 Development Commands

```bash
# Start development server
make dev

# Format code
make format

# Lint code
make lint

# Run migrations
make migrate

# Clean cache
make clean
```

## 🎯 Success Criteria

✅ Server running
✅ Health check passing
✅ QR code generation working
✅ Database connected
✅ Migrations applied
⏳ End-to-end invoice generation (test next)
⏳ Arabic font installed
⏳ Full test suite passing

## 🐛 Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>
```

### Database connection issues

```bash
# Check Docker containers
docker-compose ps

# Restart database
make docker-down && make docker-up

# Check database logs
docker-compose logs db
```

### Module import errors

```bash
# Reinstall dependencies
poetry install

# Verify environment
poetry env info
```

## 📚 Documentation

- Project instructions: `.github/instructions/zatka.instructions.md`
- API docs: http://localhost:8000/docs
- ZATCA specification: https://zatca.gov.sa/en/E-Invoicing/Pages/default.aspx

---

**Server is ready for testing!** Visit http://localhost:8000/docs to explore the API interactively.
