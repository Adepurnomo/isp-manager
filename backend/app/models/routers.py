"""
Router Model - Network Router Management
Manages Mikrotik and other network routers
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app import db

class Router(db.Model):
    """
    Router model for managing network routers.
    
    Primarily for Mikrotik RouterOS devices with API integration.
    Stores connection details and device information.
    
    Attributes:
        id: Unique router identifier
        tenant_id: Tenant this router belongs to
        name: Router name
        hostname: Router hostname or IP address
        api_port: RouterOS API port
        api_username: API username
        api_password: API password (encrypted)
        interface_name: Primary interface name
        is_active: Whether router is active
        last_sync: Last synchronization timestamp
        notes: Administrative notes
        created_date: When router was added
        updated_date: When router was last updated
    """
    __tablename__ = 'routers'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Router Information
    name = Column(String(100), nullable=False, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    api_port = Column(Integer, nullable=False, default=8728)
    
    # API Credentials (should be encrypted in production)
    api_username = Column(String(100), nullable=False)
    api_password = Column(String(255), nullable=False)
    
    # Configuration
    interface_name = Column(String(100), nullable=False)  # e.g., 'ether1'
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_sync = Column(DateTime, nullable=True)
    
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
    radius_users = db.relationship('RadiusUser', backref='router', lazy=True)
    
    def __repr__(self):
        return f"<Router(id={self.id}, name='{self.name}', hostname='{self.hostname}')>"
    
    def to_dict(self, include_credentials=False):
        """Convert router to dictionary representation."""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'hostname': self.hostname,
            'api_port': self.api_port,
            'interface_name': self.interface_name,
            'is_active': self.is_active,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'notes': self.notes,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
        if include_credentials:
            data['api_username'] = self.api_username
        return data
