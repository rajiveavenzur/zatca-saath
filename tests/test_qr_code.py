"""Tests for QR code generation."""
import pytest
from decimal import Decimal
import base64

from app.services.qr_generator import ZATCAQRGenerator


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
    decoded = base64.b64decode(qr_data)
    assert len(decoded) > 0
    
    # Check TLV structure
    assert decoded[0] == 1  # First tag should be 1 (seller name)


def test_qr_image_generation():
    """Test QR code image generation."""
    qr_data = "AQ1UZXN0IENvbXBhbnkC"
    img_bytes = ZATCAQRGenerator.generate_qr_image(qr_data)

    assert img_bytes is not None
    assert len(img_bytes) > 0
    # Should be valid PNG
    assert img_bytes.startswith(b'\x89PNG')


def test_qr_base64_generation():
    """Test QR code base64 generation."""
    qr_data = "AQ1UZXN0IENvbXBhbnkC"
    qr_base64 = ZATCAQRGenerator.generate_qr_base64(qr_data)

    assert qr_base64 is not None
    assert len(qr_base64) > 0
    
    # Should be valid base64
    decoded = base64.b64decode(qr_base64)
    assert decoded.startswith(b'\x89PNG')


def test_tlv_encoding():
    """Test TLV encoding."""
    tlv_bytes = ZATCAQRGenerator._encode_tlv(1, "Test")
    
    # Should have tag, length, and value
    assert tlv_bytes[0] == 1  # Tag
    assert tlv_bytes[1] == 4  # Length ("Test" = 4 bytes)
    assert tlv_bytes[2:] == b"Test"  # Value


def test_arabic_qr_data():
    """Test QR generation with Arabic text."""
    qr_data = ZATCAQRGenerator.generate_qr_data(
        seller_name="شركة التجارة",
        vat_number="310122393500003",
        timestamp="2024-11-25T10:00:00",
        total_amount=Decimal("5750.00"),
        vat_amount=Decimal("750.00")
    )

    assert qr_data is not None
    decoded = base64.b64decode(qr_data)
    
    # Check that Arabic text is properly encoded in UTF-8
    assert len(decoded) > 0
