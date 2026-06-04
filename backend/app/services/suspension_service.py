"""
Customer Suspension Service - Automatic service suspension for overdue payments
"""

from datetime import datetime, timedelta
from app import db
from app.models.customers import Customer, CustomerStatusEnum
from app.models.invoices import Invoice, InvoiceStatusEnum
from app.models.radius_users import RadiusUser
from app.models.vpn_users import VPNUser
from app.models.customer_notifications import CustomerNotification, CustomerNotificationTypeEnum
from app.models.audit_logs import AuditLog, AuditActionEnum

class SuspensionService:
    """
    Service for automatic customer suspension based on overdue payments.
    """
    
    @staticmethod
    def get_suspension_policy(tenant_id):
        """
        Get suspension policy configuration for tenant.
        Default: Suspend after 7 days overdue.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with suspension policy
        """
        # In production, this would be stored in a config table
        return {
            'grace_period_days': 0,  # Days after due date before suspension
            'suspension_days': 7,    # Days overdue before automatic suspension
            'reactivation_requires_full_payment': True,
            'notify_before_suspension_days': 3
        }
    
    @staticmethod
    def check_suspension_eligibility(customer_id, tenant_id):
        """
        Check if customer should be suspended based on overdue invoices.
        
        Args:
            customer_id: Customer ID
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with suspension eligibility info
        """
        customer = Customer.query.filter_by(
            id=customer_id,
            tenant_id=tenant_id,
            is_deleted=False
        ).first()
        
        if not customer:
            return {'eligible': False, 'reason': 'Customer not found'}
        
        # Check for overdue invoices
        today = datetime.utcnow().date()
        policy = SuspensionService.get_suspension_policy(tenant_id)
        
        overdue_invoices = Invoice.query.filter(
            Invoice.customer_id == customer_id,
            Invoice.tenant_id == tenant_id,
            Invoice.is_deleted == False,
            Invoice.status.in_([InvoiceStatusEnum.unpaid, InvoiceStatusEnum.overdue]),
            Invoice.due_date < today
        ).all()
        
        if not overdue_invoices:
            return {'eligible': False, 'reason': 'No overdue invoices'}
        
        # Get oldest overdue invoice
        oldest_invoice = min(overdue_invoices, key=lambda x: x.due_date)
        days_overdue = (today - oldest_invoice.due_date).days
        
        suspension_days = policy['suspension_days'] + policy['grace_period_days']
        
        return {
            'eligible': days_overdue >= suspension_days,
            'days_overdue': days_overdue,
            'suspension_threshold': suspension_days,
            'oldest_overdue_date': oldest_invoice.due_date.isoformat(),
            'total_overdue_amount': sum(i.total_amount for i in overdue_invoices)
        }
    
    @staticmethod
    def suspend_customer(customer_id, tenant_id, user_id=None):
        """
        Suspend customer service and disable all access.
        
        Args:
            customer_id: Customer ID
            tenant_id: Tenant ID
            user_id: User performing suspension
            
        Returns:
            Suspended Customer object
        """
        try:
            customer = Customer.query.filter_by(
                id=customer_id,
                tenant_id=tenant_id,
                is_deleted=False
            ).first()
            
            if not customer:
                raise ValueError('Customer not found')
            
            if customer.status == CustomerStatusEnum.suspended:
                raise ValueError('Customer is already suspended')
            
            # Update customer status
            customer.status = CustomerStatusEnum.suspended
            customer.suspension_date = datetime.utcnow()
            customer.updated_by = user_id
            customer.updated_date = datetime.utcnow()
            
            db.session.commit()
            
            # Disable RADIUS users
            SuspensionService._disable_radius_users(customer_id)
            
            # Disable VPN users
            SuspensionService._disable_vpn_users(customer_id)
            
            # Log action
            audit_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=AuditActionEnum.suspend,
                entity_type='customer',
                entity_id=customer_id,
                description=f'Suspended customer {customer.customer_number} due to overdue payment'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            # Send suspension notification
            SuspensionService._send_suspension_notification(customer)
            
            return customer
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def reactivate_customer(customer_id, tenant_id, user_id=None):
        """
        Reactivate suspended customer service.
        
        Args:
            customer_id: Customer ID
            tenant_id: Tenant ID
            user_id: User performing reactivation
            
        Returns:
            Reactivated Customer object
        """
        try:
            customer = Customer.query.filter_by(
                id=customer_id,
                tenant_id=tenant_id,
                is_deleted=False
            ).first()
            
            if not customer:
                raise ValueError('Customer not found')
            
            if customer.status != CustomerStatusEnum.suspended:
                raise ValueError('Customer is not suspended')
            
            # Update customer status
            customer.status = CustomerStatusEnum.active
            customer.suspension_date = None
            customer.updated_by = user_id
            customer.updated_date = datetime.utcnow()
            
            db.session.commit()
            
            # Re-enable RADIUS users
            SuspensionService._enable_radius_users(customer_id)
            
            # Re-enable VPN users
            SuspensionService._enable_vpn_users(customer_id)
            
            # Log action
            audit_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=AuditActionEnum.activate,
                entity_type='customer',
                entity_id=customer_id,
                description=f'Reactivated customer {customer.customer_number}'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            # Send reactivation notification
            SuspensionService._send_reactivation_notification(customer)
            
            return customer
        
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def _disable_radius_users(customer_id):
        """
        Disable all RADIUS users for a customer.
        """
        try:
            radius_users = RadiusUser.query.filter_by(
                customer_id=customer_id,
                is_deleted=False
            ).all()
            
            for user in radius_users:
                user.is_active = False
                user.disable_date = datetime.utcnow()
            
            if radius_users:
                db.session.commit()
        
        except Exception as e:
            print(f"Error disabling RADIUS users: {str(e)}")
    
    @staticmethod
    def _enable_radius_users(customer_id):
        """
        Enable all RADIUS users for a customer.
        """
        try:
            radius_users = RadiusUser.query.filter_by(
                customer_id=customer_id,
                is_deleted=False
            ).all()
            
            for user in radius_users:
                user.is_active = True
                user.enable_date = datetime.utcnow()
                user.disable_date = None
            
            if radius_users:
                db.session.commit()
        
        except Exception as e:
            print(f"Error enabling RADIUS users: {str(e)}")
    
    @staticmethod
    def _disable_vpn_users(customer_id):
        """
        Disable all VPN users for a customer.
        """
        try:
            vpn_users = VPNUser.query.filter_by(
                customer_id=customer_id,
                is_deleted=False
            ).all()
            
            for user in vpn_users:
                user.is_active = False
                user.disable_date = datetime.utcnow()
            
            if vpn_users:
                db.session.commit()
        
        except Exception as e:
            print(f"Error disabling VPN users: {str(e)}")
    
    @staticmethod
    def _enable_vpn_users(customer_id):
        """
        Enable all VPN users for a customer.
        """
        try:
            vpn_users = VPNUser.query.filter_by(
                customer_id=customer_id,
                is_deleted=False
            ).all()
            
            for user in vpn_users:
                user.is_active = True
                user.enable_date = datetime.utcnow()
                user.disable_date = None
            
            if vpn_users:
                db.session.commit()
        
        except Exception as e:
            print(f"Error enabling VPN users: {str(e)}")
    
    @staticmethod
    def _send_suspension_notification(customer):
        """
        Send suspension notification to customer.
        """
        try:
            notification = CustomerNotification(
                tenant_id=customer.tenant_id,
                customer_id=customer.id,
                notification_type=CustomerNotificationTypeEnum.suspension,
                title='Service Suspended',
                message='Your service has been suspended due to overdue payment. Please contact support to reactivate.',
                sent_via_email=True,
                sent_via_whatsapp=False
            )
            db.session.add(notification)
            db.session.commit()
        
        except Exception as e:
            print(f"Error sending suspension notification: {str(e)}")
    
    @staticmethod
    def _send_reactivation_notification(customer):
        """
        Send reactivation notification to customer.
        """
        try:
            notification = CustomerNotification(
                tenant_id=customer.tenant_id,
                customer_id=customer.id,
                notification_type=CustomerNotificationTypeEnum.system,
                title='Service Reactivated',
                message='Your service has been successfully reactivated.',
                sent_via_email=True,
                sent_via_whatsapp=False
            )
            db.session.add(notification)
            db.session.commit()
        
        except Exception as e:
            print(f"Error sending reactivation notification: {str(e)}")
