from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

class Order::
    
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    VALID_STATUSES = [STATUS_PENDING, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_CANCELLED]
    
    def __init__(self, patient_id: Optional[str] = None, order_type: Optional[str] = None, 
                 description: Optional[str] = None, documents: Optional[List[str]] = None):
        self.id = str(uuid.uuid4())
        self.patient_id = patient_id
        self.order_type = order_type or 'general'
        self.description = description
        self.status = self.STATUS_PENDING
        self.documents = documents or []  # List of document IDs
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order object to dictionary."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'order_type': self.order_type,
            'description': self.description,
            'status': self.status,
            'documents': self.documents,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Create order object from dictionary."""
        order = cls()
        order.id = data.get('id', str(uuid.uuid4()))
        order.patient_id = data.get('patient_id')
        order.order_type = data.get('order_type', 'general')
        order.description = data.get('description')
        order.status = data.get('status', cls.STATUS_PENDING)
        order.documents = data.get('documents', [])
        
        # Handle datetime fields
        for field in ['created_at', 'updated_at', 'completed_at']:
            date_value = data.get(field)
            if isinstance(date_value, str):
                setattr(order, field, datetime.fromisoformat(date_value.replace('Z', '+00:00')))
            elif isinstance(date_value, datetime):
                setattr(order, field, date_value)
            elif field in ['created_at', 'updated_at']:
                setattr(order, field, datetime.utcnow())
            else:
                setattr(order, field, None)
                
        return order
    
    def update_status(self, new_status: str):
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {self.VALID_STATUSES}")
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == self.STATUS_COMPLETED:
            self.completed_at = datetime.utcnow()
    
    def add_document(self, document_id: str):
        if document_id not in self.documents:
            self.documents.append(document_id)
            self.updated_at = datetime.utcnow()
    
    def remove_document(self, document_id: str):
        if document_id in self.documents:
            self.documents.remove(document_id)
            self.updated_at = datetime.utcnow()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                if key == 'status':
                    self.update_status(value)
                else:
                    setattr(self, key, value)
        
        if 'status' not in kwargs:  # Only update timestamp if status wasn't changed
            self.updated_at = datetime.utcnow()