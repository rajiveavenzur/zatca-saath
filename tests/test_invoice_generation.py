"""Tests for invoice generation."""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from app.main import app

client = TestClient(app)


def get_auth_token():
    """Helper function to get authentication token."""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "invoice_test@example.com",
            "password": "SecurePassword123!"
        }
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "invoice_test@example.com",
            "password": "SecurePassword123!"
        }
    )
    return response.json()["access_token"]


def create_company(token):
    """Helper function to create a company."""
    response = client.post(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name_en": "Test Trading Co.",
            "name_ar": "شركة التجارة التجريبية",
            "vat_number": "310122393500003",
            "address": "Riyadh, Saudi Arabia",
            "phone": "+966501234567",
            "email": "info@testtrading.sa"
        }
    )
    return response.json()


def test_generate_invoice_without_company():
    """Test invoice generation without company profile."""
    token = get_auth_token()
    
    response = client.post(
        "/api/v1/invoices/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer_name": "عميل تجريبي",
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
        }
    )
    
    assert response.status_code == 400
    assert "Company profile not found" in response.json()["detail"]


def test_generate_invoice_success():
    """Test successful invoice generation."""
    token = get_auth_token()
    create_company(token)
    
    response = client.post(
        "/api/v1/invoices/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
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
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["invoice_number"] == "INV-001"
    assert "pdf_base64" in data
    assert "qr_code_data" in data
    assert float(data["subtotal"]) == 5000.00
    assert float(data["total_vat"]) == 750.00
    assert float(data["total_amount"]) == 5750.00


def test_generate_invoice_invalid_vat_rate():
    """Test invoice generation with invalid VAT rate."""
    token = get_auth_token()
    create_company(token)
    
    response = client.post(
        "/api/v1/invoices/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer_name": "Test Customer",
            "customer_address": "Riyadh",
            "invoice_number": "INV-002",
            "line_items": [
                {
                    "description": "Service",
                    "quantity": 1,
                    "unit_price": 100.00,
                    "vat_rate": 20.0  # Invalid rate
                }
            ]
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_generate_invoice_without_auth():
    """Test invoice generation without authentication."""
    response = client.post(
        "/api/v1/invoices/generate",
        json={
            "customer_name": "Test",
            "customer_address": "Test",
            "invoice_number": "INV-003",
            "line_items": [
                {
                    "description": "Test",
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ]
        }
    )
    
    assert response.status_code == 401
