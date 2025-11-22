"""Simple in-memory database for testing without MongoDB."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.models.patient import Patient
from app.models.order import Order
from app.models.document import Document

logger = logging.getLogger(__name__)

class InMemoryDatabase::
    
    def __init__(self):
        self.patients = {}
        self.orders = {}  
        self.documents = {}
        self.activity_logs = []
    
    def log_activity(self, action: str, entity_type: str, entity_id: str, 
                    details: Optional[Dict[str, Any]] = None):
        """Log activity."""
        log_entry = {
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'details': details or {},
            'timestamp': datetime.utcnow()
        }
        self.activity_logs.append(log_entry)
        logger.info(f"Activity logged: {action} on {entity_type} {entity_id}")
    
    # Patient operations
    def create_patient(self, patient: Patient) -> bool:
        self.patients[patient.id] = patient
        self.log_activity('CREATE', 'patient', patient.id)
        return True
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        return self.patients.get(patient_id)
    
    def get_patients(self, skip: int = 0, limit: int = 10) -> List[Patient]:
        patient_list = list(self.patients.values())
        return patient_list[skip:skip+limit]
    
    def find_patient_by_name(self, first_name: str, last_name: str) -> Optional[Patient]:
        for patient in self.patients.values():
            if (patient.first_name and patient.first_name.lower() == first_name.lower() and
                patient.last_name and patient.last_name.lower() == last_name.lower()):
                return patient
        return None
    
    # Order operations
    def create_order(self, order: Order) -> bool:
        self.orders[order.id] = order
        self.log_activity('CREATE', 'order', order.id)
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)
    
    def get_orders(self, skip: int = 0, limit: int = 10) -> List[Order]:
        order_list = list(self.orders.values())
        return order_list[skip:skip+limit]
    
    def update_order(self, order_id: str, updates: Dict[str, Any]) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            for key, value in updates.items():
                if hasattr(order, key):
                    setattr(order, key, value)
            order.updated_at = datetime.utcnow()
            self.log_activity('UPDATE', 'order', order_id, updates)
            return True
        return False
    
    def delete_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            del self.orders[order_id]
            self.log_activity('DELETE', 'order', order_id)
            return True
        return False
    
    # Document operations
    def create_document(self, document: Document) -> bool:
        self.documents[document.id] = document
        self.log_activity('CREATE', 'document', document.id)
        return True
    
    def get_document(self, document_id: str) -> Optional[Document]:
        return self.documents.get(document_id)
    
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        if document_id in self.documents:
            document = self.documents[document_id]
            for key, value in updates.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            document.updated_at = datetime.utcnow()
            self.log_activity('UPDATE', 'document', document_id, updates)
            return True
        return False
    
    def get_documents_by_order(self, order_id: str) -> List[Document]:
        return [doc for doc in self.documents.values() if doc.order_id == order_id]
    
    def get_activity_logs(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return self.activity_logs[skip:skip+limit]

# Global instance for testing
memory_db = InMemoryDatabase()