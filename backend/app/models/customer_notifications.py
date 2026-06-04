"""
Customer Notification Model - Customer Portal Notifications
Manages notifications for customer portal
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app import db
import enum

class CustomerNotificationTypeEnum(enum.Enum):
    """
    Customer notification type enumeration.
    
    - invoice: Invoice notification
    - payment: Payment notification
    - suspension: Suspension notice
    - promotion: Promotional message
    - system: System message
    """
    invoice = 'invoice'
    payment = 'payment'
    suspension = 'suspension'
    promotion = 'promotion'
    system = 'system'

class CustomerNotification(db.Model):
    """
    Customer notification model for portal notifications.
    
    Tracks notifications sent to customers through the
    customer portal and via email/WhatsApp.
    
    Attributes:
        id: Unique notification identifier
        tenant_id: Tenant this notification belongs to
        customer_id: Associated customer
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        is_read: Whether customer has read the notification
        read_date: When notification was read
        sent_via_email: Whether sent via email
        sent_via_whatsapp: Whether sent via WhatsApp
        created_date: When notification was created
        updated_date: When notification was last updated
    """
    __tablename__ = 'customer_notifications'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey('customers.id'), nullable=False, index=True)
    
    # Notification Content
    notification_type = Column(Enum(CustomerNotificationTypeEnum), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_date = Column(DateTime, nullable=True)
    
    # Delivery Tracking
    sent_via_email = Column(Boolean, nullable=False, default=False)
    sent_via_whatsapp = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='customer_notifications')
    
    def __repr__(self):
        return f"<CustomerNotification(id={self.id}, customer_id={self.customer_id})>"
    
    def to_dict(self):
        """Convert customer notification to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'notification_type': self.notification_type.value,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'read_date': self.read_date.isoformat() if self.read_date else None,
            'sent_via_email': self.sent_via_email,
            'sent_via_whatsapp': self.sent_via_whatsapp,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
