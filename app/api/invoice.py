"""Invoice generation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
import base64
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.schemas.invoice import InvoiceRequest, InvoiceResponse
from app.schemas.invoice_history import InvoiceHistoryResponse, InvoiceDetailResponse, InvoiceListResponse
from app.models.company import Company
from app.models.invoice import Invoice
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

        # Save invoice to database
        # Convert line items to dict with string values for JSON serialization
        line_items_data = []
        for item in invoice_data.line_items:
            item_dict = item.dict()
            # Convert Decimal to float for JSON serialization
            item_dict['quantity'] = float(item_dict['quantity'])
            item_dict['unit_price'] = float(item_dict['unit_price'])
            item_dict['vat_rate'] = float(item_dict['vat_rate'])
            line_items_data.append(item_dict)
        
        new_invoice = Invoice(
            user_id=current_user.id,
            company_id=company.id,
            invoice_number=invoice_data.invoice_number,
            invoice_date=invoice_data.invoice_date,
            customer_name=invoice_data.customer_name,
            customer_vat_number=invoice_data.customer_vat_number,
            customer_address=invoice_data.customer_address,
            subtotal=invoice_data.subtotal,
            total_vat=invoice_data.total_vat,
            total_amount=invoice_data.total_amount,
            line_items=line_items_data,
            qr_code_data=qr_data,
            pdf_data=pdf_base64,
            notes=invoice_data.notes
        )
        
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

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
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate invoice: {str(e)}"
        )


@router.get("/history", response_model=InvoiceListResponse)
async def get_invoice_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by invoice number or customer name")
):
    """
    Get paginated invoice history for the current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        search: Optional search term for invoice number or customer name
        
    Returns:
        Paginated list of invoices
    """
    # Base query
    query = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    
    # Apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Invoice.invoice_number.ilike(search_pattern),
                Invoice.customer_name.ilike(search_pattern)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    invoices = query.order_by(Invoice.created_at.desc()).offset(offset).limit(page_size).all()
    
    return InvoiceListResponse(
        total=total,
        page=page,
        page_size=page_size,
        invoices=[InvoiceHistoryResponse.model_validate(inv) for inv in invoices]
    )


@router.get("/{invoice_number}", response_model=InvoiceDetailResponse)
async def get_invoice_by_number(
    invoice_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get invoice details by invoice number.
    
    Args:
        invoice_number: Invoice number to retrieve
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Complete invoice details including PDF
        
    Raises:
        HTTPException: If invoice not found
    """
    invoice = db.query(Invoice).filter(
        Invoice.invoice_number == invoice_number,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_number} not found"
        )
    
    return InvoiceDetailResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        customer_name=invoice.customer_name,
        customer_vat_number=invoice.customer_vat_number,
        customer_address=invoice.customer_address,
        subtotal=invoice.subtotal,
        total_vat=invoice.total_vat,
        total_amount=invoice.total_amount,
        line_items=invoice.line_items,
        qr_code_data=invoice.qr_code_data,
        pdf_base64=invoice.pdf_data,
        notes=invoice.notes,
        created_at=invoice.created_at
    )
