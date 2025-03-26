from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class ServiceRequest:
    def __init__(
        self,
        request_type: str,
        sub_request_type: Optional[str],
        deal_id: str,
        extracted_fields: Dict[str, Any],
        confidence_score: float,
        team_assigned: Optional[str] = None,
        status: str = "NEW",
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = str(uuid.uuid4())
        self.request_type = request_type
        self.sub_request_type = sub_request_type
        self.deal_id = deal_id
        self.extracted_fields = extracted_fields
        self.confidence_score = confidence_score
        self.team_assigned = team_assigned
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def assign_team(self, team: str) -> None:
        """Assign a team to handle the service request"""
        self.team_assigned = team
        self.updated_at = datetime.utcnow()

    def update_status(self, new_status: str) -> None:
        """Update the status of the service request"""
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the service request to a dictionary"""
        return {
            "id": self.id,
            "request_type": self.request_type,
            "sub_request_type": self.sub_request_type,
            "deal_id": self.deal_id,
            "extracted_fields": self.extracted_fields,
            "confidence_score": self.confidence_score,
            "team_assigned": self.team_assigned,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceRequest':
        """Create a ServiceRequest instance from a dictionary"""
        # Handle datetime conversion safely
        created_at = None
        updated_at = None
        
        if "created_at" in data and data["created_at"]:
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                created_at = None
                
        if "updated_at" in data and data["updated_at"]:
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                updated_at = None

        return cls(
            request_type=data["request_type"],
            sub_request_type=data.get("sub_request_type"),
            deal_id=data["deal_id"],
            extracted_fields=data["extracted_fields"],
            confidence_score=data["confidence_score"],
            team_assigned=data.get("team_assigned"),
            status=data.get("status", "NEW"),
            created_at=created_at,
            updated_at=updated_at
        ) 