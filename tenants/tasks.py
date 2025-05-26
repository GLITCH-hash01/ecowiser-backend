from celery import shared_task
from .models import Tenant
from projects.models import Project
from billings.models import Billing
from resources.models import Media, CSVTables
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMessage
from django.db.models import Sum

@shared_task
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
      "subscription_tier": tenant.subscription_tier,
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
    to=["harikichus2018@gmail.com"],

  )
  email.content_subtype = "html"
  email.send()
  return "Email sent successfully"

@shared_task
def send_usage_report_to_all():
    t=timezone.now()
    tenants = Tenant.objects.filter(
       billing__subscription_start_date__lte=t,
        billing__subscription_end_date__gte=t
    ).distinct()
    for tenant in tenants:
      get_usage_data(tenant.id)
    return "Usage report sent to all tenants"