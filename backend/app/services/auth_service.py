"""
JWT Authentication Utilities
Handles JWT token generation, validation, and refresh logic
"""

from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from app import db
from app.models.users import User
from app.models.audit_logs import AuditLog, AuditActionEnum

class AuthService:
    """
    Service for authentication operations including login, logout, token refresh.
    Handles JWT creation and validation.
    """
    
    @staticmethod
    def generate_tokens(user_id, tenant_id):
        """
        Generate access and refresh JWT tokens for a user.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        identity = {
            'user_id': user_id,
            'tenant_id': tenant_id
        }
        
        access_token = create_access_token(
            identity=identity,
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = create_refresh_token(
            identity=identity,
            expires_delta=timedelta(days=30)
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User object if authenticated, None otherwise
        """
        user = User.query.filter_by(email=email, is_deleted=False).first()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not user.verify_password(password):
            return None
        
        return user
    
    @staticmethod
    def log_audit(user_id, tenant_id, action, entity_type=None, entity_id=None,
                  description='', ip_address=None, user_agent=None, status='success'):
        """
        Log an audit trail entry.
        
        Args:
            user_id: User who performed the action
            tenant_id: Tenant ID
            action: AuditActionEnum action
            entity_type: Type of entity affected
            entity_id: ID of entity affected
            description: Action description
            ip_address: User IP address
            user_agent: User agent string
            status: Action status (success/failure)
        """
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        db.session.add(audit_log)
        db.session.commit()

def token_required(f):
    """
    Decorator to require valid JWT token for endpoint.
    """
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        identity = get_jwt_identity()
        user_id = identity.get('user_id')
        tenant_id = identity.get('tenant_id')
        
        # Verify user still exists and is active
        user = User.query.filter_by(id=user_id, tenant_id=tenant_id, is_deleted=False).first()
        if not user or not user.is_active:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(required_roles):
    """
    Decorator to require specific roles for endpoint.
    
    Args:
        required_roles: List of allowed roles or single role string
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated(*args, **kwargs):
            identity = get_jwt_identity()
            user_id = identity.get('user_id')
            tenant_id = identity.get('tenant_id')
            
            user = User.query.filter_by(
                id=user_id,
                tenant_id=tenant_id,
                is_deleted=False
            ).first()
            
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': 'User not found'
                }), 401
            
            if user.role.value not in required_roles:
                return jsonify({
                    'status': 'error',
                    'message': 'Insufficient permissions'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

def tenant_isolated(f):
    """
    Decorator to ensure tenant isolation in queries.
    Automatically filters by authenticated user's tenant.
    """
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        identity = get_jwt_identity()
        kwargs['tenant_id'] = identity.get('tenant_id')
        return f(*args, **kwargs)
    
    return decorated
