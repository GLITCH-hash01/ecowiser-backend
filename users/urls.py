from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

app_name = 'users'
urlpatterns =[
    path('sign-up/', views.UsersCreateView.as_view(), name='users-create'),
    path('<int:id>/', views.UsersRUDView.as_view(), name='users-get'),
    path('self/', views.SelfRUDView.as_view(), name='users-self'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/verify/', TokenVerifyView.as_view(), name='token_verify'),
]