"""ZATCA-compliant PDF invoice generator with Arabic support."""
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.units import mm  # type: ignore
from reportlab.lib import colors  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER  # type: ignore
from reportlab.pdfbase import pdfmetrics  # type: ignore
from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
from io import BytesIO
from typing import Dict, List
from decimal import Decimal
from datetime import datetime
import os

from app.schemas.invoice import InvoiceRequest, InvoiceLineItem

# Try to register Arabic font
FONT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'fonts', 'NotoSansArabic-Regular.ttf')
try:
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('NotoSansArabic', FONT_PATH))
        ARABIC_FONT_AVAILABLE = True
    else:
        ARABIC_FONT_AVAILABLE = False
        print(f"Warning: Arabic font not found at {FONT_PATH}")
except Exception as e:
    ARABIC_FONT_AVAILABLE = False
    print(f"Warning: Could not register Arabic font: {e}")


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
        if ARABIC_FONT_AVAILABLE:
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
        else:
            # Fallback to standard fonts
            self.styles.add(ParagraphStyle(
                name='ArabicTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                alignment=TA_RIGHT,
                textColor=colors.HexColor('#1a1a1a')
            ))

            self.styles.add(ParagraphStyle(
                name='ArabicNormal',
                parent=self.styles['Normal'],
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
