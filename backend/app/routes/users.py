"""
User Management Routes
Provides REST API endpoints for user management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db
from app.models.users import User, RoleEnum
from app.services.rbac_service import permission_required
from app.services.auth_service import AuthService, token_required
from app.models.audit_logs import AuditLog, AuditActionEnum
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

@users_bp.route('', methods=['POST'])
@permission_required('users.create')
def create_user():
    """
    Create new user.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+62812345678",
        "role": "billing"
    }
    
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
        tenant_id = identity.get('tenant_id')
        user_id = identity.get('user_id')
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body required'
            }), 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'status': 'error',
                'message': 'Email already in use'
            }), 400
        
        # Validate role
        try:
            role = RoleEnum[data['role']]
        except KeyError:
            return jsonify({
                'status': 'error',
                'message': f'Invalid role: {data["role"]}'
            }), 400
        
        # Create user
        new_user = User(
            tenant_id=tenant_id,
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=role,
            is_active=data.get('is_active', True),
            created_by=user_id
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log action
        AuthService.log_audit(
            user_id=user_id,
            tenant_id=tenant_id,
            action=AuditActionEnum.create,
            entity_type='user',
            entity_id=new_user.id,
            description=f'Created user {new_user.email}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': {
                'user': new_user.to_dict()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create user'
        }), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@permission_required('users.read')
def get_user(user_id):
    """
    Get user by ID.
    
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
            'message': 'Failed to get user'
        }), 500

@users_bp.route('', methods=['GET'])
@permission_required('users.read')
def list_users():
    """
    List all users in tenant with pagination.
    
    Query parameters:
    - page: Page number (default 1)
    - per_page: Items per page (default 20, max 100)
    - search: Search by email or name
    - role: Filter by role
    - is_active: Filter by active status
    
    Returns:
    {
        "status": "success",
        "data": {
            "users": [...],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 100,
                "pages": 5
            }
        }
    }
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        
        # Limit per_page
        per_page = min(per_page, 100)
        
        # Build query
        query = User.query.filter_by(tenant_id=tenant_id, is_deleted=False)
        
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        if role:
            try:
                role_enum = RoleEnum[role]
                query = query.filter_by(role=role_enum)
            except KeyError:
                pass
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'status': 'success',
            'data': {
                'users': [user.to_dict() for user in paginated.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': paginated.total,
                    'pages': paginated.pages
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to list users'
        }), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@permission_required('users.update')
def update_user(user_id):
    """
    Update user by ID.
    
    Request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+62812345678",
        "role": "billing",
        "is_active": true
    }
    
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
        tenant_id = identity.get('tenant_id')
        current_user_id = identity.get('user_id')
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body required'
            }), 400
        
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
        
        # Update fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'role' in data:
            try:
                user.role = RoleEnum[data['role']]
            except KeyError:
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid role: {data["role"]}'
                }), 400
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.updated_by = current_user_id
        user.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        # Log action
        AuthService.log_audit(
            user_id=current_user_id,
            tenant_id=tenant_id,
            action=AuditActionEnum.update,
            entity_type='user',
            entity_id=user.id,
            description=f'Updated user {user.email}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'User updated successfully',
            'data': {
                'user': user.to_dict()
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update user'
        }), 500

@users_bp.route('/<int:user_id>/password', methods=['PUT'])
@token_required
def change_password(user_id):
    """
    Change user password.
    
    Request body:
    {
        "old_password": "oldpass123",
        "new_password": "newpass456"
    }
    
    Returns:
    {
        "status": "success",
        "message": "Password changed successfully"
    }
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        current_user_id = identity.get('user_id')
        data = request.get_json()
        
        # Users can only change their own password unless they're admin
        if current_user_id != user_id:
            current_user = User.query.filter_by(
                id=current_user_id,
                tenant_id=tenant_id
            ).first()
            if not current_user or current_user.role.value not in ['super_admin', 'tenant_admin']:
                return jsonify({
                    'status': 'error',
                    'message': 'Cannot change another user password'
                }), 403
        
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
        
        if not data or 'old_password' not in data or 'new_password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Old and new password required'
            }), 400
        
        # Verify old password (only if changing own password)
        if current_user_id == user_id:
            if not user.verify_password(data['old_password']):
                return jsonify({
                    'status': 'error',
                    'message': 'Old password is incorrect'
                }), 400
        
        # Set new password
        user.set_password(data['new_password'])
        user.updated_by = current_user_id
        user.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        # Log action
        AuthService.log_audit(
            user_id=current_user_id,
            tenant_id=tenant_id,
            action=AuditActionEnum.update,
            entity_type='user',
            entity_id=user.id,
            description=f'Changed password for user {user.email}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to change password'
        }), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@permission_required('users.delete')
def delete_user(user_id):
    """
    Soft delete user by ID.
    
    Returns:
    {
        "status": "success",
        "message": "User deleted successfully"
    }
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        current_user_id = identity.get('user_id')
        
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
        
        # Cannot delete yourself
        if current_user_id == user_id:
            return jsonify({
                'status': 'error',
                'message': 'Cannot delete your own account'
            }), 400
        
        # Soft delete
        user.is_deleted = True
        user.updated_by = current_user_id
        user.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        # Log action
        AuthService.log_audit(
            user_id=current_user_id,
            tenant_id=tenant_id,
            action=AuditActionEnum.delete,
            entity_type='user',
            entity_id=user.id,
            description=f'Deleted user {user.email}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'User deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete user'
        }), 500
