"""
RADIUS User Model - RADIUS Authentication Users
Manages user accounts for RADIUS-based authentication
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class RadiusUser(db.Model):
    """
    RADIUS user model for FreeRADIUS authentication.
    
    Represents user accounts for PPP, Hotspot, or other
    RADIUS-based authentication mechanisms.
    
    Attributes:
        id: Unique RADIUS user identifier
        tenant_id: Tenant this user belongs to
        customer_id: Associated customer
        router_id: Associated router
        profile_id: Associated RADIUS profile
        username: RADIUS username
        password: RADIUS password (hashed)
        enable_date: When user was enabled
        disable_date: When user was disabled
        is_active: Whether user is active
        notes: Administrative notes
        created_date: When user was created
        updated_date: When user was last updated
    """
    __tablename__ = 'radius_users'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey('customers.id'), nullable=False, index=True)
    router_id = Column(BigInteger, ForeignKey('routers.id'), nullable=True)
    profile_id = Column(BigInteger, ForeignKey('radius_profiles.id'), nullable=False)
    
    # User Information
    username = Column(String(100), nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Hashed password
    
    # Status Tracking
    enable_date = Column(DateTime, nullable=True)
    disable_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Administrative
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='radius_user_records')
    router = db.relationship('Router', backref='radius_user_records')
    profile = db.relationship('RadiusProfile', backref='user_records')
    
    def __repr__(self):
        return f"<RadiusUser(id={self.id}, username='{self.username}')>"
    
    def to_dict(self):
        """Convert RADIUS user to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'router_id': self.router_id,
            'profile_id': self.profile_id,
            'username': self.username,
            'is_active': self.is_active,
            'enable_date': self.enable_date.isoformat() if self.enable_date else None,
            'disable_date': self.disable_date.isoformat() if self.disable_date else None,
            'notes': self.notes,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
