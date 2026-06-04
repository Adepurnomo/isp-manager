"""
Suspension Routes - Customer suspension and reactivation API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.customers import Customer, CustomerStatusEnum
from app.services.suspension_service import SuspensionService
from app.services.rbac_service import permission_required
from datetime import datetime

suspension_bp = Blueprint('suspension', __name__, url_prefix='/api/v1/customers')

@suspension_bp.route('/<int:customer_id>/suspension-status', methods=['GET'])
@permission_required('customers.read')
def get_suspension_status(customer_id):
    """
    Get suspension eligibility status for customer.
    
    Returns:
    {
        "status": "success",
        "data": {
            "suspension_info": {...}
        }
    }
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        customer = Customer.query.filter_by(
            id=customer_id,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        
        if not customer:
            return jsonify({
                'status': 'error',
                'message': 'Customer not found'
            }), 404
        
        suspension_info = SuspensionService.check_suspension_eligibility(customer_id, tenant_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'customer_id': customer_id,
                'current_status': customer.status.value,
                'suspension_info': suspension_info
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get suspension status'
        }), 500

@suspension_bp.route('/<int:customer_id>/suspend', methods=['POST'])
@permission_required('customers.update')
def suspend_customer(customer_id):
    """
    Suspend customer service.
    
    Request body (optional):
    {
        "reason": "Overdue payment",
        "notes": "Additional notes"
    }
    
    Returns:
    {
        "status": "success",
        "message": "Customer suspended",
        "data": {...}
    }
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        user_id = identity.get('user_id')
        
        customer = Customer.query.filter_by(
            id=customer_id,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        
        if not customer:
            return jsonify({
                'status': 'error',
                'message': 'Customer not found'
            }), 404
        
        if customer.status == CustomerStatusEnum.suspended:
            return jsonify({
                'status': 'error',
                'message': 'Customer is already suspended'
            }), 400
        
        suspended_customer = SuspensionService.suspend_customer(
            customer_id=customer_id,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Customer suspended successfully',
            'data': {
                'customer': suspended_customer.to_dict()
            }
        }), 200
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to suspend customer'
        }), 500

@suspension_bp.route('/<int:customer_id>/reactivate', methods=['POST'])
@permission_required('customers.update')
def reactivate_customer(customer_id):
    """
    Reactivate suspended customer service.
    
    Request body (optional):
    {
        "reason": "Payment received",
        "notes": "Additional notes"
    }
    
    Returns:
    {
        "status": "success",
        "message": "Customer reactivated",
        "data": {...}
    }
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        user_id = identity.get('user_id')
        
        customer = Customer.query.filter_by(
            id=customer_id,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        
        if not customer:
            return jsonify({
                'status': 'error',
                'message': 'Customer not found'
            }), 404
        
        if customer.status != CustomerStatusEnum.suspended:
            return jsonify({
                'status': 'error',
                'message': 'Customer is not suspended'
            }), 400
        
        reactivated_customer = SuspensionService.reactivate_customer(
            customer_id=customer_id,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Customer reactivated successfully',
            'data': {
                'customer': reactivated_customer.to_dict()
            }
        }), 200
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to reactivate customer'
        }), 500
