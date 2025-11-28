"""ZATCA format validation utilities."""
import re
from typing import Optional, Dict, Any
from decimal import Decimal


class ZATCAValidator:
    """Validator for ZATCA compliance rules."""
    
    @staticmethod
    def validate_vat_number(vat_number: str) -> bool:
        """
        Validate Saudi VAT number format.
        
        Must be 15 digits starting with 3.
        
        Args:
            vat_number: The VAT number to validate
            
        Returns:
            True if valid, False otherwise
        """
        return bool(re.match(r'^3\d{14}$', vat_number))
    
    @staticmethod
    def validate_invoice_number(invoice_number: str) -> bool:
        """
        Validate invoice number format.
        
        Must be non-empty and reasonable length.
        
        Args:
            invoice_number: The invoice number to validate
            
        Returns:
            True if valid, False otherwise
        """
        return bool(invoice_number and len(invoice_number) <= 50)
    
    @staticmethod
    def validate_vat_rate(vat_rate: Decimal) -> bool:
        """
        Validate VAT rate.
        
        Saudi Arabia typically uses 0%, 5%, or 15%.
        
        Args:
            vat_rate: The VAT rate to validate
            
        Returns:
            True if valid, False otherwise
        """
        return vat_rate in [Decimal("0"), Decimal("5"), Decimal("15")]
    
    @staticmethod
    def validate_amount(amount: Decimal) -> bool:
        """
        Validate monetary amount.
        
        Must be positive and have at most 2 decimal places.
        
        Args:
            amount: The amount to validate
            
        Returns:
            True if valid, False otherwise
        """
        if amount <= 0:
            return False
        
        # Check decimal places
        decimal_str = str(amount)
        if '.' in decimal_str:
            decimal_places = len(decimal_str.split('.')[1])
            return decimal_places <= 2
        
        return True
    
    @staticmethod
    def validate_invoice_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate complete invoice data for ZATCA compliance.
        
        Args:
            data: The invoice data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['customer_name', 'customer_address', 'invoice_number', 'line_items']
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate invoice number
        if not ZATCAValidator.validate_invoice_number(data['invoice_number']):
            return False, "Invalid invoice number format"
        
        # Validate customer VAT number if provided
        if data.get('customer_vat_number'):
            if not ZATCAValidator.validate_vat_number(data['customer_vat_number']):
                return False, "Invalid customer VAT number format"
        
        # Validate line items
        if not data['line_items']:
            return False, "Invoice must have at least one line item"
        
        for item in data['line_items']:
            if not ZATCAValidator.validate_amount(item.get('quantity', 0)):
                return False, f"Invalid quantity for item: {item.get('description', 'Unknown')}"
            
            if not ZATCAValidator.validate_amount(item.get('unit_price', 0)):
                return False, f"Invalid unit price for item: {item.get('description', 'Unknown')}"
        
        return True, None
