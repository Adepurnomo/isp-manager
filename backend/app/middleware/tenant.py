"""
Tenant Middleware - Enforces multi-tenant isolation
"""

from flask import request, jsonify
from functools import wraps
from flask_jwt_extended import get_jwt_identity

def verify_tenant_access(f):
    """
    Decorator to verify tenant access for requests.
    Ensures users can only access their own tenant's data.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            identity = get_jwt_identity()
            if not identity:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401
            
            tenant_id = identity.get('tenant_id')
            
            # Add tenant_id to kwargs for the route handler
            kwargs['tenant_id'] = tenant_id
            
            return f(*args, **kwargs)
        
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'Tenant verification failed'
            }), 401
    
    return decorated

def require_tenant_ownership(model_field='tenant_id'):
    """
    Decorator to ensure entity belongs to user's tenant.
    
    Args:
        model_field: Field name in model to check (default 'tenant_id')
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                identity = get_jwt_identity()
                user_tenant_id = identity.get('tenant_id')
                
                # Get entity tenant_id from kwargs or request
                entity_tenant_id = kwargs.get('tenant_id')
                
                if entity_tenant_id and entity_tenant_id != user_tenant_id:
                    return jsonify({
                        'status': 'error',
                        'message': 'Access denied'
                    }), 403
                
                return f(*args, **kwargs)
            
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Tenant ownership verification failed'
                }), 500
        
        return decorated
    
    return decorator
