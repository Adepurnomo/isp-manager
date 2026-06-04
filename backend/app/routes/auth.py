"""
Authentication Routes - Login, Logout, Token Refresh
Provides REST API endpoints for user authentication
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.users import User
from app.services.auth_service import AuthService, token_required
from app.models.audit_logs import AuditLog, AuditActionEnum
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint - Authenticate user with email and password.
    Returns JWT access and refresh tokens.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "tenant_code": "tenant_code"  # Optional
    }
    
    Returns:
    {
        "status": "success",
        "data": {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {...}
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body required'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password required'
            }), 400
        
        # Authenticate user
        user = AuthService.authenticate_user(email, password)
        
        if not user:
            # Log failed login attempt
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent')
            
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password',
                'error_code': 'AUTH_FAILED'
            }), 401
        
        # Generate tokens
        tokens = AuthService.generate_tokens(user.id, user.tenant_id)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log login action
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        AuthService.log_audit(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action=AuditActionEnum.login,
            description=f'User {email} logged in',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                **tokens,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.value,
                    'tenant_id': user.tenant_id
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Login failed',
            'error_code': 'LOGIN_ERROR'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh token endpoint - Get new access token using refresh token.
    
    Returns:
    {
        "status": "success",
        "data": {
            "access_token": "eyJ...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get('user_id')
        tenant_id = identity.get('tenant_id')
        
        # Verify user still exists and is active
        user = User.query.filter_by(
            id=user_id,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        
        if not user or not user.is_active:
            return jsonify({
                'status': 'error',
                'message': 'User not found or inactive'
            }), 401
        
        # Generate new access token
        access_token = AuthService.generate_tokens(user_id, tenant_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Token refreshed',
            'data': {
                'access_token': access_token['access_token'],
                'token_type': 'Bearer',
                'expires_in': 3600
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Token refresh failed'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Logout endpoint - Log user out and invalidate session.
    
    Returns:
    {
        "status": "success",
        "message": "Logout successful"
    }
    """
    try:
        identity = get_jwt_identity()
        user_id = identity.get('user_id')
        tenant_id = identity.get('tenant_id')
        
        # Log logout action
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        AuthService.log_audit(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditActionEnum.logout,
            description='User logged out',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Logout successful'
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Logout failed'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Get current authenticated user information.
    
    Returns:
    {
        "status": "success",
        "data": {
            "user": {...}
        }
    }
    """
    try:
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
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'user': user.to_dict()
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get user information'
        }), 500
