from django.urls import path
from . import views 

app_name = 'billings'
urlpatterns = [
   path('upgrade/',views.SubscriptionUpgradeView.as_view(), name='upgrade-subscription'),
   path('downgrade/',views.SubscriptionDowngradeView.as_view(), name='downgrade-subscription'),
   path('invoices/', views.InvoiceListView.as_view(), name='invoices-list'),
   path('subscription/', views.SubscriptionDetailsView.as_view(), name='subscription-detail'),
]