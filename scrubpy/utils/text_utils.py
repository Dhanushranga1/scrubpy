"""Text processing utilities for PDF generation and other text operations."""

import re


def clean_text_for_pdf(text):
    """
    Remove emojis and non-ASCII characters for PDF compatibility.
    
    Args:
        text (str): Input text that may contain emojis or non-ASCII characters
        
    Returns:
        str: Cleaned text safe for PDF generation
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Replace common bullet points with hyphens
    text = text.replace("•", "-")
    text = text.replace("◆", "-")
    text = text.replace("▪", "-")
    
    # Remove emojis and other non-ASCII characters
    cleaned_text = re.sub(r"[^\x00-\x7F]+", "", text)
    
    return cleaned_text


def safe_filename(filename):
    """
    Create a safe filename by removing/replacing invalid characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Safe filename for filesystem use
    """
    # Remove invalid characters for filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    return filename


def truncate_text(text, max_length=50):
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."