
from django.contrib import admin
from django.urls import path,include

handler404 = 'utils.error_views.custom_404'
handler500 = 'utils.error_views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('tenants/',include('tenants.urls')),
    path('users/',include('users.urls')),
    path('projects/',include('projects.urls')),
    path('billings/',include('billings.urls')),
    path('resources/', include('resources.urls'))
]
