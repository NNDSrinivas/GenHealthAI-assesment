from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
import os

class Document::
    
    STATUS_UPLOADED = 'uploaded'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    VALID_STATUSES = [STATUS_UPLOADED, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_FAILED]
    
    def __init__(self, filename: Optional[str] = None, file_path: Optional[str] = None, 
                 file_type: Optional[str] = None, order_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.order_id = order_id
        self.status = self.STATUS_UPLOADED
        self.file_size = 0
        
        # OCR and extraction results
        self.extracted_text = None
        self.patient_data = {}
        self.confidence_scores = {}
        
        # Processing metadata
        self.processing_time = None
        self.error_message = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.processed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document object to dictionary."""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'order_id': self.order_id,
            'status': self.status,
            'file_size': self.file_size,
            'extracted_text': self.extracted_text,
            'patient_data': self.patient_data,
            'confidence_scores': self.confidence_scores,
            'processing_time': self.processing_time,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document object from dictionary."""
        doc = cls()
        doc.id = data.get('id', str(uuid.uuid4()))
        doc.filename = data.get('filename')
        doc.file_path = data.get('file_path')
        doc.file_type = data.get('file_type')
        doc.order_id = data.get('order_id')
        doc.status = data.get('status', cls.STATUS_UPLOADED)
        doc.file_size = data.get('file_size', 0)
        doc.extracted_text = data.get('extracted_text')
        doc.patient_data = data.get('patient_data', {})
        doc.confidence_scores = data.get('confidence_scores', {})
        doc.processing_time = data.get('processing_time')
        doc.error_message = data.get('error_message')
        
        # Handle datetime fields
        for field in ['created_at', 'updated_at', 'processed_at']:
            date_value = data.get(field)
            if isinstance(date_value, str):
                setattr(doc, field, datetime.fromisoformat(date_value.replace('Z', '+00:00')))
            elif isinstance(date_value, datetime):
                setattr(doc, field, date_value)
            elif field in ['created_at', 'updated_at']:
                setattr(doc, field, datetime.utcnow())
            else:
                setattr(doc, field, None)
                
        return doc
    
    def update_status(self, new_status: str, error_message: Optional[str] = None):
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {self.VALID_STATUSES}")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status in [self.STATUS_COMPLETED, self.STATUS_FAILED]:
            self.processed_at = datetime.utcnow()
        
        if error_message:
            self.error_message = error_message
    
    def set_extracted_data(self, text: str, patient_data: Dict[str, Any], 
                          confidence_scores: Optional[Dict[str, float]] = None):
        """Set the extracted OCR data and patient information."""
        self.extracted_text = text
        self.patient_data = patient_data
        self.confidence_scores = confidence_scores or {}
        self.updated_at = datetime.utcnow()
    
    def get_file_size(self):
        if self.file_path and os.path.exists(self.file_path):
            self.file_size = os.path.getsize(self.file_path)
            return self.file_size
        return 0
    
    def is_processed(self) -> bool:
        """Check if document has been processed."""
        return self.status in [self.STATUS_COMPLETED, self.STATUS_FAILED]
    
    def has_patient_data(self) -> bool:
        """Check if patient data was successfully extracted."""
        return bool(self.patient_data and any(self.patient_data.values()))