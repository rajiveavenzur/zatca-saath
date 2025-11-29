"""Invoice service for business logic."""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from uuid import UUID
import base64

from app.models.invoice import Invoice
from app.models.company import Company
from app.schemas.invoice import InvoiceRequest
from app.services.pdf_generator import ZATCAInvoicePDF
from app.services.qr_generator import ZATCAQRGenerator


class InvoiceService:
    """
    Business logic for invoice operations.
    
    This service handles:
    - Invoice calculations
    - QR code generation
    - PDF generation
    - Database persistence
    """

    def __init__(self, db: Session):
        """
        Initialize invoice service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.pdf_generator = ZATCAInvoicePDF()
        self.qr_generator = ZATCAQRGenerator()

    def calculate_totals(self, line_items: list) -> dict:
        """
        Calculate invoice totals from line items.
        
        Args:
            line_items: List of line items with quantity, unit_price, vat_rate
            
        Returns:
            Dict with subtotal, vat_amount, total_amount
        """
        subtotal = Decimal("0")
        vat_amount = Decimal("0")

        for item in line_items:
            # Handle both dict and object formats
            if hasattr(item, 'dict'):
                item = item.dict()
            
            qty = Decimal(str(item.get('quantity', 0)))
            price = Decimal(str(item.get('unit_price', 0)))
            vat_rate = Decimal(str(item.get('vat_rate', 15)))
            
            item_subtotal = qty * price
            item_vat = (item_subtotal * vat_rate) / Decimal("100")
            
            subtotal += item_subtotal
            vat_amount += item_vat

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
        invoice_data: InvoiceRequest
    ) -> Invoice:
        """
        Create invoice with PDF and QR code.
        
        Steps:
        1. Calculate totals
        2. Generate QR code
        3. Generate PDF
        4. Save to database
        
        Args:
            user_id: User ID creating the invoice
            company: Company information
            invoice_data: Invoice data from request
            
        Returns:
            Created Invoice object
            
        Raises:
            Exception: If invoice generation fails
        """
        # Calculate totals
        totals = self.calculate_totals(invoice_data.line_items)

        # Generate QR code data (ZATCA TLV format)
        timestamp = invoice_data.invoice_date.isoformat()
        qr_data = self.qr_generator.generate_qr_data(
            seller_name=company.name_ar,
            vat_number=company.vat_number,
            timestamp=timestamp,
            total_amount=totals['total_amount'],
            vat_amount=totals['vat_amount']
        )

        # Generate QR code image
        qr_image_bytes = self.qr_generator.generate_qr_image(qr_data)

        # Prepare company info for PDF
        company_info = {
            'name_en': company.name_en,
            'name_ar': company.name_ar,
            'vat_number': company.vat_number,
            'address': company.address,
            'phone': company.phone,
            'email': company.email
        }

        # Generate PDF
        pdf_bytes = self.pdf_generator.generate_invoice(
            company_info=company_info,
            invoice_data=invoice_data,
            qr_code_image_bytes=qr_image_bytes
        )

        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Convert line items to dict for JSON serialization
        line_items_data = []
        for item in invoice_data.line_items:
            item_dict = item.dict()
            # Convert Decimal to float for JSON serialization
            item_dict['quantity'] = float(item_dict['quantity'])
            item_dict['unit_price'] = float(item_dict['unit_price'])
            item_dict['vat_rate'] = float(item_dict['vat_rate'])
            line_items_data.append(item_dict)

        # Create database record
        invoice = Invoice(
            user_id=user_id,
            company_id=company.id,
            invoice_number=invoice_data.invoice_number,
            invoice_date=invoice_data.invoice_date,
            customer_name_ar=invoice_data.customer_name_ar,
            customer_name_en=invoice_data.customer_name_en,
            customer_address_ar=invoice_data.customer_address_ar,
            customer_address_en=invoice_data.customer_address_en,
            customer_vat_number=invoice_data.customer_vat_number,
            line_items=line_items_data,
            subtotal=totals['subtotal'],
            total_vat=totals['vat_amount'],
            total_amount=totals['total_amount'],
            notes=invoice_data.notes,
            qr_code_data=qr_data,
            pdf_data=pdf_base64,
            status='generated'
        )

        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        return invoice

    def get_invoice_by_id(self, invoice_id: UUID, user_id: UUID) -> Invoice:
        """
        Get invoice by ID for a specific user.
        
        Args:
            invoice_id: Invoice ID
            user_id: User ID (for security)
            
        Returns:
            Invoice object or None
        """
        return self.db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.user_id == user_id
        ).first()

    def get_invoice_by_number(self, invoice_number: str, user_id: UUID) -> Invoice:
        """
        Get invoice by invoice number for a specific user.
        
        Args:
            invoice_number: Invoice number
            user_id: User ID (for security)
            
        Returns:
            Invoice object or None
        """
        return self.db.query(Invoice).filter(
            Invoice.invoice_number == invoice_number,
            Invoice.user_id == user_id
        ).first()

    def delete_invoice(self, invoice_id: UUID, user_id: UUID) -> bool:
        """
        Delete invoice by ID.
        
        Args:
            invoice_id: Invoice ID
            user_id: User ID (for security)
            
        Returns:
            True if deleted, False if not found
        """
        invoice = self.get_invoice_by_id(invoice_id, user_id)
        if invoice:
            self.db.delete(invoice)
            self.db.commit()
            return True
        return False
