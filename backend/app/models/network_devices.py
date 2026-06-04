"""
Network Device Model - Network Device Monitoring
Tracks network devices and their monitoring status
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app import db
import enum

class NetworkDeviceTypeEnum(enum.Enum):
    """
    Network device type enumeration.
    
    - router: Network router
    - switch: Network switch
    - access_point: Wireless access point
    - gateway: Gateway device
    - firewall: Firewall appliance
    - other: Other device type
    """
    router = 'router'
    switch = 'switch'
    access_point = 'access_point'
    gateway = 'gateway'
    firewall = 'firewall'
    other = 'other'

class NetworkDeviceStatusEnum(enum.Enum):
    """
    Network device status enumeration.
    
    - online: Device is online
    - offline: Device is offline
    - error: Device has error
    - maintenance: Device is under maintenance
    """
    online = 'online'
    offline = 'offline'
    error = 'error'
    maintenance = 'maintenance'

class NetworkDevice(db.Model):
    """
    Network device model for monitoring infrastructure.
    
    Represents physical or virtual network devices that need monitoring.
    Tracks device type, status, and operational metrics.
    
    Attributes:
        id: Unique device identifier
        tenant_id: Tenant this device belongs to
        name: Device name
        device_type: Type of device
        ip_address: Device IP address
        hostname: Device hostname
        status: Current device status
        snmp_enabled: Whether SNMP monitoring is enabled
        snmp_community: SNMP community string
        last_check: Last monitoring check timestamp
        notes: Administrative notes
        created_date: When device was added
        updated_date: When device was last updated
    """
    __tablename__ = 'network_devices'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Device Information
    name = Column(String(100), nullable=False, index=True)
    device_type = Column(Enum(NetworkDeviceTypeEnum), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv4 or IPv6
    hostname = Column(String(255), nullable=True)
    
    # Status
    status = Column(Enum(NetworkDeviceStatusEnum), nullable=False, default=NetworkDeviceStatusEnum.offline, index=True)
    
    # Monitoring Configuration
    snmp_enabled = Column(Boolean, nullable=False, default=True)
    snmp_community = Column(String(100), nullable=True)
    
    # Monitoring
    last_check = Column(DateTime, nullable=True)
    
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
    metrics = db.relationship('DeviceMetrics', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<NetworkDevice(id={self.id}, name='{self.name}', ip='{self.ip_address}')>"
    
    def to_dict(self):
        """Convert network device to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'device_type': self.device_type.value,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'status': self.status.value,
            'snmp_enabled': self.snmp_enabled,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'notes': self.notes,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
