from sqlalchemy import Column, String, Float, JSON, DateTime
from sqlalchemy.sql import func
from config.database import Base
import uuid

class ServiceRequestDB(Base):
    __tablename__ = "service_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_type = Column(String, nullable=False)
    sub_request_type = Column(String, nullable=True)
    deal_id = Column(String, nullable=False)
    extracted_fields = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)
    team_assigned = Column(String, nullable=True)
    status = Column(String, nullable=False, default="NEW")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
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
    def from_dict(cls, data):
        return cls(
            request_type=data["request_type"],
            sub_request_type=data.get("sub_request_type"),
            deal_id=data["deal_id"],
            extracted_fields=data["extracted_fields"],
            confidence_score=data["confidence_score"],
            team_assigned=data.get("team_assigned"),
            status=data.get("status", "NEW")
        ) 