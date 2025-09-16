"""
Data Point Model
"""

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app import db
import uuid


class DataPoint(db.Model):
    """Model for storing individual data points from datasets"""
    
    __tablename__ = 'data_points'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to dataset analysis
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('dataset_analysis.id', ondelete='CASCADE'), nullable=False)
    
    # Row information
    row_index = Column(Integer, nullable=False)
    
    # Store row data as JSONB
    data = Column(JSONB, nullable=False)
    
    # Relationship to dataset analysis
    dataset = relationship("DatasetAnalysis", back_populates="data_points")
    
    def __repr__(self):
        return f'<DataPoint {self.dataset_id}[{self.row_index}]>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'dataset_id': str(self.dataset_id),
            'row_index': self.row_index,
            'data': self.data
        }
