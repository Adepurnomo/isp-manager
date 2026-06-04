"""
Customer Model - ISP Customer Management
Manages customer profiles, service assignments, and account status
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Enum, Numeric, Date
from sqlalchemy.orm import relationship
from app import db
import enum

class CustomerStatusEnum(enum.Enum):
    """
    Customer account status enumeration.
    
    - active: Customer service is active
    - suspended: Customer service is suspended (overdue payment)
    - inactive: Customer is inactive but not deleted
    - trial: Customer is on trial period
    """
    active = 'active'
    suspended = 'suspended'
    inactive = 'inactive'
    trial = 'trial'

class Customer(db.Model):
    """
    Customer model representing ISP customers.
    
    Each customer is associated with a tenant and can have multiple services.
    Includes support for service suspension and account status tracking.
    
    Attributes:
        id: Unique customer identifier
        tenant_id: Tenant this customer belongs to
        customer_number: Unique customer number per tenant
        first_name: Customer's first name
        last_name: Customer's last name
        email: Customer email address
        phone: Customer phone number
        address: Customer address
        city: City
        province: Province/State
        postal_code: Postal code
        country: Country
        id_card: National ID card number
        status: Current account status
        service_package_id: Current service package
        installation_date: When service was installed
        suspension_date: When service was suspended (if applicable)
        notes: Internal notes about the customer
        created_date: When customer record was created
        updated_date: When customer record was last updated
    """
    __tablename__ = 'customers'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    service_package_id = Column(BigInteger, ForeignKey('service_packages.id'), nullable=True)
    
    # Customer Information
    customer_number = Column(String(50), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    
    # Address Information
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=False, default='Indonesia')
    
    # Identity
    id_card = Column(String(50), nullable=True, index=True)
    
    # Account Status
    status = Column(Enum(CustomerStatusEnum), nullable=False, default=CustomerStatusEnum.trial, index=True)
    installation_date = Column(Date, nullable=True)
    suspension_date = Column(DateTime, nullable=True)
    
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
    service_package = relationship('ServicePackage', backref='customers')
    invoices = relationship('Invoice', backref='customer', lazy=True, cascade='all, delete-orphan')
    radius_users = relationship('RadiusUser', backref='customer', lazy=True, cascade='all, delete-orphan')
    vpn_users = relationship('VPNUser', backref='customer', lazy=True, cascade='all, delete-orphan')
    sessions = relationship('CustomerSession', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Customer(id={self.id}, number='{self.customer_number}', name='{self.first_name} {self.last_name}')>"
    
    def to_dict(self):
        """Convert customer to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'customer_number': self.customer_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'province': self.province,
            'postal_code': self.postal_code,
            'country': self.country,
            'id_card': self.id_card,
            'status': self.status.value,
            'service_package_id': self.service_package_id,
            'installation_date': self.installation_date.isoformat() if self.installation_date else None,
            'suspension_date': self.suspension_date.isoformat() if self.suspension_date else None,
            'notes': self.notes,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
