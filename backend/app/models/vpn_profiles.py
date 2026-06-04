"""
VPN Profile Model - VPN Profile Configuration
Defines VPN profiles for customers
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app import db

class VPNProfile(db.Model):
    """
    VPN profile model for VPN configuration.
    
    Represents VPN profiles with specific settings and
    options for customers.
    
    Attributes:
        id: Unique profile identifier
        tenant_id: Tenant this profile belongs to
        server_id: Associated VPN server
        name: Profile name
        description: Profile description
        configuration: VPN configuration (JSON)
        is_active: Whether profile is active
        created_date: When profile was created
        updated_date: When profile was last updated
    """
    __tablename__ = 'vpn_profiles'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    server_id = Column(BigInteger, ForeignKey('vpn_servers.id'), nullable=False, index=True)
    
    # Profile Information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuration
    configuration = Column(JSON, nullable=True)  # VPN-specific config
    
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
    users = db.relationship('VPNUser', backref='profile', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<VPNProfile(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert VPN profile to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'server_id': self.server_id,
            'name': self.name,
            'description': self.description,
            'configuration': self.configuration,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
