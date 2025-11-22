import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from marshmallow import Schema, fields, ValidationError

from app.models.document import Document
from app.models.patient import Patient
from app.services.database import db_service
from app.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

# Create blueprint for documents API
documents_bp = Blueprint('documents', __name__)

# Initialize document processor
doc_processor = DocumentProcessor(
    tesseract_path=os.getenv('TESSERACT_PATH'),
    poppler_path=os.getenv('POPPLER_PATH')
)

def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'tif', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a document to extract patient information.
    This endpoint accepts PDF, image, and DOCX files and uses OCR to extract
    patient data including first name, last name, and date of birth.
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not supported. Allowed: PDF, PNG, JPG, TIFF, DOCX'
            }), 400
        
        # Get optional order_id from form data
        order_id = request.form.get('order_id')
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Save file to upload directory
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Create document record
        document = Document(
            filename=unique_filename,
            file_path=file_path,
            file_type=os.path.splitext(filename)[1].lower(),
            order_id=order_id
        )
        
        # Get file size
        document.get_file_size()
        
        # Save document to database
        if not db_service.create_document(document):
            # Clean up file if database save fails
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({
                'success': False,
                'error': 'Failed to save document record'
            }), 500
        
        # Process document asynchronously in background
        # For this assessment, we'll process synchronously
        document.update_status(Document.STATUS_PROCESSING)
        db_service.update_document(document.id, {'status': document.status})
        
        # Process the document using OCR
        processing_result = doc_processor.process_document(file_path)
        
        if processing_result['success']:
            # Update document with extracted data
            document.set_extracted_data(
                processing_result['extracted_text'],
                processing_result['patient_data'],
                processing_result['confidence_scores']
            )
            document.processing_time = processing_result['processing_time']
            document.update_status(Document.STATUS_COMPLETED)
            
            # Try to create or find patient record
            patient_created = False
            patient_id = None
            
            patient_data = processing_result['patient_data']
            if patient_data.get('first_name') and patient_data.get('last_name'):
                # Check if patient already exists
                existing_patient = db_service.find_patient_by_name(
                    patient_data['first_name'], 
                    patient_data['last_name']
                )
                
                if existing_patient:
                    patient_id = existing_patient.id
                    logger.info(f"Found existing patient: {patient_id}")
                else:
                    # Create new patient record
                    new_patient = Patient(
                        first_name=patient_data['first_name'],
                        last_name=patient_data['last_name'],
                        date_of_birth=patient_data['date_of_birth'],
                        extracted_from=unique_filename
                    )
                    
                    if db_service.create_patient(new_patient):
                        patient_id = new_patient.id
                        patient_created = True
                        logger.info(f"Created new patient: {patient_id}")
            
            # Update document in database
            update_data = {
                'status': document.status,
                'extracted_text': document.extracted_text,
                'patient_data': document.patient_data,
                'confidence_scores': document.confidence_scores,
                'processing_time': document.processing_time,
                'processed_at': document.processed_at
            }
            
            db_service.update_document(document.id, update_data)
            
            return jsonify({
                'success': True,
                'document': document.to_dict(),
                'patient_created': patient_created,
                'patient_id': patient_id,
                'message': 'Document processed successfully'
            }), 200
            
        else:
            # Processing failed
            document.update_status(Document.STATUS_FAILED, processing_result['error_message'])
            db_service.update_document(document.id, {
                'status': document.status,
                'error_message': document.error_message
            })
            
            return jsonify({
                'success': False,
                'document': document.to_dict(),
                'error': 'Document processing failed',
                'message': processing_result['error_message']
            }), 422
            
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to upload document',
            'message': str(e)
        }), 500

@documents_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details and processing results."""
    try:
        # Retrieve document from database
        document = db_service.get_document(document_id)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': document.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve document',
            'message': str(e)
        }), 500

@documents_bp.route('/batch', methods=['POST'])
def batch_upload():
    """
    Upload multiple documents for batch processing.
    Simulates batch processing capabilities for large document volumes.
    """
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            }), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                'success': False,
                'error': 'No files selected'
            }), 400
        
        # Get optional order_id
        order_id = request.form.get('order_id')
        
        results = []
        successful_count = 0
        failed_count = 0
        
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    # Process each file similar to single upload
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    # Create document record
                    document = Document(
                        filename=unique_filename,
                        file_path=file_path,
                        file_type=os.path.splitext(filename)[1].lower(),
                        order_id=order_id
                    )
                    document.get_file_size()
                    
                    if db_service.create_document(document):
                        results.append({
                            'filename': filename,
                            'document_id': document.id,
                            'status': 'uploaded',
                            'message': 'File uploaded successfully, processing will begin shortly'
                        })
                        successful_count += 1
                    else:
                        # Clean up file if database save fails
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        results.append({
                            'filename': filename,
                            'status': 'failed',
                            'error': 'Failed to save document record'
                        })
                        failed_count += 1
                        
                except Exception as e:
                    results.append({
                        'filename': file.filename,
                        'status': 'failed',
                        'error': str(e)
                    })
                    failed_count += 1
            else:
                results.append({
                    'filename': file.filename,
                    'status': 'failed',
                    'error': 'File type not supported'
                })
                failed_count += 1
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_files': len(files),
                'successful': successful_count,
                'failed': failed_count
            },
            'message': f'Batch upload completed. {successful_count} files uploaded successfully.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Batch upload failed',
            'message': str(e)
        }), 500

@documents_bp.route('/test', methods=['POST'])
def test_extraction():
    """
    Test endpoint for document processing without saving to database.
    Useful for testing OCR capabilities with the assessment sample PDF.
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'File type not supported'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join('/tmp', f"test_{filename}")
        file.save(temp_path)
        
        try:
            # Process document
            result = doc_processor.process_document(temp_path)
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                'success': result['success'],
                'extracted_text': result['extracted_text'],
                'patient_data': result['patient_data'],
                'confidence_scores': result['confidence_scores'],
                'processing_time': result['processing_time'],
                'error_message': result['error_message']
            }), 200
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    except Exception as e:
        logger.error(f"Error in test extraction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Test extraction failed',
            'message': str(e)
        }), 500