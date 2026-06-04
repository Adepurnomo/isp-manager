"""
VPN Session Model - VPN User Sessions
Tracks VPN connection sessions
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class VPNSession(db.Model):
    """
    VPN session model for VPN connection tracking.
    
    Records active and historical VPN sessions including
    connection times and traffic data.
    
    Attributes:
        id: Unique session identifier
        tenant_id: Tenant this session belongs to
        vpn_user_id: Associated VPN user
        session_id: Unique session identifier
        remote_ip: Client IP address
        vpn_ip: Assigned VPN IP address
        login_time: When session started
        logout_time: When session ended
        bytes_uploaded: Bytes uploaded
        bytes_downloaded: Bytes downloaded
        duration: Session duration in seconds
        created_date: When session record was created
        updated_date: When session record was last updated
    """
    __tablename__ = 'vpn_sessions'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    vpn_user_id = Column(BigInteger, ForeignKey('vpn_users.id'), nullable=False, index=True)
    
    # Session Information
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    remote_ip = Column(String(45), nullable=True)  # Client IP
    vpn_ip = Column(String(45), nullable=False)  # Assigned VPN IP
    
    # Session Duration
    login_time = Column(DateTime, nullable=False, index=True)
    logout_time = Column(DateTime, nullable=True)
    duration = Column(BigInteger, nullable=True)  # Seconds
    
    # Traffic
    bytes_uploaded = Column(BigInteger, nullable=False, default=0)
    bytes_downloaded = Column(BigInteger, nullable=False, default=0)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self):
        return f"<VPNSession(id={self.id}, session_id='{self.session_id}')>"
    
    def to_dict(self):
        """Convert VPN session to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'vpn_user_id': self.vpn_user_id,
            'session_id': self.session_id,
            'remote_ip': self.remote_ip,
            'vpn_ip': self.vpn_ip,
            'login_time': self.login_time.isoformat(),
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'duration': self.duration,
            'bytes_uploaded': self.bytes_uploaded,
            'bytes_downloaded': self.bytes_downloaded,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
