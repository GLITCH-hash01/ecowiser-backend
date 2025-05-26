from django.urls import path
from . import views

app_name = 'tenants'
urlpatterns=[
    path('',views.TenantsListView.as_view(), name='tenants-list'),
    path('create/',views.TenantsCreateView.as_view(), name='tenants-create'),
    path('<uuid:tenant_id>/',views.TenantsRUDView.as_view(), name='tenants-get'),
    path('members/', views.ManageMembersView.as_view(), name='tenants-manage-users'),
    path('members/to-admin/',views.RoleToAdminView.as_view(), name='tenants-role-to-admin'),
    path('members/to-owner/',views.RoleToOwnerView.as_view(), name='tenants-role-to-owner'),
    path('members/to-member/',views.RoleToMemberView.as_view(), name='tenants-role-to-member'),
    path('generate-usage-report/', views.GenerateUsageReportView.as_view(), name='tenants-generate-usage-report'),

]