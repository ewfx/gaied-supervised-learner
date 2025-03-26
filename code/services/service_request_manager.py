from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from models.service_request import ServiceRequest
from models.db_models import ServiceRequestDB
from services.duplicate_detector import DuplicateDetectorService
from config.database import SessionLocal

class ServiceRequestManager:
    def __init__(self):
        self.duplicate_detector = DuplicateDetectorService()
        
        # Team assignment mapping based on request types
        self.team_mapping = {
            "Adjustment": "ADJUSTMENT_TEAM",
            "AU Transfer": "TRANSFER_TEAM",
            "Closing Notice": "CLOSING_TEAM",
            "Commitment Change": "COMMITMENT_TEAM",
            "Fee Payment": "FEE_TEAM",
            "Money Movement - Inbound": "INBOUND_TEAM",
            "Money Movement - Outbound": "OUTBOUND_TEAM"
        }

    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()

    def create_service_request(
        self,
        request_type: str,
        sub_request_type: Optional[str],
        deal_id: str,
        extracted_fields: Dict[str, Any],
        confidence_score: float,
        email_content: str
    ) -> Optional[ServiceRequest]:
        """
        Create a new service request if it's not a duplicate
        Returns None if it's a duplicate, otherwise returns the created ServiceRequest
        """
        # Check for duplicates using the email content
        is_duplicate, duplicate_confidence = self.duplicate_detector.check_duplicate(email_content)
        
        if is_duplicate:
            return None
            
        # Create new service request
        service_request = ServiceRequest(
            request_type=request_type,
            sub_request_type=sub_request_type,
            deal_id=deal_id,
            extracted_fields=extracted_fields,
            confidence_score=confidence_score
        )
        
        # Assign team based on request type
        team = self.team_mapping.get(request_type, "DEFAULT_TEAM")
        service_request.assign_team(team)
        
        # Store in database
        db = self._get_db()
        try:
            db_request = ServiceRequestDB.from_dict(service_request.to_dict())
            db.add(db_request)
            db.commit()
            db.refresh(db_request)
            return ServiceRequest.from_dict(db_request.to_dict())
        finally:
            db.close()

    def get_service_request(self, request_id: str) -> Optional[ServiceRequest]:
        """Get a service request by ID"""
        db = self._get_db()
        try:
            db_request = db.query(ServiceRequestDB).filter(ServiceRequestDB.id == request_id).first()
            if not db_request:
                return None
            return ServiceRequest.from_dict(db_request.to_dict())
        finally:
            db.close()

    def get_service_requests_by_team(self, team: str) -> List[ServiceRequest]:
        """Get all service requests assigned to a specific team"""
        db = self._get_db()
        try:
            db_requests = db.query(ServiceRequestDB).filter(ServiceRequestDB.team_assigned == team).all()
            return [ServiceRequest.from_dict(request.to_dict()) for request in db_requests]
        finally:
            db.close()

    def update_service_request_status(self, request_id: str, new_status: str) -> Optional[ServiceRequest]:
        """Update the status of a service request"""
        db = self._get_db()
        try:
            db_request = db.query(ServiceRequestDB).filter(ServiceRequestDB.id == request_id).first()
            if not db_request:
                return None
            db_request.status = new_status
            db.commit()
            db.refresh(db_request)
            return ServiceRequest.from_dict(db_request.to_dict())
        finally:
            db.close() 