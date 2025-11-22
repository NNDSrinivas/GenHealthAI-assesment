import logging
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from flask import current_app
from datetime import datetime
import uuid

from app.models.patient import Patient
from app.models.order import Order
from app.models.document import Document

logger = logging.getLogger(__name__)

class DatabaseService:
    
    def __init__(self):
        """Initialize database service with MongoDB collections."""
        self.db: Optional[Any] = None
        self.patients_collection: Optional[Collection] = None
        self.orders_collection: Optional[Collection] = None
        self.documents_collection: Optional[Collection] = None
        self.activity_logs_collection: Optional[Collection] = None
    
    def init_db(self, db):
        """Initialize database collections."""
        self.db = db
        if db is not None:
            self.patients_collection = db.patients
            self.orders_collection = db.orders
            self.documents_collection = db.documents
            self.activity_logs_collection = db.activity_logs
            
            # Create indexes for better performance
            self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for improved query performance."""
        if not all([self.patients_collection, self.orders_collection, 
                   self.documents_collection, self.activity_logs_collection]):
            logger.error("Collections not initialized. Cannot create indexes.")
            return
        
        try:
            # Patient indexes
            if self.patients_collection is not None:
                self.patients_collection.create_index([("first_name", 1), ("last_name", 1)])
                self.patients_collection.create_index("date_of_birth")
                self.patients_collection.create_index("created_at")
            
            # Order indexes
            if self.orders_collection is not None:
                self.orders_collection.create_index("patient_id")
                self.orders_collection.create_index("status")
                self.orders_collection.create_index("created_at")
            
            # Document indexes
            if self.documents_collection is not None:
                self.documents_collection.create_index("order_id")
                self.documents_collection.create_index("status")
                self.documents_collection.create_index("filename")
            
            # Activity log indexes
            if self.activity_logs_collection is not None:
                self.activity_logs_collection.create_index("timestamp")
                self.activity_logs_collection.create_index("action")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create database indexes: {str(e)}")
    
    def log_activity(self, action: str, entity_type: str, entity_id: str, 
                    details: Optional[Dict[str, Any]] = None):
        """Log user activity for audit trails."""
        if self.activity_logs_collection is None:
            logger.warning("Activity logs collection not initialized. Cannot log activity.")
            return
        
        try:
            log_entry = {
                'id': str(uuid.uuid4()),
                'action': action,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'details': details or {},
                'timestamp': datetime.utcnow(),
                'ip_address': None,  # Could be extracted from request context
                'user_agent': None   # Could be extracted from request context
            }
            
            self.activity_logs_collection.insert_one(log_entry)
            logger.info(f"Activity logged: {action} on {entity_type} {entity_id}")
            
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
    
    # Patient CRUD Operations
    def create_patient(self, patient: Patient) -> bool:
        """Create a new patient record."""
        if self.patients_collection is None:
            logger.error("Patients collection not initialized. Cannot create patient.")
            return False
        
        try:
            result = self.patients_collection.insert_one(patient.to_dict())
            
            if result.inserted_id:
                self.log_activity('CREATE', 'patient', patient.id)
                logger.info(f"Patient created successfully: {patient.id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to create patient: {str(e)}")
            return False
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Retrieve a patient by ID."""
        if self.patients_collection is None:
            logger.error("Patients collection not initialized. Cannot retrieve patient.")
            return None
        
        try:
            patient_data = self.patients_collection.find_one({'id': patient_id})
            
            if patient_data:
                self.log_activity('READ', 'patient', patient_id)
                return Patient.from_dict(patient_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve patient {patient_id}: {str(e)}")
            return None
    
    def get_patients(self, skip: int = 0, limit: int = 10) -> List[Patient]:
        """Retrieve patients with pagination."""
        if self.patients_collection is None:
            logger.error("Patients collection not initialized. Cannot retrieve patients.")
            return []
        
        try:
            cursor = self.patients_collection.find().sort('created_at', -1).skip(skip).limit(limit)
            patients = [Patient.from_dict(data) for data in cursor]
            
            self.log_activity('LIST', 'patient', 'all', {'count': len(patients)})
            return patients
            
        except Exception as e:
            logger.error(f"Failed to retrieve patients: {str(e)}")
            return []
    
    def update_patient(self, patient_id: str, updates: Dict[str, Any]) -> bool:
        """Update patient information."""
        if self.patients_collection is None:
            logger.error("Patients collection not initialized. Cannot update patient.")
            return False
        
        try:
            # Add updated timestamp
            updates['updated_at'] = datetime.utcnow()
            
            result = self.patients_collection.update_one(
                {'id': patient_id}, 
                {'$set': updates}
            )
            
            if result.modified_count > 0:
                self.log_activity('UPDATE', 'patient', patient_id, updates)
                logger.info(f"Patient updated successfully: {patient_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update patient {patient_id}: {str(e)}")
            return False
    
    def find_patient_by_name(self, first_name: str, last_name: str) -> Optional[Patient]:
        """Find patient by name (for avoiding duplicates)."""
        if self.patients_collection is None:
            logger.error("Patients collection not initialized. Cannot find patient.")
            return None
        
        try:
            patient_data = self.patients_collection.find_one({
                'first_name': {'$regex': f'^{first_name}$', '$options': 'i'},
                'last_name': {'$regex': f'^{last_name}$', '$options': 'i'}
            })
            
            if patient_data:
                return Patient.from_dict(patient_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to find patient by name: {str(e)}")
            return None
    
    # Order CRUD Operations
    def create_order(self, order: Order) -> bool:
        """Create a new order."""
        if self.orders_collection is None:
            logger.error("Orders collection not initialized. Cannot create order.")
            return False
        
        try:
            result = self.orders_collection.insert_one(order.to_dict())
            
            if result.inserted_id:
                self.log_activity('CREATE', 'order', order.id)
                logger.info(f"Order created successfully: {order.id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieve an order by ID."""
        if self.orders_collection is None:
            logger.error("Orders collection not initialized. Cannot retrieve order.")
            return None
        
        try:
            order_data = self.orders_collection.find_one({'id': order_id})
            
            if order_data:
                self.log_activity('read', 'order', order_id)
                return Order.from_dict(order_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve order {order_id}: {str(e)}")
            return None
    
    def get_orders(self, skip: int = 0, limit: int = 10) -> List[Order]:
        """Retrieve orders with pagination."""
        if self.orders_collection is None:
            logger.error("Orders collection not initialized. Cannot retrieve orders.")
            return []
        
        try:
            cursor = self.orders_collection.find().sort('created_at', -1).skip(skip).limit(limit)
            orders = [Order.from_dict(data) for data in cursor]
            
            self.log_activity('LIST', 'order', 'all', {'count': len(orders)})
            return orders
            
        except Exception as e:
            logger.error(f"Failed to retrieve orders: {str(e)}")
            return []
    
    def update_order(self, order_id: str, updates: Dict[str, Any]) -> bool:
        """Update order information."""
        if self.orders_collection is None:
            logger.error("Orders collection not initialized. Cannot update order.")
            return False
        
        try:
            # Add updated timestamp
            updates['updated_at'] = datetime.utcnow()
            
            result = self.orders_collection.update_one(
                {'id': order_id}, 
                {'$set': updates}
            )
            
            if result.modified_count > 0:
                self.log_activity('UPDATE', 'order', order_id, updates)
                logger.info(f"Order updated successfully: {order_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update order {order_id}: {str(e)}")
            return False
    
    def delete_order(self, order_id: str) -> bool:
        """Delete an order."""
        if self.orders_collection is None:
            logger.error("Orders collection not initialized. Cannot delete order.")
            return False
        
        try:
            result = self.orders_collection.delete_one({'id': order_id})
            
            if result.deleted_count > 0:
                self.log_activity('DELETE', 'order', order_id)
                logger.info(f"Order deleted successfully: {order_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete order {order_id}: {str(e)}")
            return False
    
    # Document CRUD Operations
    def create_document(self, document: Document) -> bool:
        """Create a new document record."""
        if self.documents_collection is None:
            logger.error("Documents collection not initialized. Cannot create document.")
            return False
        
        try:
            result = self.documents_collection.insert_one(document.to_dict())
            
            if result.inserted_id:
                self.log_activity('CREATE', 'document', document.id)
                logger.info(f"Document created successfully: {document.id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            return False
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        if self.documents_collection is None:
            logger.error("Documents collection not initialized. Cannot retrieve document.")
            return None
        
        try:
            doc_data = self.documents_collection.find_one({'id': document_id})
            
            if doc_data:
                self.log_activity('read', 'document', document_id)
                return Document.from_dict(doc_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {str(e)}")
            return None
    
    def get_documents_by_order(self, order_id: str) -> List[Document]:
        """Retrieve all documents for a specific order."""
        if self.documents_collection is None:
            logger.error("Documents collection not initialized. Cannot retrieve documents.")
            return []
        
        try:
            cursor = self.documents_collection.find({'order_id': order_id})
            documents = [Document.from_dict(data) for data in cursor]
            
            self.log_activity('LIST', 'document', order_id, {'count': len(documents)})
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents for order {order_id}: {str(e)}")
            return []
    
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update document information."""
        if self.documents_collection is None:
            logger.error("Documents collection not initialized. Cannot update document.")
            return False
        
        try:
            # Add updated timestamp
            updates['updated_at'] = datetime.utcnow()
            
            result = self.documents_collection.update_one(
                {'id': document_id}, 
                {'$set': updates}
            )
            
            if result.modified_count > 0:
                self.log_activity('UPDATE', 'document', document_id, updates)
                logger.info(f"Document updated successfully: {document_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            return False
    
    def get_activity_logs(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve activity logs with pagination."""
        if self.activity_logs_collection is None:
            logger.error("Activity logs collection not initialized. Cannot retrieve logs.")
            return []
        
        try:
            cursor = self.activity_logs_collection.find().sort('timestamp', -1).skip(skip).limit(limit)
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Failed to retrieve activity logs: {str(e)}")
            return []


# Global database service instance
db_service = DatabaseService()