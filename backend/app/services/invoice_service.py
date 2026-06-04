"""
Invoice Service - Invoice generation and management
"""

from datetime import datetime, timedelta
from app import db
from app.models.invoices import Invoice, InvoiceStatusEnum
from app.models.customers import Customer
from app.models.service_packages import ServicePackage
from app.models.audit_logs import AuditLog, AuditActionEnum

class InvoiceService:
    """
    Service for invoice operations including generation, numbering, and status management.
    """
    
    @staticmethod
    def generate_invoice_number(tenant_id):
        """
        Generate unique invoice number for tenant.
        Format: TENANT_CODE-YYYY-000001
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Unique invoice number string
        """
        from app.models.tenants import Tenant
        
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        if not tenant:
            raise ValueError('Tenant not found')
        
        # Get the last invoice number for this tenant
        last_invoice = Invoice.query.filter_by(
            tenant_id=tenant_id,
            is_deleted=False
        ).order_by(Invoice.id.desc()).first()
        
        # Extract number from last invoice or start at 1
        if last_invoice:
            parts = last_invoice.invoice_number.split('-')
            last_num = int(parts[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        year = datetime.utcnow().year
        invoice_number = f"{tenant.code.upper()}-{year}-{next_num:06d}"
        
        return invoice_number
    
    @staticmethod
    def create_invoice(tenant_id, customer_id, amount, description=None, due_days=30, user_id=None):
        """
        Create new invoice for customer.
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            amount: Invoice amount
            description: Invoice description
            due_days: Days until invoice is due (default 30)
            user_id: User creating the invoice
            
        Returns:
            Created Invoice object
        """
        try:
            # Verify customer exists and belongs to tenant
            customer = Customer.query.filter_by(
                id=customer_id,
                tenant_id=tenant_id,
                is_deleted=False
            ).first()
            
            if not customer:
                raise ValueError('Customer not found')
            
            # Generate invoice number
            invoice_number = InvoiceService.generate_invoice_number(tenant_id)
            
            # Calculate dates
            issued_date = datetime.utcnow().date()
            due_date = issued_date + timedelta(days=due_days)
            
            # Create invoice
            invoice = Invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                invoice_number=invoice_number,
                description=description,
                amount=amount,
                tax_amount=0,  # Can be calculated based on configuration
                total_amount=amount,
                status=InvoiceStatusEnum.unpaid,
                issued_date=issued_date,
                due_date=due_date,
                created_by=user_id
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            # Log action
            audit_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=AuditActionEnum.create,
                entity_type='invoice',
                entity_id=invoice.id,
                description=f'Created invoice {invoice_number}'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return invoice
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def mark_invoice_paid(invoice_id, tenant_id, user_id=None):
        """
        Mark invoice as paid and update status.
        
        Args:
            invoice_id: Invoice ID
            tenant_id: Tenant ID
            user_id: User marking invoice as paid
            
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
                description=f'Marked invoice {invoice.invoice_number} as paid'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return invoice
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def check_overdue_invoices(tenant_id):
        """
        Find all overdue invoices for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of overdue Invoice objects
        """
        today = datetime.utcnow().date()
        
        overdue_invoices = Invoice.query.filter(
            Invoice.tenant_id == tenant_id,
            Invoice.is_deleted == False,
            Invoice.status.in_([InvoiceStatusEnum.unpaid, InvoiceStatusEnum.overdue]),
            Invoice.due_date < today
        ).all()
        
        return overdue_invoices
    
    @staticmethod
    def update_overdue_status(tenant_id):
        """
        Update status of overdue invoices.
        Changes unpaid invoices past due date to overdue status.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Number of invoices updated
        """
        try:
            overdue_invoices = InvoiceService.check_overdue_invoices(tenant_id)
            
            count = 0
            for invoice in overdue_invoices:
                if invoice.status == InvoiceStatusEnum.unpaid:
                    invoice.status = InvoiceStatusEnum.overdue
                    invoice.updated_date = datetime.utcnow()
                    count += 1
            
            if count > 0:
                db.session.commit()
            
            return count
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def get_invoice_summary(tenant_id):
        """
        Get summary of invoices for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with invoice statistics
        """
        invoices = Invoice.query.filter_by(tenant_id=tenant_id, is_deleted=False).all()
        
        summary = {
            'total_invoices': len(invoices),
            'paid_invoices': len([i for i in invoices if i.status == InvoiceStatusEnum.paid]),
            'unpaid_invoices': len([i for i in invoices if i.status == InvoiceStatusEnum.unpaid]),
            'overdue_invoices': len([i for i in invoices if i.status == InvoiceStatusEnum.overdue]),
            'total_amount': sum(i.total_amount for i in invoices),
            'paid_amount': sum(i.total_amount for i in invoices if i.status == InvoiceStatusEnum.paid),
            'unpaid_amount': sum(i.total_amount for i in invoices if i.status in [InvoiceStatusEnum.unpaid, InvoiceStatusEnum.overdue])
        }
        
        return summary
