"""
Bandwidth Profile Model - Network Bandwidth Configuration
Defines bandwidth allocation and QoS profiles
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app import db

class BandwidthProfile(db.Model):
    """
    Bandwidth profile model for QoS configuration.
    
    Defines bandwidth allocation rules for customers including
    upload/download speeds and burst capabilities.
    
    Attributes:
        id: Unique profile identifier
        tenant_id: Tenant this profile belongs to
        name: Profile name
        description: Profile description
        max_bandwidth_down: Maximum download bandwidth (Mbps)
        max_bandwidth_up: Maximum upload bandwidth (Mbps)
        burst_down: Burst download bandwidth (Mbps)
        burst_up: Burst upload bandwidth (Mbps)
        burst_time: Burst time duration (seconds)
        priority: Traffic priority (0-7)
        is_active: Whether profile is active
        created_date: When profile was created
        updated_date: When profile was last updated
    """
    __tablename__ = 'bandwidth_profiles'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Profile Information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Bandwidth Configuration
    max_bandwidth_down = Column(BigInteger, nullable=False)  # Mbps
    max_bandwidth_up = Column(BigInteger, nullable=False)  # Mbps
    burst_down = Column(BigInteger, nullable=False, default=0)  # Mbps
    burst_up = Column(BigInteger, nullable=False, default=0)  # Mbps
    burst_time = Column(BigInteger, nullable=False, default=0)  # Seconds
    
    # QoS Settings
    priority = Column(BigInteger, nullable=False, default=5)  # 0-7
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self):
        return f"<BandwidthProfile(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert bandwidth profile to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'max_bandwidth_down': self.max_bandwidth_down,
            'max_bandwidth_up': self.max_bandwidth_up,
            'burst_down': self.burst_down,
            'burst_up': self.burst_up,
            'burst_time': self.burst_time,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
