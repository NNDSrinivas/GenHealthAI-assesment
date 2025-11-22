from datetime import datetime
from typing import Dict, Any, Optional
import uuid

class Patient:
    
    def __init__(self, first_name: Optional[str] = None, last_name: Optional[str] = None, 
                 date_of_birth: Optional[str] = None, extracted_from: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.extracted_from = extracted_from  # Source document filename
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert patient object to dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'extracted_from': self.extracted_from,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        """Create patient object from dictionary."""
        patient = cls()
        patient.id = data.get('id', str(uuid.uuid4()))
        patient.first_name = data.get('first_name')
        patient.last_name = data.get('last_name')
        patient.date_of_birth = data.get('date_of_birth')
        patient.extracted_from = data.get('extracted_from')
        
        # Handle datetime fields
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            patient.created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        elif isinstance(created_at, datetime):
            patient.created_at = created_at
        else:
            patient.created_at = datetime.utcnow()
            
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            patient.updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        elif isinstance(updated_at, datetime):
            patient.updated_at = updated_at
        else:
            patient.updated_at = datetime.utcnow()
            
        return patient
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def get_full_name(self) -> str:
        """Get patient's full name."""
        names = [name for name in [self.first_name, self.last_name] if name]
        return ' '.join(names) if names else 'Unknown Patient'