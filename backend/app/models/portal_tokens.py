"""
Portal Token Model - Customer Portal Authentication
Manages authentication tokens for customer portal
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app import db
import secrets

class PortalToken(db.Model):
    """
    Portal token model for customer portal access.
    
    Manages secure tokens for customer portal authentication
    with expiration support.
    
    Attributes:
        id: Unique token identifier
        tenant_id: Tenant this token belongs to
        customer_id: Associated customer
        token: Token value (hashed)
        expires_at: Token expiration timestamp
        is_revoked: Whether token is revoked
        last_used: When token was last used
        created_date: When token was created
        updated_date: When token was last updated
    """
    __tablename__ = 'portal_tokens'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey('customers.id'), nullable=False, index=True)
    
    # Token Information
    token = Column(String(255), nullable=False, unique=True, index=True)
    
    # Status
    expires_at = Column(DateTime, nullable=False, index=True)
    is_revoked = Column(Boolean, nullable=False, default=False, index=True)
    last_used = Column(DateTime, nullable=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='portal_tokens')
    
    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    def is_valid(self):
        """Check if token is valid (not expired, not revoked)."""
        return not self.is_revoked and datetime.utcnow() < self.expires_at
    
    def __repr__(self):
        return f"<PortalToken(id={self.id}, customer_id={self.customer_id})>"
    
    def to_dict(self):
        """Convert portal token to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'expires_at': self.expires_at.isoformat(),
            'is_revoked': self.is_revoked,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
