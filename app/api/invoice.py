"""Invoice generation endpoints."""
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
    
    Args:
        invoice_data: Invoice data with customer and line items
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Generated invoice with PDF and QR code
        
    Raises:
        HTTPException: If company profile not found or generation fails
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
            seller_name=str(company.name_ar),
            vat_number=str(company.vat_number),
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
    
    Args:
        invoice_number: Invoice number to preview
        current_user: Authenticated user
        
    Raises:
        HTTPException: Feature not implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Invoice history feature coming in Week 3"
    )
