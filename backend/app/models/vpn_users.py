"""
VPN User Model - VPN User Accounts
Manages user accounts for VPN services
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class VPNUser(db.Model):
    """
    VPN user model for VPN user account management.
    
    Represents user accounts for accessing VPN services
    with associated credentials and status tracking.
    
    Attributes:
        id: Unique VPN user identifier
        tenant_id: Tenant this user belongs to
        customer_id: Associated customer
        profile_id: Associated VPN profile
        username: VPN username
        password: VPN password (hashed)
        is_active: Whether account is active
        enable_date: When account was enabled
        disable_date: When account was disabled
        notes: Administrative notes
        created_date: When user was created
        updated_date: When user was last updated
    """
    __tablename__ = 'vpn_users'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey('customers.id'), nullable=False, index=True)
    profile_id = Column(BigInteger, ForeignKey('vpn_profiles.id'), nullable=False, index=True)
    
    # User Information
    username = Column(String(100), nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Hashed password
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    enable_date = Column(DateTime, nullable=True)
    disable_date = Column(DateTime, nullable=True)
    
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
    customer = db.relationship('Customer', backref='vpn_user_records')
    profile = db.relationship('VPNProfile', backref='user_records')
    sessions = db.relationship('VPNSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<VPNUser(id={self.id}, username='{self.username}')>"
    
    def to_dict(self):
        """Convert VPN user to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'profile_id': self.profile_id,
            'username': self.username,
            'is_active': self.is_active,
            'enable_date': self.enable_date.isoformat() if self.enable_date else None,
            'disable_date': self.disable_date.isoformat() if self.disable_date else None,
            'notes': self.notes,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
