from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import IsMember, IsAdminorOwner
from .serializers import ProjectSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView,ListAPIView
from .models import Project 
from ecowiser.settings import SUBSCRIPTION_TIERS_DETAILS

class CreateProjectView(APIView):
  permission_classes = [IsAuthenticated, IsAdminorOwner]
  def post(self, request):
    data = request.data
    data['created_by'] = request.user.id

    if request.user.tenant is None:
      return Response({"message": "User does not belong to a tenant"}, status=400)
    else:
      data['tenant'] = request.user.tenant.id

    # Check if the user has reached the project limit for their subscription tier
    current_project_count=request.user.tenant.projects.count()
    subscription_tier_limit= SUBSCRIPTION_TIERS_DETAILS[request.user.tenant.subscriptions.subscription_tier]['projects']
    if subscription_tier_limit is not None:
      if current_project_count >= subscription_tier_limit:
        return Response({"message": "Project limit reached for your subscription tier"}, status=400)

    serializer = ProjectSerializer(data=data)
    if not serializer.is_valid():
      return Response({"message": "Project creation failed", "errors": serializer.errors}, status=400)
    serializer.save()
    data = serializer.data


    response = {
      "message": "Project created successfully",
      "data": data  # This should be replaced with actual project data
    }
    return Response(response, status=201)

class ProjectsListView(ListAPIView):
  permission_classes = [IsAuthenticated, IsMember]
  serializer_class = ProjectSerializer

  def get_queryset(self):
    if self.request.user.tenant is None:
      return Project.objects.none()
    return Project.objects.filter(tenant=self.request.user.tenant)

class ProjectRUDView(RetrieveUpdateDestroyAPIView):
  permission_classes = [IsAuthenticated, IsAdminorOwner]
  queryset = Project.objects.all()
  serializer_class = ProjectSerializer
  lookup_field = 'id'

  def get_object(self):
    obj = super().get_object()
    if obj.tenant != self.request.user.tenant:
      raise PermissionError("You do not have permission to access this project")
    return obj