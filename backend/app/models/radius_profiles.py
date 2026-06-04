"""
RADIUS Profile Model - RADIUS Server Configuration
Defines RADIUS server settings and authentication parameters
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app import db

class RadiusProfile(db.Model):
    """
    RADIUS profile model for FreeRADIUS configuration.
    
    Defines RADIUS server parameters and authentication settings
    for user authentication and accounting.
    
    Attributes:
        id: Unique profile identifier
        tenant_id: Tenant this profile belongs to
        name: Profile name
        description: Profile description
        radius_server: RADIUS server IP/hostname
        radius_port: RADIUS port (default 1812)
        radius_secret: RADIUS shared secret
        accounting_port: Accounting port (default 1813)
        timeout: Request timeout (seconds)
        retries: Number of retries
        is_active: Whether profile is active
        created_date: When profile was created
        updated_date: When profile was last updated
    """
    __tablename__ = 'radius_profiles'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Profile Information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # RADIUS Server Configuration
    radius_server = Column(String(255), nullable=False)  # IP or hostname
    radius_port = Column(Integer, nullable=False, default=1812)
    radius_secret = Column(String(255), nullable=False)  # Shared secret
    accounting_port = Column(Integer, nullable=False, default=1813)
    
    # Request Settings
    timeout = Column(Integer, nullable=False, default=5)  # Seconds
    retries = Column(Integer, nullable=False, default=3)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    radius_users = db.relationship('RadiusUser', backref='profile', lazy=True)
    
    def __repr__(self):
        return f"<RadiusProfile(id={self.id}, name='{self.name}', server='{self.radius_server}')>"
    
    def to_dict(self, include_secret=False):
        """Convert RADIUS profile to dictionary representation."""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'radius_server': self.radius_server,
            'radius_port': self.radius_port,
            'accounting_port': self.accounting_port,
            'timeout': self.timeout,
            'retries': self.retries,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
        if include_secret:
            data['radius_secret'] = self.radius_secret
        return data
