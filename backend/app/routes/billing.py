"""
Billing Routes - Invoice and Payment API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db
from app.models.invoices import Invoice, InvoiceStatusEnum
from app.models.payments import Payment
from app.models.customers import Customer
from app.services.invoice_service import InvoiceService
from app.services.payment_service import PaymentService
from app.services.rbac_service import permission_required
from app.services.auth_service import AuthService
from datetime import datetime

invoices_bp = Blueprint('invoices', __name__, url_prefix='/api/v1/invoices')
payments_bp = Blueprint('payments', __name__, url_prefix='/api/v1/payments')

# ==================== INVOICE ROUTES ====================

@invoices_bp.route('', methods=['POST'])
@permission_required('invoices.create')
def create_invoice():
    """
    Create new invoice for customer.
    
    Request body:
    {
        "customer_id": 1,
        "amount": 500000,
        "description": "Monthly service fee",
        "due_days": 30
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
        if 'customer_id' not in data or 'amount' not in data:
            return jsonify({
                'status': 'error',
                'message': 'customer_id and amount required'
            }), 400
        
        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=data['customer_id'],
            amount=data['amount'],
            description=data.get('description'),
            due_days=data.get('due_days', 30),
            user_id=user_id
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Invoice created',
            'data': {
                'invoice': invoice.to_dict()
            }
        }), 201
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to create invoice'
        }), 500

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@permission_required('invoices.read')
def get_invoice(invoice_id):
    """
    Get invoice by ID.
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        
        if not invoice:
            return jsonify({
                'status': 'error',
                'message': 'Invoice not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'invoice': invoice.to_dict()
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get invoice'
        }), 500

@invoices_bp.route('', methods=['GET'])
@permission_required('invoices.read')
def list_invoices():
    """
    List invoices with filtering and pagination.
    
    Query parameters:
    - customer_id: Filter by customer
    - status: Filter by status (unpaid, paid, overdue, draft, cancelled)
    - from_date: Filter from date (YYYY-MM-DD)
    - to_date: Filter to date (YYYY-MM-DD)
    - page: Page number
    - per_page: Items per page
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        per_page = min(per_page, 100)
        
        # Build query
        query = Invoice.query.filter_by(tenant_id=tenant_id, is_deleted=False)
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if status:
            try:
                status_enum = InvoiceStatusEnum[status]
                query = query.filter_by(status=status_enum)
            except KeyError:
                pass
        
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                query = query.filter(Invoice.issued_date >= from_date_obj)
            except ValueError:
                pass
        
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                query = query.filter(Invoice.issued_date <= to_date_obj)
            except ValueError:
                pass
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'status': 'success',
            'data': {
                'invoices': [inv.to_dict() for inv in paginated.items],
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
            'message': 'Failed to list invoices'
        }), 500

@invoices_bp.route('/summary', methods=['GET'])
@permission_required('invoices.read')
def invoice_summary():
    """
    Get invoice summary for tenant.
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        summary = InvoiceService.get_invoice_summary(tenant_id)
        
        return jsonify({
            'status': 'success',
            'data': summary
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get summary'
        }), 500

# ==================== PAYMENT ROUTES ====================

@payments_bp.route('', methods=['POST'])
@permission_required('payments.create')
def record_payment():
    """
    Record a payment for an invoice.
    
    Request body:
    {
        "invoice_id": 1,
        "amount": 500000,
        "method": "bank_transfer",
        "reference_number": "TRF123456"
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
        if 'invoice_id' not in data or 'amount' not in data or 'method' not in data:
            return jsonify({
                'status': 'error',
                'message': 'invoice_id, amount, and method required'
            }), 400
        
        payment = PaymentService.record_payment(
            tenant_id=tenant_id,
            invoice_id=data['invoice_id'],
            amount=data['amount'],
            method=data['method'],
            reference_number=data.get('reference_number'),
            user_id=user_id
        )
        
        # Reconcile invoice
        PaymentService.reconcile_invoice_payment(
            invoice_id=data['invoice_id'],
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Payment recorded',
            'data': {
                'payment': payment.to_dict()
            }
        }), 201
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to record payment'
        }), 500

@payments_bp.route('/<int:payment_id>', methods=['GET'])
@permission_required('payments.read')
def get_payment(payment_id):
    """
    Get payment by ID.
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        payment = Payment.query.filter_by(
            id=payment_id,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        
        if not payment:
            return jsonify({
                'status': 'error',
                'message': 'Payment not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'payment': payment.to_dict()
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get payment'
        }), 500

@payments_bp.route('', methods=['GET'])
@permission_required('payments.read')
def list_payments():
    """
    List payments with filtering and pagination.
    
    Query parameters:
    - invoice_id: Filter by invoice
    - customer_id: Filter by customer
    - method: Filter by payment method
    - status: Filter by payment status
    - page: Page number
    - per_page: Items per page
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        invoice_id = request.args.get('invoice_id', type=int)
        method = request.args.get('method')
        status = request.args.get('status')
        
        per_page = min(per_page, 100)
        
        # Build query
        query = Payment.query.filter_by(tenant_id=tenant_id, is_deleted=False)
        
        if invoice_id:
            query = query.filter_by(invoice_id=invoice_id)
        
        if method:
            query = query.filter_by(method=method)
        
        if status:
            query = query.filter_by(status=status)
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'status': 'success',
            'data': {
                'payments': [p.to_dict() for p in paginated.items],
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
            'message': 'Failed to list payments'
        }), 500

@payments_bp.route('/summary', methods=['GET'])
@permission_required('payments.read')
def payment_summary():
    """
    Get payment summary for tenant.
    """
    try:
        identity = get_jwt_identity()
        tenant_id = identity.get('tenant_id')
        
        summary = PaymentService.get_payment_summary(tenant_id)
        
        return jsonify({
            'status': 'success',
            'data': summary
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get summary'
        }), 500
