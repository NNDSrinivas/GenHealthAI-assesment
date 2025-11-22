from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
import logging
from typing import Dict, Any, cast

from app.models.patient import Patient
from app.services.database import db_service

logger = logging.getLogger(__name__)

# Create blueprint for patients API
patients_bp = Blueprint('patients', __name__)

class PatientSchema(Schema):
    """Schema for patient validation and serialization."""
    first_name = fields.Str(required=False, allow_none=True, load_default=None)
    last_name = fields.Str(required=False, allow_none=True, load_default=None) 
    date_of_birth = fields.Str(required=False, allow_none=True, load_default=None)
    extracted_from = fields.Str(required=False, allow_none=True, load_default=None)
    
    class Meta:
        unknown = 'EXCLUDE'

patient_schema = PatientSchema()

@patients_bp.route('', methods=['GET'])
def get_patients():
    """
    Get list of patients with pagination.
    """
    try:
        # Get pagination parameters
        skip = request.args.get('skip', 0, type=int)
        limit = min(request.args.get('limit', 10, type=int), 100)  # Max 100 items
        
        # Retrieve patients from database
        patients = db_service.get_patients(skip=skip, limit=limit)
        
        # Convert to dictionaries
        patients_data = [patient.to_dict() for patient in patients]
        
        return jsonify({
            'success': True,
            'data': patients_data,
            'total': len(patients_data),
            'skip': skip,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving patients: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve patients',
            'message': str(e)
        }), 500

@patients_bp.route('/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """
    Get a specific patient by ID.
    """
    try:
        # Retrieve patient from database
        patient = db_service.get_patient(patient_id)
        
        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': patient.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving patient {patient_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve patient',
            'message': str(e)
        }), 500

@patients_bp.route('', methods=['POST'])
def create_patient():
    """
    Create a new patient manually (usually patients are created via document processing).
    """
    try:
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        # Validate input schema
        try:
            validated_data = cast(Dict[str, Any], patient_schema.load(json_data))
        except ValidationError as err:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': err.messages
            }), 400
        
        # Create patient object
        patient = Patient(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            date_of_birth=validated_data.get('date_of_birth'),
            extracted_from=validated_data.get('extracted_from')
        )
        
        # Save to database
        if db_service.create_patient(patient):
            return jsonify({
                'success': True,
                'data': patient.to_dict(),
                'message': 'Patient created successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create patient'
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create patient',
            'message': str(e)
        }), 500

@patients_bp.route('/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """
    Update patient information.
    """
    try:
        # Check if patient exists
        existing_patient = db_service.get_patient(patient_id)
        if not existing_patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        # Validate input schema
        try:
            validated_data = cast(Dict[str, Any], patient_schema.load(json_data))
        except ValidationError as err:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': err.messages
            }), 400
        
        # Update patient in database
        # Update patient in database
        if db_service.update_patient(patient_id, validated_data):
            # Retrieve updated patient
            updated_patient = db_service.get_patient(patient_id)
            if not updated_patient:
                return jsonify({
                    'success': False,
                    'error': 'Failed to retrieve updated patient'
                }), 500
            return jsonify({
                'success': True,
                'data': updated_patient.to_dict(),
                'message': 'Patient updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update patient'
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update patient',
            'message': str(e)
        }), 500

@patients_bp.route('/search', methods=['GET'])
def search_patients():
    """
    Search patients by name or other criteria.
    """
    try:
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        
        if not first_name or not last_name:
            return jsonify({
                'success': False,
                'error': 'Both first_name and last_name are required for search'
            }), 400
        
        # Search for patient by name
        patient = db_service.find_patient_by_name(first_name, last_name)
        
        if patient:
            return jsonify({
                'success': True,
                'data': patient.to_dict(),
                'message': 'Patient found'
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No patient found with given name'
            }), 200
            
    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to search patients',
            'message': str(e)
        }), 500