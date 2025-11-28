"""ZATCA-compliant QR code generator service."""
import base64
from decimal import Decimal
from io import BytesIO

import qrcode  # type: ignore


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
        """
        Encode data in TLV (Tag-Length-Value) format.
        
        Args:
            tag: The tag number (1-5 for ZATCA)
            value: The value to encode
            
        Returns:
            The TLV-encoded bytes
        """
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
        
        Args:
            seller_name: Seller's company name (Arabic preferred)
            vat_number: VAT registration number (15 digits)
            timestamp: Invoice timestamp in ISO format
            total_amount: Total invoice amount including VAT
            vat_amount: Total VAT amount
            
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
        
        Args:
            qr_data: The data to encode in QR code
            box_size: Size of each box in pixels
            border: Border size in boxes
            
        Returns:
            PNG image as bytes
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
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
        
        Args:
            qr_data: The data to encode in QR code
            
        Returns:
            Base64-encoded PNG image
        """
        img_bytes = ZATCAQRGenerator.generate_qr_image(qr_data)
        return base64.b64encode(img_bytes).decode('utf-8')
