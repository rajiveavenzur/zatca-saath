"""Invoice generation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.schemas.invoice import InvoiceRequest, InvoiceResponse
from app.schemas.invoice_history import InvoiceHistoryResponse, InvoiceDetailResponse, InvoiceListResponse
from app.models.company import Company
from app.models.invoice import Invoice
from app.services.invoice_service import InvoiceService
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

    # Use service layer for business logic
    invoice_service = InvoiceService(db)

    try:
        # Create invoice using service
        invoice = invoice_service.create_invoice(
            user_id=current_user.id,
            company=company,
            invoice_data=invoice_data
        )

        # Return response
        return InvoiceResponse(
            invoice_number=invoice.invoice_number,
            pdf_base64=invoice.pdf_data,
            qr_code_data=invoice.qr_code_data,
            subtotal=invoice.subtotal,
            total_vat=invoice.total_vat,
            total_amount=invoice.total_amount,
            generated_at=invoice.created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate invoice: {str(e)}"
        )


@router.get("/", response_model=InvoiceListResponse)
async def list_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List user's invoices with pagination.
    
    Args:
        current_user: Authenticated user
        db: Database session
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        
    Returns:
        Paginated list of invoices
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Build query
    query = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    
    # Get total count
    total = query.count()
    
    # Get paginated invoices
    invoices = query.order_by(desc(Invoice.created_at)).offset(offset).limit(page_size).all()
    
    return InvoiceListResponse(
        total=total,
        page=page,
        page_size=page_size,
        invoices=[InvoiceHistoryResponse.model_validate(inv) for inv in invoices]
    )


@router.get("/search", response_model=InvoiceListResponse)
async def search_invoices(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search invoices by invoice number or customer name.
    
    Args:
        q: Search query
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Paginated search results
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Build search query
    search_pattern = f"%{q}%"
    search_filter = or_(
        Invoice.invoice_number.ilike(search_pattern),
        Invoice.customer_name_ar.ilike(search_pattern),
        Invoice.customer_name_en.ilike(search_pattern)
    )
    
    query = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        search_filter
    )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    invoices = query.order_by(desc(Invoice.created_at)).offset(offset).limit(page_size).all()
    
    return InvoiceListResponse(
        total=total,
        page=page,
        page_size=page_size,
        invoices=[InvoiceHistoryResponse.model_validate(inv) for inv in invoices]
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
    Get paginated invoice history for the current user (backward compatibility).
    
    This endpoint is deprecated. Use GET /api/v1/invoices or GET /api/v1/invoices/search instead.
    
    Args:
        current_user: Authenticated user
        db: Database session
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        search: Optional search term for invoice number or customer name
        
    Returns:
        Paginated list of invoices
    """
    # If search provided, redirect to search endpoint logic
    if search:
        search_pattern = f"%{search}%"
        search_filter = or_(
            Invoice.invoice_number.ilike(search_pattern),
            Invoice.customer_name_ar.ilike(search_pattern),
            Invoice.customer_name_en.ilike(search_pattern)
        )
        query = db.query(Invoice).filter(
            Invoice.user_id == current_user.id,
            search_filter
        )
    else:
        query = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    invoices = query.order_by(desc(Invoice.created_at)).offset(offset).limit(page_size).all()
    
    return InvoiceListResponse(
        total=total,
        page=page,
        page_size=page_size,
        invoices=[InvoiceHistoryResponse.model_validate(inv) for inv in invoices]
    )


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get invoice by ID.
    
    Args:
        invoice_id: Invoice ID (UUID)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Complete invoice details including PDF
        
    Raises:
        HTTPException: If invoice not found
    """
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id, current_user.id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return InvoiceDetailResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        customer_name_ar=invoice.customer_name_ar,
        customer_name_en=invoice.customer_name_en,
        customer_vat_number=invoice.customer_vat_number,
        customer_address_ar=invoice.customer_address_ar,
        customer_address_en=invoice.customer_address_en,
        subtotal=invoice.subtotal,
        total_vat=invoice.total_vat,
        total_amount=invoice.total_amount,
        line_items=invoice.line_items,
        qr_code_data=invoice.qr_code_data,
        pdf_base64=invoice.pdf_data,
        notes=invoice.notes,
        created_at=invoice.created_at
    )


@router.get("/number/{invoice_number}", response_model=InvoiceDetailResponse)
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
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_number(invoice_number, current_user.id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_number} not found"
        )
    
    return InvoiceDetailResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        customer_name_ar=invoice.customer_name_ar,
        customer_name_en=invoice.customer_name_en,
        customer_vat_number=invoice.customer_vat_number,
        customer_address_ar=invoice.customer_address_ar,
        customer_address_en=invoice.customer_address_en,
        subtotal=invoice.subtotal,
        total_vat=invoice.total_vat,
        total_amount=invoice.total_amount,
        line_items=invoice.line_items,
        qr_code_data=invoice.qr_code_data,
        pdf_base64=invoice.pdf_data,
        notes=invoice.notes,
        created_at=invoice.created_at
    )


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete invoice by ID.
    
    Args:
        invoice_id: Invoice ID to delete
        current_user: Authenticated user
        db: Database session
        
    Raises:
        HTTPException: If invoice not found
    """
    invoice_service = InvoiceService(db)
    deleted = invoice_service.delete_invoice(invoice_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return None
