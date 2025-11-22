"""Utility functions and helpers for the clinical document processing API."""

import os
import re
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(original_filename)
    return f"{timestamp}_{name}_{str(uuid.uuid4())[:8]}{ext}"

def validate_file_size(file_path: str, max_size_mb: int = 16) -> bool:
    """Validate that file size is within limits."""
    if not os.path.exists(file_path):
        return False
    
    file_size = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text from OCR."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common OCR artifacts
    text = re.sub(r'[^\w\s\-\/\.:,()&]', ' ', text)
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()

def normalize_patient_name(name: str) -> str:
    """Normalize patient name for consistency."""
    if not name:
        return ""
    
    # Remove extra spaces and convert to title case
    normalized = ' '.join(name.split()).title()
    
    # Handle common name prefixes/suffixes
    prefixes = ['Dr', 'Mr', 'Mrs', 'Ms', 'Miss']
    suffixes = ['Jr', 'Sr', 'II', 'III', 'IV']
    
    # This is a simplified normalization
    return normalized

def format_date_of_birth(dob_str: str) -> Optional[str]:
    """Format date of birth to standard format MM/DD/YYYY."""
    if not dob_str:
        return None
    
    # Common date patterns
    patterns = [
        r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
        r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})',   # MM/DD/YY or MM-DD-YY
        r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',   # YYYY/MM/DD or YYYY-MM-DD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, dob_str)
        if match:
            parts = match.groups()
            
            if len(parts[2]) == 4:  # Full year
                if len(parts[0]) == 4:  # YYYY/MM/DD format
                    year, month, day = parts
                else:  # MM/DD/YYYY format
                    month, day, year = parts
            else:  # 2-digit year
                month, day, year_short = parts
                year_int = int(year_short)
                # Assume years > 50 are 19xx, others are 20xx
                if year_int > 50:
                    year = f"19{year_short}"
                else:
                    year = f"20{year_short}"
            
            # Validate month and day
            try:
                month_int = int(month)
                day_int = int(day)
                
                if 1 <= month_int <= 12 and 1 <= day_int <= 31:
                    return f"{month.zfill(2)}/{day.zfill(2)}/{year}"
            except ValueError:
                continue
    
    return dob_str  # Return original if no pattern matched

def calculate_processing_stats(documents: list) -> Dict[str, Any]:
    """Calculate processing statistics for a list of documents."""
    if not documents:
        return {
            'total_documents': 0,
            'completed': 0,
            'processing': 0,
            'failed': 0,
            'avg_processing_time': 0,
            'success_rate': 0
        }
    
    total = len(documents)
    completed = sum(1 for doc in documents if doc.status == 'completed')
    processing = sum(1 for doc in documents if doc.status == 'processing')
    failed = sum(1 for doc in documents if doc.status == 'failed')
    
    # Calculate average processing time for completed documents
    processing_times = [doc.processing_time for doc in documents 
                       if doc.processing_time and doc.status == 'completed']
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    success_rate = (completed / total * 100) if total > 0 else 0
    
    return {
        'total_documents': total,
        'completed': completed,
        'processing': processing,
        'failed': failed,
        'avg_processing_time': round(avg_processing_time, 2),
        'success_rate': round(success_rate, 2)
    }

def create_api_response(success: bool, data: Any = None, error: Optional[str] = None,
                       message: Optional[str] = None, status_code: int = 200) -> Dict[str, Any]:
    """Create standardized API response format."""
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
    
    return response

def validate_patient_data(patient_data: Dict[str, Any]) -> Dict[str, str]:
    """Validate extracted patient data and return validation errors."""
    errors = {}
    
    # Check first name
    first_name = patient_data.get('first_name', '').strip()
    if not first_name:
        errors['first_name'] = 'First name is required'
    elif len(first_name) < 2 or len(first_name) > 50:
        errors['first_name'] = 'First name must be between 2 and 50 characters'
    elif not re.match(r'^[a-zA-Z\s\-\'\.]+$', first_name):
        errors['first_name'] = 'First name contains invalid characters'
    
    # Check last name
    last_name = patient_data.get('last_name', '').strip()
    if not last_name:
        errors['last_name'] = 'Last name is required'
    elif len(last_name) < 2 or len(last_name) > 50:
        errors['last_name'] = 'Last name must be between 2 and 50 characters'
    elif not re.match(r'^[a-zA-Z\s\-\'\.]+$', last_name):
        errors['last_name'] = 'Last name contains invalid characters'
    
    # Check date of birth
    dob = patient_data.get('date_of_birth', '').strip()
    if dob:
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', dob):
            errors['date_of_birth'] = 'Date of birth must be in MM/DD/YYYY format'
        else:
            try:
                month, day, year = dob.split('/')
                datetime(int(year), int(month), int(day))
            except ValueError:
                errors['date_of_birth'] = 'Invalid date of birth'
    
    return errors

def get_file_type_info(filename: str) -> Dict[str, Any]:
    """Get information about file type and processing requirements."""
    if not filename:
        return {'supported': False, 'type': 'unknown'}
    
    ext = os.path.splitext(filename)[1].lower()
    
    file_types = {
        '.pdf': {
            'supported': True,
            'type': 'pdf',
            'description': 'Portable Document Format',
            'ocr_required': True,
            'preprocessing': 'pdf_to_image'
        },
        '.png': {
            'supported': True,
            'type': 'image',
            'description': 'Portable Network Graphics',
            'ocr_required': True,
            'preprocessing': 'image_enhancement'
        },
        '.jpg': {
            'supported': True,
            'type': 'image',
            'description': 'JPEG Image',
            'ocr_required': True,
            'preprocessing': 'image_enhancement'
        },
        '.jpeg': {
            'supported': True,
            'type': 'image',
            'description': 'JPEG Image',
            'ocr_required': True,
            'preprocessing': 'image_enhancement'
        },
        '.tiff': {
            'supported': True,
            'type': 'image',
            'description': 'Tagged Image File Format',
            'ocr_required': True,
            'preprocessing': 'image_enhancement'
        },
        '.tif': {
            'supported': True,
            'type': 'image',
            'description': 'Tagged Image File Format',
            'ocr_required': True,
            'preprocessing': 'image_enhancement'
        },
        '.docx': {
            'supported': True,
            'type': 'document',
            'description': 'Microsoft Word Document',
            'ocr_required': False,
            'preprocessing': 'text_extraction'
        }
    }
    
    return file_types.get(ext, {'supported': False, 'type': 'unknown'})