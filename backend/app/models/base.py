"""
Base model for all database entities.
Provides common fields and methods for all models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from app import db

Base = declarative_base()

class BaseModel(db.Model):
    """
    Base model class that all database models inherit from.
    Provides automatic timestamps and soft delete functionality.
    
    All tables MUST include:
    - id (primary key)
    - tenant_id (for multi-tenant isolation)
    - created_date (when record was created)
    - updated_date (when record was last updated)
    - created_by (user who created the record)
    - updated_by (user who last updated the record)
    - is_deleted (soft delete flag)
    """
    __abstract__ = True
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Multi-tenant field
    tenant_id = Column(BigInteger, nullable=False, index=True)
    
    # Timestamp fields
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit fields
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    
    # Soft delete flag
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, tenant_id={self.tenant_id})>"
    
    def to_dict(self, exclude_fields=None):
        """
        Convert model instance to dictionary.
        
        Args:
            exclude_fields: List of field names to exclude from output
            
        Returns:
            Dictionary representation of the model
        """
        if exclude_fields is None:
            exclude_fields = []
        
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Handle datetime serialization
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
        return result
