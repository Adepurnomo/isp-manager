"""
Notification Model - System Notifications
Manages system notifications for users
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app import db
import enum

class NotificationTypeEnum(enum.Enum):
    """
    Notification type enumeration.
    
    - invoice_created: Invoice created notification
    - payment_reminder: Payment reminder
    - suspension_notice: Service suspension notice
    - payment_success: Payment received confirmation
    - reactivation: Service reactivated
    - system_alert: System alert
    """
    invoice_created = 'invoice_created'
    payment_reminder = 'payment_reminder'
    suspension_notice = 'suspension_notice'
    payment_success = 'payment_success'
    reactivation = 'reactivation'
    system_alert = 'system_alert'

class NotificationStatusEnum(enum.Enum):
    """
    Notification status enumeration.
    """
    pending = 'pending'
    sent = 'sent'
    failed = 'failed'
    read = 'read'

class Notification(db.Model):
    """
    Notification model for system notifications.
    
    Tracks notifications sent to users for various events
    including invoices, payments, and system alerts.
    
    Attributes:
        id: Unique notification identifier
        tenant_id: Tenant this notification belongs to
        user_id: Recipient user
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        data: Additional data (JSON)
        status: Notification status
        read_date: When notification was read
        sent_date: When notification was sent
        created_date: When notification was created
        updated_date: When notification was last updated
    """
    __tablename__ = 'notifications'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, index=True)
    
    # Notification Content
    notification_type = Column(Enum(NotificationTypeEnum), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    status = Column(Enum(NotificationStatusEnum), nullable=False, default=NotificationStatusEnum.pending, index=True)
    read_date = Column(DateTime, nullable=True)
    sent_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type.value})>"
    
    def to_dict(self):
        """Convert notification to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'notification_type': self.notification_type.value,
            'title': self.title,
            'message': self.message,
            'status': self.status.value,
            'read_date': self.read_date.isoformat() if self.read_date else None,
            'sent_date': self.sent_date.isoformat() if self.sent_date else None,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
