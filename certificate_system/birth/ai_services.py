import os
from PIL import Image
import pytesseract
import re

def analyze_document(file):
    """Analyze uploaded documents and provide suggestions"""
    suggestions = []
    
    # Check if file is an image (OCR processing)
    if file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            text = pytesseract.image_to_string(Image.open(file))
            
            # Example checks (customize based on your requirements)
            if "birth" in file.name.lower() and "hospital" not in text.lower():
                suggestions.append("Hospital name not clearly visible in birth certificate")
            
            if "aadhaar" in file.name.lower() and not re.search(r"\d{4}\s?\d{4}\s?\d{4}", text):
                suggestions.append("Aadhaar number not clearly visible")
                
        except Exception as e:
            suggestions.append(f"Could not process image: {str(e)}")
    
    return {
        'is_valid': len(suggestions) == 0,
        'suggestions': suggestions
    }