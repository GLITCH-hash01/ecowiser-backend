from django.urls import path
from . import views 
app_name = 'billings'

urlpatterns = [
    path('upgrade/', views.UpgradeView.as_view(), name='upgrade'),
    path('downgrade/', views.DowngradingView.as_view(), name='downgrade'),
]