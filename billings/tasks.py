from celery import shared_task
from django.utils import timezone
from .models import Subscription, Invoices
from ecowiser.settings import SUBSCRIPTION_TIERS_DETAILS
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

TIER_ORDER= ['Free', 'Pro', 'Enterprise']

@shared_task(name="mail_invoice")
def mail_invoice(tenant_id, invoice_id):

  innvoice = Invoices.objects.get(invoice_id=invoice_id)
  context={
       "invoice": innvoice,
    }
  html= render_to_string("billings/subscription_invoice.html", context)
  subject = f"Invoice for {innvoice.tenant.name} - {innvoice.subscription_id.subscription_tier} Tier"
  email = EmailMessage(
      subject=subject,
      body=html,
      from_email="Ecowiser <harikichus2004@gmail.com>",
      to=[innvoice.tenant.contact_email],
  )
  email.content_subtype = "html"
  email.send()
  
  return f"Invoice email sent to {innvoice.tenant.contact_email} for invoice {invoice_id}."
    
@shared_task(name="upgrade_subscription_tier")
def upgrade_tier(tenant_id, new_tier):
    
    """
    Upgrade the subscription tier for a tenant.
    """
    nw=timezone.now()
    subscription= Subscription.objects.get(tenant_id=tenant_id)

    old_tier = subscription.subscription_tier

    old_price = SUBSCRIPTION_TIERS_DETAILS[old_tier]['price']
    new_price = SUBSCRIPTION_TIERS_DETAILS[new_tier]['price']

    start= subscription.current_cycle_start_date
    end= subscription.current_cycle_end_date
    
    total_days = (end - start).days
    remaining_days = (end - nw ).days
    new_amount = ((new_price - old_price)* remaining_days)/ total_days
    new_amount = max(new_amount, 0)

    subscription.subscription_tier = new_tier
    subscription.next_subscription_tier = new_tier
    subscription.auto_renew = True
    subscription.save()

    
    invoice = Invoices.objects.create(
        tenant=subscription.tenant,
        subscription_id=subscription,
        amount=new_amount,
        billing_start_date=subscription.current_cycle_start_date,
        billing_end_date=subscription.current_cycle_end_date
    )
    mail_invoice.delay(tenant_id=subscription.tenant.id, invoice_id=invoice.invoice_id)
    return f"Tenant {subscription.tenant.name} upgraded to {new_tier} tier."

@shared_task(name="project_deletion_warning_mail")
def project_deletion_warning_mail(tenant_id,new_tier):
    """
    Send a warning email to the tenant about project deletion due to subscription downgrade.
    """
    subscription = Subscription.objects.get(tenant_id=tenant_id)
    tenant = subscription.tenant
    project_count = tenant.projects.count()
    diff=project_count- SUBSCRIPTION_TIERS_DETAILS[new_tier]['projects']
    if diff <= 0:
        return
    else:
      projects_to_delete = tenant.projects.order_by('created_at')[:diff]
      context = {
          "projects": projects_to_delete
      }
      html = render_to_string("billings/project_deletion_warning.html", context)
      subject = f"Project Deletion Warning for {tenant.name}"

      email = EmailMessage(
          subject=subject,
          body=html,
          from_email="Ecowiser <harikichus2004@gmail.com>",
          to=[tenant.contact_email],
      )
      email.content_subtype = "html"
      email.send()



@shared_task(name="renew_subscription")
def renew_subscription():
  subscriptions= Subscription.objects.all()
  for subscription in subscriptions:
    nw=timezone.now().date()
    old_tier = subscription.subscription_tier
    new_tier = subscription.next_subscription_tier
    if nw >= subscription.current_cycle_end_date.date():
      new_start_date = subscription.current_cycle_end_date
      new_end_date = new_start_date + timezone.timedelta(days=30)
      subscription.current_cycle_start_date = new_start_date
      subscription.current_cycle_end_date = new_end_date
      if subscription.auto_renew:
        subscription.subscription_tier = subscription.next_subscription_tier
        subscription.next_subscription_tier = subscription.subscription_tier
        subscription.save()
        invoice = Invoices.objects.create(
            tenant=subscription.tenant,
            subscription_id=subscription,
            amount=SUBSCRIPTION_TIERS_DETAILS[subscription.subscription_tier]['price'],
            billing_start_date=new_start_date,
            billing_end_date=new_end_date
        )
        mail_invoice.delay(tenant_id=subscription.tenant.id, invoice_id=invoice.invoice_id)
      else:
        new_tier="Free"
        subscription.subscription_tier = "Free"
        subscription.next_subscription_tier = "Free"
        subscription.auto_renew = False
        subscription.save()
    
    is_downgrade = TIER_ORDER.index(new_tier) < TIER_ORDER.index(old_tier)
    if is_downgrade:
        project_deletion_warning_mail.delay(
            tenant_id=subscription.tenant.id,
            new_tier=new_tier,
            old_tier=old_tier
        )
        
   