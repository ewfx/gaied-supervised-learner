from flask import Blueprint, request, jsonify
from services.email_classifier import EmailClassifierService
from services.service_request_manager import ServiceRequestManager

api_blueprint = Blueprint('api', __name__)
email_classifier = EmailClassifierService()
service_request_manager = ServiceRequestManager()

@api_blueprint.route('/process-email', methods=['POST'])
def process_email():
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Process the email classification
        result = email_classifier.process_email(file)
        
        if not result:
            return jsonify({'error': 'Failed to process email'}), 500
            
        return jsonify(result)
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/service-requests/<request_id>', methods=['GET'])
def get_service_request(request_id):
    try:
        service_request = service_request_manager.get_service_request(request_id)
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
        return jsonify(service_request.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/service-requests/team/<team>', methods=['GET'])
def get_team_service_requests(team):
    try:
        service_requests = service_request_manager.get_service_requests_by_team(team)
        return jsonify([request.to_dict() for request in service_requests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/service-requests/<request_id>/status', methods=['PUT'])
def update_service_request_status(request_id):
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
            
        service_request = service_request_manager.update_service_request_status(
            request_id, 
            data['status']
        )
        
        if not service_request:
            return jsonify({'error': 'Service request not found'}), 404
            
        return jsonify(service_request.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500 