"""
User and Role Models - Authentication and Authorization
Manages system users, roles, and permissions
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import enum

class RoleEnum(enum.Enum):
    """
    Enumeration of available user roles.
    
    - super_admin: Full system access
    - tenant_admin: Tenant-level management
    - billing: Invoice and payment management
    - noc: Network operations center
    - customer_service: Customer support
    """
    super_admin = 'super_admin'
    tenant_admin = 'tenant_admin'
    billing = 'billing'
    noc = 'noc'
    customer_service = 'customer_service'

class User(db.Model):
    """
    User model representing system users.
    
    Users can have different roles and permissions within their tenant.
    Passwords are hashed using werkzeug security functions.
    
    Attributes:
        id: Unique user identifier
        tenant_id: Tenant this user belongs to
        email: Unique email address
        password_hash: Hashed password
        first_name: User's first name
        last_name: User's last name
        phone: User's phone number
        role: User's role (from RoleEnum)
        is_active: Whether the user account is active
        last_login: Timestamp of last login
        created_date: When the user was created
        updated_date: When the user was last updated
    """
    __tablename__ = 'users'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # User Information
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Authentication
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.customer_service, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_login = Column(DateTime, nullable=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def verify_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role.value})>"
    
    def to_dict(self, include_password=False):
        """Convert user to dictionary representation."""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role.value,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data

class Role(db.Model):
    """
    Role model for managing permissions.
    Currently uses RoleEnum for simplicity, but this model
    allows future expansion to granular permission management.
    
    Attributes:
        id: Unique role identifier
        name: Role name
        description: Role description
        permissions: JSON or relationship to permissions
    """
    __tablename__ = 'roles'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Role Information
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
