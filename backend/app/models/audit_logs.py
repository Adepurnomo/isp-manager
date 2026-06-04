"""
Audit Log Model - Comprehensive Audit Trail
Tracks all system operations for compliance and debugging
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from app import db
import enum

class AuditActionEnum(enum.Enum):
    """
    Audit action enumeration.
    
    - login: User login
    - logout: User logout
    - create: Record created
    - update: Record updated
    - delete: Record deleted
    - suspend: Service suspended
    - activate: Service activated
    - payment_recorded: Payment recorded
    """
    login = 'login'
    logout = 'logout'
    create = 'create'
    update = 'update'
    delete = 'delete'
    suspend = 'suspend'
    activate = 'activate'
    payment_recorded = 'payment_recorded'

class AuditLog(db.Model):
    """
    Audit log model for comprehensive operation tracking.
    
    Records all significant system operations including logins,
    data modifications, and business actions for compliance
    and audit purposes.
    
    Attributes:
        id: Unique audit log identifier
        tenant_id: Tenant this action belongs to
        user_id: User who performed the action
        action: Type of action performed
        entity_type: Type of entity affected
        entity_id: ID of entity affected
        description: Action description
        changes: JSON object showing what changed
        ip_address: IP address of user
        user_agent: User agent string
        status: Action status (success/failure)
        created_date: When action was performed
    """
    __tablename__ = 'audit_logs'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True, index=True)
    
    # Action Information
    action = Column(Enum(AuditActionEnum), nullable=False, index=True)
    entity_type = Column(String(100), nullable=True, index=True)  # e.g., 'customer', 'invoice'
    entity_id = Column(BigInteger, nullable=True, index=True)
    
    # Description and Changes
    description = Column(Text, nullable=False)
    changes = Column(JSON, nullable=True)  # Before/after values
    
    # Request Information
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default='success', index=True)  # success, failure
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action.value}, entity={self.entity_type})>"
    
    def to_dict(self):
        """Convert audit log to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'action': self.action.value,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'changes': self.changes,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status,
            'created_date': self.created_date.isoformat()
        }
