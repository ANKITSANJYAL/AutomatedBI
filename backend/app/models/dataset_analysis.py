"""
Dataset Analysis Model
"""

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, Integer, Float, BigInteger, DateTime, Text, Enum
from app import db
import uuid
from datetime import datetime
import enum


class ProcessingStatus(enum.Enum):
    """Enum for processing status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DatasetAnalysis(db.Model):
    """Model for storing dataset analysis results"""
    
    __tablename__ = 'dataset_analysis'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    upload_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Processing status
    status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Data analysis results
    domain_classification = Column(String(100))
    confidence_score = Column(Float)
    row_count = Column(Integer)
    column_count = Column(Integer)
    
    # Store analysis metadata as JSONB
    data_quality_report = Column(JSONB)
    column_analysis = Column(JSONB)
    domain_insights = Column(JSONB)
    recommended_kpis = Column(JSONB)
    recommended_charts = Column(JSONB)
    dashboard_structure = Column(JSONB)
    
    def __repr__(self):
        return f'<DatasetAnalysis {self.original_filename}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'upload_timestamp': self.upload_timestamp.isoformat() if self.upload_timestamp else None,
            'status': self.status.value if self.status else None,
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processing_completed_at': self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            'error_message': self.error_message,
            'domain_classification': self.domain_classification,
            'confidence_score': self.confidence_score,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'data_quality_report': self.data_quality_report,
            'column_analysis': self.column_analysis,
            'domain_insights': self.domain_insights,
            'recommended_kpis': self.recommended_kpis,
            'recommended_charts': self.recommended_charts,
            'dashboard_structure': self.dashboard_structure
        }
