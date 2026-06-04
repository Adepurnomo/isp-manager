"""
Payment Service - Payment processing and reconciliation
"""

from datetime import datetime
from decimal import Decimal
from app import db
from app.models.payments import Payment, PaymentStatusEnum, PaymentMethodEnum, PaymentTransaction, PaymentCallback
from app.models.invoices import Invoice, InvoiceStatusEnum
from app.models.audit_logs import AuditLog, AuditActionEnum

class PaymentService:
    """
    Service for payment operations including recording, verification, and reconciliation.
    """
    
    @staticmethod
    def generate_payment_number(tenant_id):
        """
        Generate unique payment number for tenant.
        Format: PAY-YYYY-000001
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Unique payment number string
        """
        # Get the last payment number for this tenant
        last_payment = Payment.query.filter_by(
            tenant_id=tenant_id,
            is_deleted=False
        ).order_by(Payment.id.desc()).first()
        
        # Extract number from last payment or start at 1
        if last_payment:
            parts = last_payment.payment_number.split('-')
            last_num = int(parts[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        year = datetime.utcnow().year
        payment_number = f"PAY-{year}-{next_num:06d}"
        
        return payment_number
    
    @staticmethod
    def record_payment(tenant_id, invoice_id, amount, method, reference_number=None, user_id=None):
        """
        Record a payment for an invoice.
        
        Args:
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            amount: Payment amount
            method: Payment method (from PaymentMethodEnum)
            reference_number: External reference number
            user_id: User recording the payment
            
        Returns:
            Created Payment object
        """
        try:
            # Verify invoice exists and belongs to tenant
            invoice = Invoice.query.filter_by(
                id=invoice_id,
                tenant_id=tenant_id,
                is_deleted=False
            ).first()
            
            if not invoice:
                raise ValueError('Invoice not found')
            
            # Verify invoice is not already paid
            if invoice.status == InvoiceStatusEnum.paid:
                raise ValueError('Invoice is already paid')
            
            # Generate payment number
            payment_number = PaymentService.generate_payment_number(tenant_id)
            
            # Parse method if string
            if isinstance(method, str):
                method = PaymentMethodEnum[method]
            
            # Create payment
            payment = Payment(
                tenant_id=tenant_id,
                invoice_id=invoice_id,
                payment_number=payment_number,
                amount=amount,
                method=method,
                status=PaymentStatusEnum.completed,
                reference_number=reference_number,
                payment_date=datetime.utcnow(),
                created_by=user_id
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Log action
            audit_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=AuditActionEnum.payment_recorded,
                entity_type='invoice',
                entity_id=invoice_id,
                description=f'Recorded payment {payment_number} for invoice {invoice.invoice_number}'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return payment
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def reconcile_invoice_payment(invoice_id, tenant_id, user_id=None):
        """
        Reconcile payments for an invoice and update invoice status.
        If total paid amount >= invoice total, mark invoice as paid.
        
        Args:
            invoice_id: Invoice ID
            tenant_id: Tenant ID
            user_id: User reconciling the payment
            
        Returns:
            Updated Invoice object
        """
        try:
            invoice = Invoice.query.filter_by(
                id=invoice_id,
                tenant_id=tenant_id,
                is_deleted=False
            ).first()
            
            if not invoice:
                raise ValueError('Invoice not found')
            
            # Calculate total paid amount
            total_paid = db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.invoice_id == invoice_id,
                Payment.status == PaymentStatusEnum.completed,
                Payment.is_deleted == False
            ).scalar() or Decimal(0)
            
            # Update invoice status based on payment
            if total_paid >= invoice.total_amount:
                invoice.status = InvoiceStatusEnum.paid
                invoice.paid_date = datetime.utcnow().date()
                invoice.updated_by = user_id
                invoice.updated_date = datetime.utcnow()
                
                db.session.commit()
                
                # Log action
                audit_log = AuditLog(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    action=AuditActionEnum.update,
                    entity_type='invoice',
                    entity_id=invoice.id,
                    description=f'Reconciled invoice {invoice.invoice_number} as paid'
                )
                db.session.add(audit_log)
                db.session.commit()
            
            return invoice
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def process_gateway_callback(tenant_id, gateway, webhook_id, payload, signature):
        """
        Process payment gateway webhook callback.
        
        Args:
            tenant_id: Tenant ID
            gateway: Gateway name (midtrans, xendit, tripay)
            webhook_id: Webhook ID from gateway
            payload: Webhook payload (dict)
            signature: Webhook signature for verification
            
        Returns:
            PaymentCallback object
        """
        try:
            # Create callback record
            callback = PaymentCallback(
                tenant_id=tenant_id,
                gateway=gateway,
                webhook_id=webhook_id,
                payload=payload,
                signature=signature,
                is_verified=False,
                status='pending'
            )
            
            db.session.add(callback)
            db.session.commit()
            
            return callback
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def verify_gateway_signature(callback, gateway_secret):
        """
        Verify payment gateway webhook signature.
        
        Args:
            callback: PaymentCallback object
            gateway_secret: Gateway secret key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib
        import json
        
        # Create signature based on gateway type
        # Different gateways use different signature algorithms
        payload_string = json.dumps(callback.payload, separators=(',', ':'), sort_keys=True)
        
        # Generate expected signature
        expected_signature = hmac.new(
            gateway_secret.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(callback.signature, expected_signature)
    
    @staticmethod
    def get_payment_summary(tenant_id):
        """
        Get summary of payments for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with payment statistics
        """
        payments = Payment.query.filter_by(tenant_id=tenant_id, is_deleted=False).all()
        
        summary = {
            'total_payments': len(payments),
            'completed_payments': len([p for p in payments if p.status == PaymentStatusEnum.completed]),
            'pending_payments': len([p for p in payments if p.status == PaymentStatusEnum.pending]),
            'failed_payments': len([p for p in payments if p.status == PaymentStatusEnum.failed]),
            'total_amount': sum(p.amount for p in payments),
            'completed_amount': sum(p.amount for p in payments if p.status == PaymentStatusEnum.completed),
            'pending_amount': sum(p.amount for p in payments if p.status == PaymentStatusEnum.pending)
        }
        
        return summary
