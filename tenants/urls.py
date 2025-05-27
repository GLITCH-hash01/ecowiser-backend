from django.urls import path
from . import views

app_name = 'tenants'
urlpatterns=[
    path('create/',views.TenantsCreateView.as_view(), name='tenants-create'),
    path('manage/',views.TenantsRUDView.as_view(), name='tenants-get'),
    path('members/', views.ManageMembersView.as_view(), name='tenants-manage-users'),
    path('members/role/',views.ManageUsersRoleView.as_view(), name='tenants-manage-users-role'),
    path('generate-usage-report/', views.GenerateUsageReportView.as_view(), name='tenants-generate-usage-report'),

]