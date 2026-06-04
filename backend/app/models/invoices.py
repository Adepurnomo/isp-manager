"""
Invoice Model - Billing and Invoice Management
Manages customer invoices with multiple states and payment tracking
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, Date, BigInteger, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from app import db
import enum

class InvoiceStatusEnum(enum.Enum):
    """
    Invoice status enumeration.
    
    - draft: Invoice is draft and not sent
    - unpaid: Invoice sent but not paid
    - paid: Invoice has been paid
    - overdue: Invoice is past due date
    - cancelled: Invoice has been cancelled
    """
    draft = 'draft'
    unpaid = 'unpaid'
    paid = 'paid'
    overdue = 'overdue'
    cancelled = 'cancelled'

class Invoice(db.Model):
    """
    Invoice model representing billing documents.
    
    Invoices are generated for customers and track payment status.
    Multiple payment states are supported with due date tracking.
    
    Attributes:
        id: Unique invoice identifier
        tenant_id: Tenant this invoice belongs to
        customer_id: Customer being invoiced
        invoice_number: Unique invoice number per tenant
        description: Invoice description/items
        amount: Total invoice amount
        tax_amount: Tax amount
        total_amount: Total with tax
        status: Current invoice status
        issued_date: When invoice was issued
        due_date: When payment is due
        paid_date: When invoice was paid
        notes: Payment notes
        created_date: When invoice was created
        updated_date: When invoice was last updated
    """
    __tablename__ = 'invoices'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey('customers.id'), nullable=False, index=True)
    
    # Invoice Information
    invoice_number = Column(String(50), nullable=False, index=True)
    __table_args__ = (
        db.Index('idx_invoice_number_tenant', 'invoice_number', 'tenant_id', unique=True),
    )
    
    description = Column(Text, nullable=True)
    
    # Amounts
    amount = Column(Numeric(15, 2), nullable=False)  # Base amount
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)  # Tax
    total_amount = Column(Numeric(15, 2), nullable=False)  # Total with tax
    
    # Status
    status = Column(Enum(InvoiceStatusEnum), nullable=False, default=InvoiceStatusEnum.draft, index=True)
    
    # Dates
    issued_date = Column(Date, nullable=False, default=datetime.utcnow)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    customer = db.relationship('Customer', backref='invoices')
    payments = db.relationship('Payment', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status={self.status.value})>"
    
    def to_dict(self):
        """Convert invoice to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_id': self.customer_id,
            'invoice_number': self.invoice_number,
            'description': self.description,
            'amount': float(self.amount),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'status': self.status.value,
            'issued_date': self.issued_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'notes': self.notes,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
