"""
Update billing jobs to include suspension checks
"""

from datetime import datetime, timedelta
from app import db, scheduler
from app.models.tenants import Tenant
from app.models.customers import Customer, CustomerStatusEnum
from app.models.invoices import Invoice, InvoiceStatusEnum
from app.services.invoice_service import InvoiceService
from app.services.payment_service import PaymentService
from app.services.suspension_service import SuspensionService

def schedule_billing_jobs():
    """
    Schedule all billing-related background jobs.
    """
    # Daily task to check for overdue invoices
    scheduler.add_job(
        id='check_overdue_invoices',
        func=check_overdue_invoices_job,
        trigger='cron',
        hour=0,
        minute=0,
        name='Check Overdue Invoices',
        replace_existing=True
    )
    
    # Daily task to generate monthly invoices
    scheduler.add_job(
        id='generate_monthly_invoices',
        func=generate_monthly_invoices_job,
        trigger='cron',
        day=1,
        hour=1,
        minute=0,
        name='Generate Monthly Invoices',
        replace_existing=True
    )
    
    # Daily task to check for suspension eligibility
    scheduler.add_job(
        id='check_suspension_eligibility',
        func=check_suspension_eligibility_job,
        trigger='cron',
        hour=6,
        minute=0,
        name='Check Suspension Eligibility',
        replace_existing=True
    )

def check_overdue_invoices_job():
    """
    Check for overdue invoices and update their status.
    Called daily at midnight.
    """
    try:
        tenants = Tenant.query.filter_by(is_active=True).all()
        
        for tenant in tenants:
            # Update overdue status
            updated_count = InvoiceService.update_overdue_status(tenant.id)
            
            if updated_count > 0:
                print(f"Updated {updated_count} overdue invoices for tenant {tenant.code}")
    
    except Exception as e:
        print(f"Error in check_overdue_invoices_job: {str(e)}")

def generate_monthly_invoices_job():
    """
    Generate monthly invoices for all active customers.
    Called on the 1st of each month at 1 AM.
    """
    try:
        tenants = Tenant.query.filter_by(is_active=True).all()
        
        for tenant in tenants:
            # Get all active customers with service packages
            customers = Customer.query.filter(
                Customer.tenant_id == tenant.id,
                Customer.is_deleted == False,
                Customer.status == CustomerStatusEnum.active,
                Customer.service_package_id.isnot(None)
            ).all()
            
            for customer in customers:
                try:
                    # Create invoice for monthly service fee
                    if customer.service_package:
                        InvoiceService.create_invoice(
                            tenant_id=tenant.id,
                            customer_id=customer.id,
                            amount=customer.service_package.price,
                            description=f"Monthly service fee - {customer.service_package.name}",
                            due_days=30,
                            user_id=None  # System-generated
                        )
                
                except Exception as e:
                    print(f"Error generating invoice for customer {customer.id}: {str(e)}")
    
    except Exception as e:
        print(f"Error in generate_monthly_invoices_job: {str(e)}")

def check_suspension_eligibility_job():
    """
    Check for customers eligible for suspension based on overdue invoices.
    Called daily at 6 AM.
    """
    try:
        tenants = Tenant.query.filter_by(is_active=True).all()
        
        for tenant in tenants:
            # Get all active customers
            active_customers = Customer.query.filter(
                Customer.tenant_id == tenant.id,
                Customer.is_deleted == False,
                Customer.status == CustomerStatusEnum.active
            ).all()
            
            for customer in active_customers:
                try:
                    # Check suspension eligibility
                    eligibility = SuspensionService.check_suspension_eligibility(
                        customer.id,
                        tenant.id
                    )
                    
                    if eligibility['eligible']:
                        # Suspend customer
                        SuspensionService.suspend_customer(
                            customer_id=customer.id,
                            tenant_id=tenant.id,
                            user_id=None  # System-generated
                        )
                        print(f"Suspended customer {customer.customer_number} for overdue payment")
                
                except Exception as e:
                    print(f"Error checking suspension eligibility for customer {customer.id}: {str(e)}")
    
    except Exception as e:
        print(f"Error in check_suspension_eligibility_job: {str(e)}")
