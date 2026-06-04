"""
VPN Server Model - VPN Server Management
Manages VPN servers (OpenVPN, WireGuard, etc)
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from app import db
import enum

class VPNServerTypeEnum(enum.Enum):
    """
    VPN server type enumeration.
    
    - openvpn: OpenVPN server
    - wireguard: WireGuard server
    - pptp: PPTP server
    - l2tp: L2TP/IPSec server
    - sstp: SSTP server
    """
    openvpn = 'openvpn'
    wireguard = 'wireguard'
    pptp = 'pptp'
    l2tp = 'l2tp'
    sstp = 'sstp'

class VPNServer(db.Model):
    """
    VPN server model for VPN infrastructure management.
    
    Represents VPN servers with connection details and
    configuration parameters.
    
    Attributes:
        id: Unique server identifier
        tenant_id: Tenant this server belongs to
        name: Server name
        server_type: Type of VPN server
        hostname: Server hostname or IP
        port: VPN port
        protocol: Protocol (TCP/UDP for OpenVPN)
        certificate: Server certificate path
        private_key: Private key path
        is_active: Whether server is active
        max_users: Maximum concurrent users
        created_date: When server was added
        updated_date: When server was last updated
    """
    __tablename__ = 'vpn_servers'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Server Information
    name = Column(String(100), nullable=False, index=True)
    server_type = Column(Enum(VPNServerTypeEnum), nullable=False, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=True)  # TCP, UDP
    
    # Certificates
    certificate = Column(String(500), nullable=True)  # Path or content
    private_key = Column(String(500), nullable=True)  # Path or content
    
    # Configuration
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    max_users = Column(BigInteger, nullable=False, default=100)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    profiles = db.relationship('VPNProfile', backref='server', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<VPNServer(id={self.id}, name='{self.name}', type={self.server_type.value})>"
    
    def to_dict(self):
        """Convert VPN server to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'server_type': self.server_type.value,
            'hostname': self.hostname,
            'port': self.port,
            'protocol': self.protocol,
            'is_active': self.is_active,
            'max_users': self.max_users,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
