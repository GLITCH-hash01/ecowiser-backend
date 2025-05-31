from rest_framework.views import  APIView
from rest_framework.response import Response
from .serializers import TenantSerializer
from .models import Tenant
from users.models import User
from users.serializers import UserGetSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsOwner,IsAdminorOwner
from .tasks import get_usage_data, create_subscription_and_invoice
from ecowiser.settings import SUBSCRIPTION_TIERS_DETAILS
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination

# View to handle tenant creation
class TenantsCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if request.user.tenant:
            return Response({"message": "User already belongs to a tenant"}, status=400)
        
        
        serializer = TenantSerializer(data=data)
        if serializer.is_valid():
            tenant = serializer.save()

            request.user.tenant = tenant
            request.user.role = 'Owner'  
            request.user.save()


            subscription_tier = data.get('subscription_tier', 'Free')
            create_subscription_and_invoice.delay(tenant.id, subscription_tier)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# View to handle tenant retrieval, update, and deletion
class TenantsRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = TenantSerializer
    def get_object(self):
        return self.request.user.tenant

# View to manage members of a tenant
class ManageMembersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorOwner]
    
    def post(self, request):
        try:
            tenant = Tenant.objects.get(id=request.user.tenant.id)
        except Tenant.DoesNotExist:
            return Response({"message": "Tenant not found"}, status=404)

        user_email = request.data.get('user_email')
        if not user_email:
            return Response({"message": "User email is required"}, status=400)
        if request.data["role"] not in ['Admin', 'Member', 'Owner']:
            return Response({"message": "Invalid role provided"}, status=400)
        

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)
        if user.tenant:
            return Response({"message": "User already belongs to a tenant"}, status=400)
        user.tenant = tenant
        user.role = request.data.get('role', 'Member')  # Default to 'Member' if not provided
        user.save()

        response = {
            "message": "User added to tenant successfully",
            "user": UserGetSerializer(user).data
        }
        return Response(response, status=200)
    
    def delete(self, request):
        try:
            tenant = Tenant.objects.get(id=request.user.tenant.id)
        except Tenant.DoesNotExist:
            return Response({"message": "Tenant not found"}, status=404)

        user_email = request.data.get('user_email')
        if not user_email:
            return Response({"message": "User email is required"}, status=400)
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)
        if user.tenant != tenant:
            return Response({"message": "User does not belong to this tenant"}, status=400)
        
        if request.user.role == "Admin" and user.role == "Owner":
            return Response({"message": "Cannot remove the owner from the tenant"}, status=400)


        user.tenant = None
        user.role = 'Member'
        user.save()

        response = {
            "message": "User removed from tenant successfully",
            "user": UserGetSerializer(user).data
        }
        return Response(response, status=200)

    def get(self,request):
        try:
            tenant = Tenant.objects.get(id=request.user.tenant.id)
            
        except Tenant.DoesNotExist:
            return Response({"message": "Tenant not found"}, status=404)

        try:
            members = User.objects.filter(tenant=tenant).order_by('role')

            paginator= PageNumberPagination()
            paginator.page_size = 5
            result_page= paginator.paginate_queryset(members, request)
            serializer = UserGetSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status=500)

# View to manage user roles within a tenant
class ManageUsersRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorOwner]
    
    def post(self, request):
        user_email = request.data.get('user_email')
        if not user_email:
            return Response({"message": "User email is required"}, status=400)

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        new_role = request.data.get('role')
        if not new_role or new_role not in ['Admin', 'Member', 'Owner']:
            return Response({"message": "Invalid role provided"}, status=400)

        if new_role == 'Owner' and request.user.role != 'Owner':
            return Response({"message": "Only the owner can promote a user to Owner"}, status=403)

        user.role = new_role
        user.save()

        response = {
            "message": f"User role updated to {new_role} successfully",
            "user": UserGetSerializer(user).data
        }
        return Response(response, status=200)

# View to generate a usage report for the tenant
class GenerateUsageReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorOwner]
    
    def get(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"message": "Tenant not found"}, status=404)

        get_usage_data.delay(tenant.id)

        return Response({"message": "Usage report will be sent to your mail shortly"}, status=200)