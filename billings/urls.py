from django.urls import path
from . import views 
app_name = 'billings'

urlpatterns = [
    path('upgrade/', views.UpgradeView.as_view(), name='upgrade'),
    path('downgrade/', views.DowngradingView.as_view(), name='downgrade'),
    path('cancel/<uuid:billing_id>/', views.CancellingQueuedSubscriptionView.as_view(), name='cancel_subscription'),
    path('billing-history/', views.BillingListView.as_view(), name='billing_history'),
]