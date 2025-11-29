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
import arabic_reshaper  # type: ignore
from bidi.algorithm import get_display  # type: ignore

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


def reshape_arabic_text(text: str) -> str:
    """
    Reshape Arabic text for proper RTL (right-to-left) rendering in PDFs.
    
    This function:
    1. Reshapes Arabic characters to their correct positional forms
    2. Reorders text for RTL display
    3. Handles mixed Arabic/English text
    
    Args:
        text: Input text (may contain Arabic, English, or mixed)
        
    Returns:
        Reshaped text ready for PDF rendering
    """
    if not text:
        return text
    
    try:
        # Reshape Arabic characters (handles ligatures and positional forms)
        reshaped_text = arabic_reshaper.reshape(text)
        
        # Apply bidirectional algorithm (handles RTL/LTR mixing)
        bidi_text = get_display(reshaped_text)
        
        return bidi_text
    except Exception as e:
        print(f"Warning: Could not reshape Arabic text: {e}")
        return text


class ZATCAInvoicePDF:
    """
    Generate ZATCA-compliant invoice PDFs with Arabic support.
    """

    def __init__(self):
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _get_default_labels(self, language: str = "ar") -> Dict[str, str]:
        """Get default labels based on language."""
        if language == "ar":
            return {
                "vat_number": "الرقم الضريبي",
                "invoice_number": "رقم الفاتورة",
                "date": "التاريخ",
                "customer_info": "معلومات العميل",
                "description": "الوصف",
                "quantity": "الكمية",
                "amount": "المبلغ",
                "vat": "ض.ق.م",
                "total": "الإجمالي",
                "subtotal": "المجموع الفرعي",
                "vat_total": "ضريبة القيمة المضافة (15%)",
                "grand_total": "الإجمالي",
                "qr_code": "رمز الاستجابة السريعة",
                "notes": "ملاحظات"
            }
        else:  # English
            return {
                "vat_number": "VAT Number",
                "invoice_number": "Invoice Number",
                "date": "Date",
                "customer_info": "Customer Information",
                "description": "Description",
                "quantity": "Qty",
                "amount": "Amount",
                "vat": "VAT",
                "total": "Total",
                "subtotal": "Subtotal",
                "vat_total": "VAT (15%)",
                "grand_total": "Total",
                "qr_code": "QR Code",
                "notes": "Notes"
            }
    
    def _get_labels(self, invoice_data: InvoiceRequest) -> Dict[str, str]:
        """Get labels from request or use defaults based on language."""
        default_labels = self._get_default_labels(invoice_data.language)
        
        if invoice_data.labels:
            # Merge custom labels with defaults
            labels = default_labels.copy()
            labels.update(invoice_data.labels.model_dump(exclude_none=True))
            return labels
        
        return default_labels

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

    def _create_header(self, company_info: Dict, invoice_data: InvoiceRequest, labels: Dict[str, str]):
        """Create invoice header with company and invoice details."""
        header_data = []
        
        # Get both Arabic and English labels
        ar_labels = self._get_default_labels('ar')
        en_labels = self._get_default_labels('en')

        # Company name (Arabic + English)
        company_name_ar = reshape_arabic_text(company_info['name_ar'])
        header_data.append([
            Paragraph(f"<b>{company_name_ar}</b>", self.styles['ArabicTitle']),
            Paragraph(f"<b>{company_info['name_en']}</b>", self.styles['EnglishTitle'])
        ])

        # VAT Number (Bilingual)
        vat_label_ar = reshape_arabic_text(labels.get('vat_number', ar_labels['vat_number']))
        vat_label_en = labels.get('vat_number', en_labels['vat_number']) if invoice_data.language == 'en' else en_labels['vat_number']
        header_data.append([
            Paragraph(f"{vat_label_ar}: {company_info['vat_number']}", self.styles['ArabicNormal']),
            Paragraph(f"{vat_label_en}: {company_info['vat_number']}", self.styles['Normal'])
        ])

        # Invoice Number (Bilingual)
        inv_label_ar = reshape_arabic_text(labels.get('invoice_number', ar_labels['invoice_number']))
        inv_label_en = labels.get('invoice_number', en_labels['invoice_number']) if invoice_data.language == 'en' else en_labels['invoice_number']
        header_data.append([
            Paragraph(f"{inv_label_ar}: {invoice_data.invoice_number}", self.styles['ArabicNormal']),
            Paragraph(f"{inv_label_en}: {invoice_data.invoice_number}", self.styles['Normal'])
        ])

        # Date (Bilingual)
        date_label_ar = reshape_arabic_text(labels.get('date', ar_labels['date']))
        date_label_en = labels.get('date', en_labels['date']) if invoice_data.language == 'en' else en_labels['date']
        header_data.append([
            Paragraph(f"{date_label_ar}: {invoice_data.invoice_date.strftime('%Y-%m-%d')}", self.styles['ArabicNormal']),
            Paragraph(f"{date_label_en}: {invoice_data.invoice_date.strftime('%Y-%m-%d')}", self.styles['Normal'])
        ])

        header_table = Table(header_data, colWidths=[self.width/2, self.width/2])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        return header_table

    def _create_customer_section(self, invoice_data: InvoiceRequest, labels: Dict[str, str]):
        """Create customer information section - Arabic MANDATORY per ZATCA."""
        # Get both Arabic and English labels
        ar_labels = self._get_default_labels('ar')
        en_labels = self._get_default_labels('en')
        
        # Customer info header (Bilingual)
        customer_label_ar = reshape_arabic_text(labels.get('customer_info', ar_labels['customer_info']))
        customer_label_en = labels.get('customer_info', en_labels['customer_info']) if invoice_data.language == 'en' else en_labels['customer_info']
        
        # Arabic is MANDATORY - reshape it
        customer_name_ar = reshape_arabic_text(invoice_data.customer_name_ar)
        customer_address_ar = reshape_arabic_text(invoice_data.customer_address_ar)
        
        # English is optional
        customer_name_en = invoice_data.customer_name_en or ""
        customer_address_en = invoice_data.customer_address_en or ""
        
        customer_data = [
            [
                Paragraph(f"<b>{customer_label_ar}</b>", self.styles['ArabicNormal']),
                Paragraph(f"<b>{customer_label_en}</b>", self.styles['Normal'])
            ],
            [
                Paragraph(customer_name_ar, self.styles['ArabicNormal']),
                Paragraph(customer_name_en, self.styles['Normal'])
            ],
            [
                Paragraph(customer_address_ar, self.styles['ArabicNormal']),
                Paragraph(customer_address_en, self.styles['Normal'])
            ],
        ]

        if invoice_data.customer_vat_number:
            vat_label_ar = reshape_arabic_text(labels.get('vat_number', ar_labels['vat_number']))
            vat_label_en = labels.get('vat_number', en_labels['vat_number']) if invoice_data.language == 'en' else en_labels['vat_number']
            customer_data.append([
                Paragraph(f"{vat_label_ar}: {invoice_data.customer_vat_number}", self.styles['ArabicNormal']),
                Paragraph(f"{vat_label_en}: {invoice_data.customer_vat_number}", self.styles['Normal'])
            ])

        customer_table = Table(customer_data, colWidths=[self.width/2, self.width/2])
        
        # Use Arabic font if available and language is Arabic
        customer_font = 'NotoSansArabic' if (ARABIC_FONT_AVAILABLE and invoice_data.language == 'ar') else 'Helvetica'
        
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, -1), customer_font),
        ]))

        return customer_table

    def _create_line_items_table(self, line_items: List[InvoiceLineItem], labels: Dict[str, str], language: str):
        """Create line items table with calculations."""
        # Get both Arabic and English labels
        ar_labels = self._get_default_labels('ar')
        en_labels = self._get_default_labels('en')
        
        # Create bilingual headers with proper styling
        total_ar = reshape_arabic_text(labels.get('total', ar_labels['total']))
        total_en = labels.get('total', en_labels['total']) if language == 'en' else en_labels['total']
        vat_ar = reshape_arabic_text(labels.get('vat', ar_labels['vat']))
        vat_en = labels.get('vat', en_labels['vat']) if language == 'en' else en_labels['vat']
        amount_ar = reshape_arabic_text(labels.get('amount', ar_labels['amount']))
        amount_en = labels.get('amount', en_labels['amount']) if language == 'en' else en_labels['amount']
        qty_ar = reshape_arabic_text(labels.get('quantity', ar_labels['quantity']))
        qty_en = labels.get('quantity', en_labels['quantity']) if language == 'en' else en_labels['quantity']
        desc_ar = reshape_arabic_text(labels.get('description', ar_labels['description']))
        desc_en = labels.get('description', en_labels['description']) if language == 'en' else en_labels['description']
        
        # Create header with Paragraphs for proper font rendering
        header_style_ar = ParagraphStyle('HeaderAr', parent=self.styles['Normal'], fontName='NotoSansArabic' if ARABIC_FONT_AVAILABLE else 'Helvetica', fontSize=9, alignment=TA_CENTER, textColor=colors.white)
        header_style_en = ParagraphStyle('HeaderEn', parent=self.styles['Normal'], fontName='Helvetica', fontSize=9, alignment=TA_CENTER, textColor=colors.white)
        
        headers = [[
            Paragraph(f"{total_ar}<br/>{total_en}", header_style_ar),
            Paragraph(f"{vat_ar}<br/>{vat_en}", header_style_ar),
            Paragraph(f"{amount_ar}<br/>{amount_en}", header_style_ar),
            Paragraph(f"{qty_ar}<br/>{qty_en}", header_style_ar),
            Paragraph(f"{desc_ar}<br/>{desc_en}", header_style_ar)
        ]]

        # Data rows
        data_rows = []
        for item in line_items:
            # Reshape Arabic description
            description_ar = reshape_arabic_text(item.description)
            
            row = [
                f"{item.total:.2f}",
                f"{item.vat_amount:.2f}",
                f"{item.unit_price:.2f}",
                f"{item.quantity:.2f}",
                description_ar
            ]
            data_rows.append(row)

        # Combine headers and data
        table_data = headers + data_rows

        # Create table
        col_widths = [80, 60, 80, 60, 220]
        items_table = Table(table_data, colWidths=col_widths)

        # Use Arabic font for data if available
        data_font = 'NotoSansArabic' if ARABIC_FONT_AVAILABLE else 'Helvetica'

        items_table.setStyle(TableStyle([
            # Header style - don't override font as we're using Paragraphs
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Data rows style
            ('FONTNAME', (0, 1), (-1, -1), data_font),
            ('ALIGN', (0, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return items_table

    def _create_totals_section(self, invoice_data: InvoiceRequest, labels: Dict[str, str]):
        """Create totals section with VAT breakdown."""
        # Get both Arabic and English labels
        ar_labels = self._get_default_labels('ar')
        en_labels = self._get_default_labels('en')
        
        # Create bilingual labels
        subtotal_ar = reshape_arabic_text(labels.get('subtotal', ar_labels['subtotal']))
        subtotal_en = labels.get('subtotal', en_labels['subtotal']) if invoice_data.language == 'en' else en_labels['subtotal']
        vat_ar = reshape_arabic_text(labels.get('vat_total', ar_labels['vat_total']))
        vat_en = labels.get('vat_total', en_labels['vat_total']) if invoice_data.language == 'en' else en_labels['vat_total']
        total_ar = reshape_arabic_text(labels.get('grand_total', ar_labels['grand_total']))
        total_en = labels.get('grand_total', en_labels['grand_total']) if invoice_data.language == 'en' else en_labels['grand_total']
        
        totals_data = [
            [f"{subtotal_ar} | {subtotal_en}", f"{invoice_data.subtotal:.2f} SAR"],
            [f"{vat_ar} | {vat_en}", f"{invoice_data.total_vat:.2f} SAR"],
            [f"{total_ar} | {total_en}", f"{invoice_data.total_amount:.2f} SAR"],
        ]

        totals_table = Table(totals_data, colWidths=[350, 150])
        
        # Use Arabic font if available and language is Arabic
        totals_font = 'NotoSansArabic' if (ARABIC_FONT_AVAILABLE and invoice_data.language == 'ar') else 'Helvetica'
        totals_font_bold = 'NotoSansArabic' if (ARABIC_FONT_AVAILABLE and invoice_data.language == 'ar') else 'Helvetica-Bold'
        
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), totals_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, -1), (-1, -1), totals_font_bold),
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

        # Get labels (either custom or defaults based on language)
        labels = self._get_labels(invoice_data)
        
        # Build document elements
        elements = []

        # Header
        elements.append(self._create_header(company_info, invoice_data, labels))
        elements.append(Spacer(1, 15*mm))

        # Customer section
        elements.append(self._create_customer_section(invoice_data, labels))
        elements.append(Spacer(1, 10*mm))

        # Line items
        elements.append(self._create_line_items_table(invoice_data.line_items, labels, invoice_data.language))
        elements.append(Spacer(1, 10*mm))

        # Totals
        elements.append(self._create_totals_section(invoice_data, labels))
        elements.append(Spacer(1, 15*mm))

        # QR Code (Bilingual)
        ar_labels = self._get_default_labels('ar')
        en_labels = self._get_default_labels('en')
        qr_label_ar = reshape_arabic_text(labels.get('qr_code', ar_labels['qr_code']))
        qr_label_en = labels.get('qr_code', en_labels['qr_code']) if invoice_data.language == 'en' else en_labels['qr_code']
        qr_img = Image(BytesIO(qr_code_image_bytes), width=50*mm, height=50*mm)
        
        # Create QR label with mixed fonts
        qr_style = ParagraphStyle('QRLabel', parent=self.styles['Normal'], fontSize=10, alignment=TA_CENTER)
        qr_label_para = Paragraph(
            f'<font name="NotoSansArabic">{qr_label_ar}</font> | {qr_label_en}',
            qr_style
        )
        elements.append(qr_label_para)
        elements.append(qr_img)

        # Notes (if any) - Bilingual
        if invoice_data.notes:
            elements.append(Spacer(1, 10*mm))
            notes_label_ar = reshape_arabic_text(labels.get('notes', ar_labels['notes']))
            notes_label_en = labels.get('notes', en_labels['notes']) if invoice_data.language == 'en' else en_labels['notes']
            notes_text_ar = reshape_arabic_text(invoice_data.notes)
            
            # Create bilingual notes with proper font handling
            notes_style = ParagraphStyle('NotesStyle', parent=self.styles['Normal'], fontSize=10)
            notes_para = Paragraph(
                f'<b><font name="NotoSansArabic">{notes_label_ar}</font> | {notes_label_en}:</b><br/>' +
                f'<font name="NotoSansArabic">{notes_text_ar}</font>',
                notes_style
            )
            elements.append(notes_para)

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        return buffer.getvalue()
