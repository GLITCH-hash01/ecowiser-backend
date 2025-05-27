from celery import shared_task
from .models import Tenant
from projects.models import Project
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMessage
from django.db.models import Sum
from ecowiser.settings import SUBSCRIPTION_TIERS_DETAILS

@shared_task(name="send_usage_report")
def get_usage_data(tenant_id):
  tenant= Tenant.objects.get(id=tenant_id)
  projects = Project.objects.filter(tenant=tenant)
  project_count = projects.count()
  user_count = tenant.users.count()
  csv_files=0
  media_files={
    "total": 0,
    "public": 0,
    "private": 0
  }
  media_size=0
  csv_size=0
  for project in projects:
    csv_files += project.csv_tables.count()
    media_files["total"] += project.media.count()
    media_files["public"] += project.media.filter(visibility="Public").count()
    media_files["private"] += project.media.filter(visibility="Private").count()  
    media_size += project.media.aggregate(
      total_size=Sum('file_size')
    )['total_size'] or 0
    csv_size += project.csv_tables.aggregate(
      total_size=Sum('file_size')
    )['total_size'] or 0

  total_storage_used = media_size + csv_size
  storage_used = f"{total_storage_used / (1024 * 1024):.2f}MB" if total_storage_used else "0MB"
  
  subject = f"Usage Report for {tenant.name}"
  html = render_to_string("tenants/usage_report.html", {
      "tenant_name": tenant.name,
      "subscription_tier": tenant.subscriptions.subscription_tier,
      "report_date": timezone.now().strftime("%Y-%m-%d"),
      "users_count": user_count,
      "project_count": project_count,
      "csv_count": csv_files,
      "media_total": media_files["total"],
      "media_public": media_files["public"],
      "media_private": media_files["private"],
      "storage_used": storage_used,
  })

  email = EmailMessage(
    subject=subject,
    body=html,
    from_email="Ecowiser <harikichus2004@gmail.com>",
    to=[tenant.contact_email],

  )
  email.content_subtype = "html"
  email.send()
  return "Email sent successfully"

@shared_task(name="send_usage_report_to_all")
def send_usage_report_to_all():
    t=timezone.now()
    tenants = Tenant.objects.filter(
        subscription_tier__in=[ 'Enterprise', 'Pro'],)
    for tenant in tenants:
      get_usage_data(tenant.id)
    return "Usage report sent to all tenants"

@shared_task(name="auto_project_deletion")
def auto_project_deletion():
  tenants=Tenant.objects.filter(subscriptions__subscription_tier__in=['Free', 'Pro']).distinct()
  for tenant in tenants:
    try:
      project_count = tenant.projects.count()
      allowed_projects = SUBSCRIPTION_TIERS_DETAILS[tenant.subscriptions.subscription_tier]['projects']
      extra_projects = project_count - allowed_projects
      if extra_projects > 0:
        nw = timezone.now()
        start = tenant.subscriptions.current_cycle_start_date
        if (nw - start).days >= 10:
          list_of_projects = tenant.projects.order_by('created_at')[:extra_projects]
          list_of_projects.delete()
          context={
            "tenant_name": tenant.name,
            "subscription_tier": tenant.subscriptions.subscription_tier,
            "deleted_projects": list_of_projects,
          }
          html=render_to_string('tenants/project_deleted.html', context)
          subject = f"Project Deletion Notification for {tenant.name}"
          email = EmailMessage(
            subject=subject,
            body=html,
            from_email="Ecowiser <harikichus2004@gmail.com>",
            to=[tenant.contact_email],
          )
          email.content_subtype = "html"
          email.send()
    except Exception as e:
      print(f"Error occurred while deleting projects for tenant {tenant.id}: {e}")
  return "Auto project deletion task completed successfully"
    