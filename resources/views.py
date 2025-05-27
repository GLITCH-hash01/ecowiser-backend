from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MediaSerializer, CSVTablesSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import ProjectBelongsToTenant,MediaBelongsToTenant
from .models import Media,CSVTables 
from .tasks import change_visibility_file,delete_media_file
from rest_framework.pagination import PageNumberPagination
from ecowiser import settings

class UploadMediaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data=request.data
        data['uploaded_by'] = request.user.id
        serializer = MediaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class MediaListView(APIView):
    permission_classes = [IsAuthenticated, ProjectBelongsToTenant]

    def get(self, request , project_id):
        name=request.query_params.get('name', None)
        if name:
          resources = Media.objects.filter(project__id=project_id, name__icontains=name).first()
          if not resources:
            return Response({"error": "Resource not found"}, status=404)          
        else:
          resources = Media.objects.filter(project__id=project_id)
        paginator= PageNumberPagination()
        result_page= paginator.paginate_queryset(resources, request)
        serializer = MediaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class MediaSetVisibilityView(APIView):
    permission_classes = [IsAuthenticated,MediaBelongsToTenant]

    def post(self, request, id):
        try:
            resource = Media.objects.get(id=id)
            if resource.project.tenant.id != request.user.tenant.id:
                return Response({"error": "You do not have permission to change visibility of this resource"}, status=403)
            visibility = request.data.get('visibility', None)
            if not visibility:
                return Response({"error": "Visibility not provided"}, status=400)
            if visibility not in ['Public', 'Private']:
                return Response({"error": "Invalid visibility"}, status=400)
            # if visibility == resource.visibility:
            #     return Response({"message": "Visibility is already set to this value"}, status=200)
            resource.visibility = visibility
            url=resource.file_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
            print(url)
            thumb_url=resource.thumb_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
            change_visibility_file.delay(url, visibility)
            change_visibility_file.delay(thumb_url, visibility)
            resource.save()
            serializer = MediaSerializer(resource)
            return Response(serializer.data, status=200)
        except Media.DoesNotExist:
            return Response({"error": "Resource not found"}, status=404)
        
class MediaDetailView(APIView):
    permission_classes = [IsAuthenticated,MediaBelongsToTenant]

    def delete(self, request, id):
        try:
            resource = Media.objects.get(id=id)
            if resource.project.tenant.id != request.user.tenant.id:
                return Response({"error": "You do not have permission to delete this resource"}, status=403)
            if not resource:
                return Response({"error": "Resource not found"}, status=404)
            if resource.file_url:
                url_key = resource.file_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
                delete_media_file.delay(url_key)
            if resource.thumb_url:
                thumb_key = resource.thumb_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/')
                delete_media_file.delay(thumb_key)
            resource.delete()
            return Response({"message": "Resource deleted successfully"}, status=204)
        except Media.DoesNotExist:
            return Response({"error": "Resource not found"}, status=404)
    
    def get(self, request, id):
        try:
            resource = Media.objects.get(id=id)
            if resource.project.tenant.id != request.user.tenant.id:
                return Response({"error": "You do not have permission to view this resource"}, status=403)
            if not resource:
                return Response({"error": "Resource not found"}, status=404)
            serializer = MediaSerializer(resource)
            return Response(serializer.data)
        except Media.DoesNotExist:
            return Response({"error": "Resource not found"}, status=404)
        
class CSVTableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data= request.data.copy()
        data['uploaded_by'] = request.user.id
        if 'project' not in data:
            return Response({"error": "Project ID is required"}, status=400)
        serializer = CSVTablesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request):
        id = request.query_params.get('id', None)
        project_id = request.query_params.get('project_id', None)
        if not project_id:
            return Response({"error": "Project ID is required"}, status=400)
        if id:
            resources = CSVTables.objects.filter(project__id=project_id, id=id).first()
            if not resources:
                return Response({"error": "Resource not found"}, status=404)
            serializer = CSVTablesSerializer(resources)
        else:
            resources = CSVTables.objects.filter(project__id=project_id)
            serializer = CSVTablesSerializer(resources, many=True)
        
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(resources, request)
        serializer = CSVTablesSerializer(result_page, many=True)
        if paginator.get_page_size(request) == 0:
            return Response({"error": "No resources found"}, status=404)
        
        return paginator.get_paginated_response(serializer.data)
    
    def delete(self, request):
        id= request.query_params.get('id', None)
        if not id:
            return Response({"error": "ID is required"}, status=400)
        try:
            resource = CSVTables.objects.get(id=id)
            if resource.project.tenant.id != request.user.tenant.id:
                return Response({"error": "You do not have permission to delete this resource"}, status=403)
            if not resource:
                return Response({"error": "Resource not found"}, status=404)
            delete_media_file.delay(resource.file_url.removeprefix(f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'))
            resource.delete()
            return Response({"message": "Resource deleted successfully"}, status=204)
        except CSVTables.DoesNotExist:
            return Response({"error": "Resource not found"}, status=404)