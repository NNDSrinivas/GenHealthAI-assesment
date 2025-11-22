import os
import re
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from docx import Document as DocxDocument

# Optional OCR imports with fallback
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR libraries not available - document processing will be limited to text extraction only")

logger = logging.getLogger(__name__)

class DocumentProcessor:
    
    def __init__(self, tesseract_path: Optional[str] = None, poppler_path: Optional[str] = None):
        if OCR_AVAILABLE and tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.poppler_path = poppler_path
        self.ocr_available = OCR_AVAILABLE
        # Support DOCX always, other formats only if OCR is available
        base_formats = {'.docx', '.txt'}
        ocr_formats = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif'} if OCR_AVAILABLE else set()
        self.supported_formats = base_formats | ocr_formats
        
        # Patient data extraction patterns
        self.name_patterns = [
            r'patient\s*name[:\s]+([a-zA-Z\s,]+)',
            r'name[:\s]+([a-zA-Z\s,]+)',
            r'last\s*name[:\s]+([a-zA-Z\s]+)',
            r'first\s*name[:\s]+([a-zA-Z\s]+)',
        ]
        
        self.dob_patterns = [
            r'date\s*of\s*birth[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'dob[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'birth\s*date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'born[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document and extract patient information.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing extracted text and patient data
        """
        try:
            start_time = datetime.now()
            
            # Determine file type and extract text
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                raw_text = self._extract_pdf_text(file_path)
            elif file_extension == '.docx':
                raw_text = self._extract_docx_text(file_path)
            elif file_extension in {'.png', '.jpg', '.jpeg', '.tiff', '.tif'}:
                raw_text = self._extract_image_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(raw_text)
            
            # Extract patient data
            patient_data = self._extract_patient_data(cleaned_text)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(patient_data, cleaned_text)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'extracted_text': cleaned_text,
                'patient_data': patient_data,
                'confidence_scores': confidence_scores,
                'processing_time': processing_time,
                'error_message': None
            }
            
        except Exception as e:
            logger.error(f"Document processing failed for {file_path}: {str(e)}")
            return {
                'success': False,
                'extracted_text': None,
                'patient_data': {},
                'confidence_scores': {},
                'processing_time': None,
                'error_message': str(e)
            }
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using OCR on converted images."""
        if not self.ocr_available:
            return "OCR processing not available - unable to process PDF files"
            
        try:
            # Convert PDF pages to images
            if self.poppler_path:
                images = pdf2image.convert_from_path(
                    file_path, 
                    poppler_path=self.poppler_path,
                    dpi=300
                )
            else:
                images = pdf2image.convert_from_path(file_path, dpi=300)
            
            extracted_text = []
            
            for i, image in enumerate(images):
                # Preprocess image for better OCR results
                processed_image = self._preprocess_image(np.array(image))
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(
                    processed_image,
                    config='--psm 6 --oem 3'
                )
                
                if text.strip():
                    extracted_text.append(f"--- Page {i+1} ---\n{text}")
            
            return '\n\n'.join(extracted_text)
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {str(e)}")
            raise e
    
    def _extract_image_text(self, file_path: str) -> str:
        """Extract text from image files using OCR."""
        if not self.ocr_available:
            return "OCR processing not available - unable to process image files"
            
        try:
            # Load and preprocess image
            image = Image.open(file_path)
            image_array = np.array(image)
            processed_image = self._preprocess_image(image_array)
            
            # Extract text using Tesseract with optimized config
            text = pytesseract.image_to_string(
                processed_image,
                config='--psm 6 --oem 3'
            )
            
            return text
            
        except Exception as e:
            logger.error(f"Image text extraction failed: {str(e)}")
            raise e
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files."""
        try:
            doc = DocxDocument(file_path)
            paragraphs = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            
            return '\n'.join(paragraphs)
            
        except Exception as e:
            logger.error(f"DOCX text extraction failed: {str(e)}")
            raise e
    
    def _preprocess_image(self, image):
        """
        Preprocess image for better OCR results.
        Applies noise reduction, contrast enhancement, and binarization.
        """
        if not self.ocr_available:
            return image
            
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        # Apply adaptive thresholding for binarization
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        
        # Remove common OCR artifacts
        cleaned = re.sub(r'[^\w\s\-\/\.:,()]', ' ', cleaned)
        
        return cleaned.strip()
    
    def _extract_patient_data(self, text: str) -> Dict[str, Any]:
        """Extract structured patient data from cleaned text."""
        patient_data: Dict[str, Optional[str]] = {
            'first_name': None,
            'last_name': None,
            'date_of_birth': None
        }
        
        text_lower = text.lower()
        
        # Extract names
        names = self._extract_names(text_lower)
        if names:
            patient_data.update(names)
        
        # Extract date of birth
        dob = self._extract_date_of_birth(text_lower)
        if dob:
            patient_data['date_of_birth'] = dob
        
        return patient_data
    
    def _extract_names(self, text: str) -> Dict[str, Optional[str]]:
        """Extract first and last names from text."""
        names: Dict[str, Optional[str]] = {'first_name': None, 'last_name': None}
        
        for pattern in self.name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name_text = match.group(1).strip()
                name_parts = [part.strip().title() for part in name_text.split() if part.strip()]
                
                if len(name_parts) >= 2:
                    names['first_name'] = name_parts[0]
                    names['last_name'] = ' '.join(name_parts[1:])
                    break
                elif len(name_parts) == 1 and not names['first_name']:
                    names['first_name'] = name_parts[0]
        
        return names
    
    def _extract_date_of_birth(self, text: str) -> Optional[str]:
        """Extract date of birth from text."""
        for pattern in self.dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dob_text = match.group(1).strip()
                # Normalize date format
                normalized_dob = self._normalize_date(dob_text)
                return normalized_dob
        
        return None
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to standard format."""
        # Replace different separators with /
        normalized = re.sub(r'[-\.]', '/', date_str)
        
        # Handle different date formats
        parts = normalized.split('/')
        if len(parts) == 3:
            month, day, year = parts
            
            # Ensure 4-digit year
            if len(year) == 2:
                current_year = datetime.now().year
                year_int = int(year)
                # Assume dates > 50 are 19xx, others are 20xx
                if year_int > 50:
                    year = f"19{year}"
                else:
                    year = f"20{year}"
            
            return f"{month.zfill(2)}/{day.zfill(2)}/{year}"
        
        return date_str
    
    def _calculate_confidence_scores(self, patient_data: Dict[str, Any], text: str) -> Dict[str, float]:
        """Calculate confidence scores for extracted data."""
        confidence_scores = {}
        
        for field, value in patient_data.items():
            if value:
                # Simple confidence based on text context and format
                if field in ['first_name', 'last_name']:
                    confidence_scores[field] = self._name_confidence(value, text)
                elif field == 'date_of_birth':
                    confidence_scores[field] = self._date_confidence(value, text)
                else:
                    confidence_scores[field] = 0.7  # Default confidence
            else:
                confidence_scores[field] = 0.0
        
        return confidence_scores
    
    def _name_confidence(self, name: str, text: str) -> float:
        """Calculate confidence score for extracted names."""
        base_confidence = 0.6
        
        # Boost confidence if name appears near common clinical terms
        clinical_context = ['patient', 'name', 'client', 'individual']
        context_boost = sum(1 for term in clinical_context if term in text.lower()) * 0.1
        
        # Boost confidence for proper capitalization
        capitalization_boost = 0.1 if name.istitle() else 0
        
        # Boost confidence for reasonable name length
        length_boost = 0.1 if 2 <= len(name) <= 30 else 0
        
        return min(1.0, base_confidence + context_boost + capitalization_boost + length_boost)
    
    def _date_confidence(self, date: str, text: str) -> float:
        """Calculate confidence score for extracted dates."""
        base_confidence = 0.7
        
        # Boost confidence if date format is standard
        format_boost = 0.2 if re.match(r'\d{2}/\d{2}/\d{4}', date) else 0
        
        # Boost confidence if date appears near DOB-related terms
        dob_context = ['birth', 'born', 'dob']
        context_boost = sum(1 for term in dob_context if term in text.lower()) * 0.05
        
        return min(1.0, base_confidence + format_boost + context_boost)