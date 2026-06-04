"""
Service Package Model - ISP Service Offerings
Defines service packages available to customers
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from app import db
import enum

class ServicePackageStatusEnum(enum.Enum):
    """
    Service package status enumeration.
    
    - active: Package is available for purchase
    - inactive: Package is inactive
    - discontinued: Package is discontinued
    """
    active = 'active'
    inactive = 'inactive'
    discontinued = 'discontinued'

class ServicePackage(db.Model):
    """
    Service package model representing ISP service offerings.
    
    Each package defines bandwidth, price, and service terms.
    Customers purchase packages which determine their service level.
    
    Attributes:
        id: Unique package identifier
        tenant_id: Tenant this package belongs to
        name: Package name
        description: Package description
        bandwidth_up: Upload bandwidth in Mbps
        bandwidth_down: Download bandwidth in Mbps
        price: Monthly price
        setup_fee: One-time setup fee
        contract_period: Contract period in months
        status: Package status
        is_active: Whether package is active
        created_date: When package was created
        updated_date: When package was last updated
    """
    __tablename__ = 'service_packages'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Package Information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Service Specifications
    bandwidth_up = Column(BigInteger, nullable=False)  # Mbps
    bandwidth_down = Column(BigInteger, nullable=False)  # Mbps
    
    # Pricing
    price = Column(Numeric(15, 2), nullable=False)  # Monthly price
    setup_fee = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Contract
    contract_period = Column(BigInteger, nullable=False, default=12)  # Months
    
    # Status
    status = Column(Enum(ServicePackageStatusEnum), nullable=False, default=ServicePackageStatusEnum.active, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    customers = db.relationship('Customer', backref='package', lazy=True)
    
    def __repr__(self):
        return f"<ServicePackage(id={self.id}, name='{self.name}', bandwidth={self.bandwidth_down}Mbps)>"
    
    def to_dict(self):
        """Convert service package to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'bandwidth_up': self.bandwidth_up,
            'bandwidth_down': self.bandwidth_down,
            'price': float(self.price),
            'setup_fee': float(self.setup_fee),
            'contract_period': self.contract_period,
            'status': self.status.value,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
