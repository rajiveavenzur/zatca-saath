"""Arabic text helper utilities."""
import re
from typing import Optional


def is_arabic_text(text: str) -> bool:
    """
    Check if text contains Arabic characters.
    
    Args:
        text: The text to check
        
    Returns:
        True if text contains Arabic characters, False otherwise
    """
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')
    return bool(arabic_pattern.search(text))


def clean_arabic_text(text: str) -> str:
    """
    Clean and normalize Arabic text.
    
    Args:
        text: The text to clean
        
    Returns:
        The cleaned text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Normalize Arabic characters
    text = text.replace('ك', 'ك')  # Normalize Kaf
    text = text.replace('ي', 'ي')  # Normalize Yaa
    
    return text.strip()


def format_arabic_number(number: float, decimals: int = 2) -> str:
    """
    Format number with Arabic locale conventions.
    
    Args:
        number: The number to format
        decimals: Number of decimal places
        
    Returns:
        The formatted number string
    """
    # Use Western Arabic numerals (0-9) for ZATCA compliance
    return f"{number:.{decimals}f}"


def reverse_arabic_text_for_display(text: str) -> str:
    """
    Reverse Arabic text for proper RTL display in some contexts.
    
    Note: ReportLab handles RTL automatically with proper fonts,
    but this utility is here for edge cases.
    
    Args:
        text: The text to reverse
        
    Returns:
        The reversed text if Arabic, original otherwise
    """
    if is_arabic_text(text):
        return text[::-1]
    return text
