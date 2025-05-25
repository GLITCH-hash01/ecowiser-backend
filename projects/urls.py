from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
  path('create/', views.CreateProjectView.as_view(), name='projects-create'),
  path('', views.ProjectsListView.as_view(), name='projects-list'),
  path('<uuid:id>/', views.ProjectRUDView.as_view(), name='projects-get'),
]
