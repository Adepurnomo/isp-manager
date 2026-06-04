"""
RBAC (Role-Based Access Control) Service
Manages roles, permissions, and access control
"""

from app.models.users import User, RoleEnum

class RBACService:
    """
    Service for role-based access control.
    Manages permissions and role checks.
    """
    
    # Role to permissions mapping
    ROLE_PERMISSIONS = {
        'super_admin': [
            'users.create', 'users.read', 'users.update', 'users.delete',
            'customers.create', 'customers.read', 'customers.update', 'customers.delete',
            'invoices.create', 'invoices.read', 'invoices.update', 'invoices.delete',
            'payments.create', 'payments.read', 'payments.update', 'payments.delete',
            'routers.create', 'routers.read', 'routers.update', 'routers.delete',
            'radius.manage', 'vpn.manage',
            'reports.view', 'audit.view',
            'tenant.manage', 'settings.manage'
        ],
        'tenant_admin': [
            'users.create', 'users.read', 'users.update', 'users.delete',
            'customers.create', 'customers.read', 'customers.update', 'customers.delete',
            'invoices.create', 'invoices.read', 'invoices.update', 'invoices.delete',
            'payments.create', 'payments.read', 'payments.update', 'payments.delete',
            'routers.read', 'radius.manage', 'vpn.manage',
            'reports.view', 'audit.view', 'settings.manage'
        ],
        'billing': [
            'customers.read',
            'invoices.create', 'invoices.read', 'invoices.update',
            'payments.create', 'payments.read', 'payments.update',
            'reports.view'
        ],
        'noc': [
            'customers.read',
            'routers.read',
            'radius.manage', 'vpn.manage',
            'reports.view', 'audit.view'
        ],
        'customer_service': [
            'customers.read', 'customers.update',
            'invoices.read',
            'payments.read',
            'reports.view'
        ]
    }
    
    @staticmethod
    def has_permission(user, permission):
        """
        Check if user has specific permission.
        
        Args:
            user: User object
            permission: Permission string (e.g., 'customers.create')
            
        Returns:
            True if user has permission, False otherwise
        """
        role = user.role.value
        permissions = RBACService.ROLE_PERMISSIONS.get(role, [])
        return permission in permissions
    
    @staticmethod
    def has_any_permission(user, permissions):
        """
        Check if user has any of the specified permissions.
        
        Args:
            user: User object
            permissions: List of permission strings
            
        Returns:
            True if user has any permission, False otherwise
        """
        for permission in permissions:
            if RBACService.has_permission(user, permission):
                return True
        return False
    
    @staticmethod
    def has_all_permissions(user, permissions):
        """
        Check if user has all specified permissions.
        
        Args:
            user: User object
            permissions: List of permission strings
            
        Returns:
            True if user has all permissions, False otherwise
        """
        for permission in permissions:
            if not RBACService.has_permission(user, permission):
                return False
        return True
    
    @staticmethod
    def get_user_permissions(user):
        """
        Get all permissions for a user.
        
        Args:
            user: User object
            
        Returns:
            List of permission strings
        """
        role = user.role.value
        return RBACService.ROLE_PERMISSIONS.get(role, [])

def permission_required(permission):
    """
    Decorator to require specific permission for endpoint.
    
    Args:
        permission: Permission string (e.g., 'customers.create')
    """
    from functools import wraps
    from flask import jsonify
    from flask_jwt_extended import jwt_required, get_jwt_identity
    
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
            
            if not RBACService.has_permission(user, permission):
                return jsonify({
                    'status': 'error',
                    'message': 'Insufficient permissions',
                    'required_permission': permission
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator
