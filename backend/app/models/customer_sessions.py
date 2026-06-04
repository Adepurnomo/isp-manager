"""
Customer Session Model - Customer Connection Sessions
Tracks customer connection sessions (PPP, Hotspot, VPN)
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app import db

class CustomerSession(db.Model):
    """
    Customer session model for connection tracking.
    
    Records active and historical sessions for PPP, Hotspot,
    or other connection types. Allows bandwidth tracking and
    session history analysis.
    
    Attributes:
        id: Unique session identifier
        tenant_id: Tenant this session belongs to
        customer_id: Customer for this session
        session_id: Unique session ID from authentication system
        session_type: Type of session (ppp, hotspot, vpn, etc)
        ip_address: Assigned IP address
        login_time: When session started
        logout_time: When session ended
        bytes_uploaded: Bytes uploaded in session
        bytes_downloaded: Bytes downloaded in session
        duration: Session duration in seconds
        created_date: When session record was created
        updated_date: When session record was last updated
    """
    __tablename__ = 'customer_sessions'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey('customers.id'), nullable=False, index=True)
    
    # Session Information
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    session_type = Column(String(50), nullable=False, index=True)  # ppp, hotspot, vpn, etc
    ip_address = Column(String(45), nullable=True)  # Assigned IP
    
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
    
    # Relationships
    customer = db.relationship('Customer', backref='session_records')
    
    def __repr__(self):
        return f"<CustomerSession(id={self.id}, session_id='{self.session_id}', type='{self.session_type}')>"
    
    def to_dict(self):
        """Convert customer session to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'session_id': self.session_id,
            'session_type': self.session_type,
            'ip_address': self.ip_address,
            'login_time': self.login_time.isoformat(),
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'duration': self.duration,
            'bytes_uploaded': self.bytes_uploaded,
            'bytes_downloaded': self.bytes_downloaded,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
