"""
Tenant Model - Multi-tenant organization support
Each tenant represents an ISP organization with isolated data
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger
from app import db

class Tenant(db.Model):
    """
    Tenant model representing an ISP organization.
    
    A tenant is the top-level organization unit. All data is scoped to a tenant.
    No tenant may access another tenant's data.
    
    Attributes:
        id: Unique tenant identifier
        name: Human-readable tenant name
        code: Unique tenant code (lowercase, no spaces)
        description: Tenant description
        is_active: Whether the tenant is active
        max_users: Maximum number of users allowed
        max_customers: Maximum number of customers allowed
        created_date: When the tenant was created
        updated_date: When the tenant was last updated
    """
    __tablename__ = 'tenants'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Tenant Information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Limits
    max_users = Column(BigInteger, nullable=False, default=50)
    max_customers = Column(BigInteger, nullable=False, default=5000)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy=True, cascade='all, delete-orphan')
    customers = db.relationship('Customer', backref='tenant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self):
        """Convert tenant to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'is_active': self.is_active,
            'max_users': self.max_users,
            'max_customers': self.max_customers,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
