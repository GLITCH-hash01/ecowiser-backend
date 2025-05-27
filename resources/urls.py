from django.urls import path
from . import views

app_name = 'resources'
urlpatterns = [
    path('upload/', views.UploadMediaView.as_view(), name='upload_media'),
    path('media/<uuid:project_id>/', views.MediaListView.as_view(), name='media_list'),
    path('media/visibility/<int:id>/', views.MediaSetVisibilityView.as_view(), name='media_set_visibility'),
    path('media/<int:id>/', views.MediaDetailView.as_view(), name='media_detail'),
    path('csv/', views.CSVTableView.as_view(), name='upload_csv'),
]