"""
Payment Models - Payment Processing and Tracking
Manages payment records, transactions, and gateway callbacks
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Numeric, Enum, JSON
from sqlalchemy.orm import relationship
from app import db
import enum

class PaymentMethodEnum(enum.Enum):
    """
    Payment method enumeration.
    
    - bank_transfer: Direct bank transfer
    - midtrans: Midtrans payment gateway
    - xendit: Xendit payment gateway
    - tripay: Tripay payment gateway
    - cash: Cash payment
    - check: Check payment
    """
    bank_transfer = 'bank_transfer'
    midtrans = 'midtrans'
    xendit = 'xendit'
    tripay = 'tripay'
    cash = 'cash'
    check = 'check'

class PaymentStatusEnum(enum.Enum):
    """
    Payment status enumeration.
    
    - pending: Payment is pending
    - processing: Payment is being processed
    - completed: Payment is completed
    - failed: Payment failed
    - refunded: Payment was refunded
    """
    pending = 'pending'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'
    refunded = 'refunded'

class Payment(db.Model):
    """
    Payment model for recording invoice payments.
    
    Tracks individual payments against invoices with
    full audit trail and status tracking.
    
    Attributes:
        id: Unique payment identifier
        tenant_id: Tenant this payment belongs to
        invoice_id: Invoice being paid
        payment_number: Unique payment reference number
        amount: Payment amount
        method: Payment method used
        status: Payment status
        reference_number: External reference (bank reference, etc)
        notes: Payment notes
        payment_date: When payment was received
        created_date: When payment record was created
        updated_date: When payment record was last updated
    """
    __tablename__ = 'payments'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    invoice_id = Column(BigInteger, ForeignKey('invoices.id'), nullable=False, index=True)
    
    # Payment Information
    payment_number = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment Details
    method = Column(Enum(PaymentMethodEnum), nullable=False, default=PaymentMethodEnum.bank_transfer, index=True)
    status = Column(Enum(PaymentStatusEnum), nullable=False, default=PaymentStatusEnum.pending, index=True)
    reference_number = Column(String(100), nullable=True, index=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='payment_records')
    transactions = db.relationship('PaymentTransaction', backref='payment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Payment(id={self.id}, number='{self.payment_number}', amount={self.amount})>"
    
    def to_dict(self):
        """Convert payment to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'invoice_id': self.invoice_id,
            'payment_number': self.payment_number,
            'amount': float(self.amount),
            'method': self.method.value,
            'status': self.status.value,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'payment_date': self.payment_date.isoformat(),
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }

class PaymentTransaction(db.Model):
    """
    Payment transaction model for gateway transactions.
    
    Records detailed transaction information from payment gateways
    including amounts, fees, and status tracking.
    
    Attributes:
        id: Unique transaction identifier
        tenant_id: Tenant this transaction belongs to
        payment_id: Associated payment
        gateway: Payment gateway (midtrans, xendit, tripay)
        transaction_id: Gateway transaction ID
        gateway_response: Full gateway response data
        status: Transaction status
        gross_amount: Gross transaction amount
        net_amount: Net amount after fees
        fee: Gateway fee
        created_date: When transaction was created
        updated_date: When transaction was last updated
    """
    __tablename__ = 'payment_transactions'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    payment_id = Column(BigInteger, ForeignKey('payments.id'), nullable=False, index=True)
    
    # Transaction Information
    gateway = Column(String(50), nullable=False, index=True)  # midtrans, xendit, tripay
    transaction_id = Column(String(100), nullable=False, index=True)
    
    # Amounts
    gross_amount = Column(Numeric(15, 2), nullable=False)
    net_amount = Column(Numeric(15, 2), nullable=False)
    fee = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Status
    status = Column(String(50), nullable=False, index=True)  # settle, pending, failed, etc
    
    # Gateway Response (JSON)
    gateway_response = Column(JSON, nullable=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, gateway='{self.gateway}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert payment transaction to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'payment_id': self.payment_id,
            'gateway': self.gateway,
            'transaction_id': self.transaction_id,
            'gross_amount': float(self.gross_amount),
            'net_amount': float(self.net_amount),
            'fee': float(self.fee),
            'status': self.status,
            'gateway_response': self.gateway_response,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }

class PaymentCallback(db.Model):
    """
    Payment callback model for webhook tracking.
    
    Records all webhook callbacks from payment gateways
    for audit and verification purposes.
    
    Attributes:
        id: Unique callback identifier
        tenant_id: Tenant this callback belongs to
        gateway: Payment gateway name
        webhook_id: Gateway webhook ID
        payload: Full webhook payload (JSON)
        signature: Webhook signature for verification
        is_verified: Whether signature was verified
        status: Processing status
        created_date: When callback was received
        updated_date: When callback was last processed
    """
    __tablename__ = 'payment_callbacks'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Callback Information
    gateway = Column(String(50), nullable=False, index=True)
    webhook_id = Column(String(100), nullable=False, index=True)
    
    # Payload and Signature
    payload = Column(JSON, nullable=False)  # Full webhook payload
    signature = Column(String(255), nullable=False)  # Webhook signature
    is_verified = Column(Boolean, nullable=False, default=False, index=True)
    
    # Status
    status = Column(String(50), nullable=False, default='pending', index=True)  # pending, processed, failed
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self):
        return f"<PaymentCallback(id={self.id}, gateway='{self.gateway}', verified={self.is_verified})>"
    
    def to_dict(self):
        """Convert payment callback to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'gateway': self.gateway,
            'webhook_id': self.webhook_id,
            'is_verified': self.is_verified,
            'status': self.status,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
