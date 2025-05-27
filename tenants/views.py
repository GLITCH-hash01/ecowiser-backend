from django.shortcuts import render
from rest_framework.views import  APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializers import TenantSerializer
from .models import Tenant
from users.models import User
from users.serializers import UserSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsMember,IsOwner,IsAdminorOwner
from billings.models import Subscription, Invoices
from billings.serializers import SubscriptionSerializer,InvoicesSerializer
from django.db import transaction
from django.utils import timezone
from rest_framework.serializers import ValidationError
from .tasks import get_usage_data
from billings.tasks import mail_invoice
from ecowiser.settings import SUBSCRIPTION_TIERS_DETAILS
# Create your views here
class TenantsListView(ListAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

class TenantsCreateView(APIView):
    permission_classes = [IsAuthenticated, IsMember]

    def post(self, request):
        data = request.data
        if request.user.tenant:
            return Response({"message": "User already belongs to a tenant"}, status=400)
        subscription_tier = data.get('subscription_tier', 'Free')
        
        try:
            with transaction.atomic():
                # Creating the Tenant
                serializer = TenantSerializer(data=data)
                if serializer.is_valid():
                    tenant = serializer.save()
                else:
                    print(serializer.errors)
                    response={
                        "message": "Tenant creation failed",
                    }
                    raise ValidationError(response, status=400)
                
                # Creating the Billing record
                subscription=SubscriptionSerializer(
                    data={
                        "tenant": tenant.id,
                        "subscription_tier": subscription_tier,
                        "next_subscription_tier": subscription_tier,
                    }
                )
                if subscription.is_valid():
                    subscription.save()
                else: 
                    response={
                        "message": "Subscription record creation failed",
                    }
                    raise ValidationError(response)
                invoice=InvoicesSerializer(
                    data={
                        "tenant": tenant.id,
                        "subscription_id": subscription.instance.id,
                        "amount":SUBSCRIPTION_TIERS_DETAILS[subscription_tier]['price'],
                        "billing_start_date": subscription.instance.current_cycle_start_date,
                        "billing_end_date": subscription.instance.current_cycle_end_date
                    })
                if invoice.is_valid():
                    invoice.save()
                    mail_invoice.delay(
                        tenant_id=tenant.id, 
                        invoice_id=invoice.instance.invoice_id
                    )
                else:
                    response={
                        "message": "Invoice record creation failed",
                    }
                    raise ValidationError(response)

                # Assigning the tenant to the user
                request.user.tenant = tenant
                request.user.role = 'Owner'
                request.user.save()
                response={
                    "message": "Tenant created successfully",
                    "tenant": serializer.data
                }
                response['tenant']['subscription_tier'] = subscription_tier
                return Response(response, status=201)
        except Exception as e:
            print(f"Error occurred: {e}")
            response={
                "message": "Tenant creation failed",
                "errors": serializer.errors
            }
            return Response(response, status=400)

class TenantsRUDView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    def get(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"message": "Tenant not found"}, status=404)

        serializer = TenantSerializer(tenant)
        response = {
            "message": "Tenant retrieved successfully",
            "tenant": serializer.data
        }
        return Response(response, status=200)
    
    def put(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"message": "Tenant not found"}, status=404)

        serializer = TenantSerializer(tenant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "Tenant updated successfully",
                "tenant": serializer.data
            }
            return Response(response, status=200)

        response = {
            "message": "Tenant update failed",
            "errors": serializer.errors
        }
        return Response(response, status=400)

    def delete(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({"message": "Tenant not found"}, status=404)

        tenant.delete()
        response = {
            "message": "Tenant deleted successfully"
        }
        return Response(response, status=204)

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

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)
        if user.tenant:
            return Response({"message": "User already belongs to a tenant"}, status=400)
        user.tenant = tenant
        user.role = 'Member'
        user.save()

        response = {
            "message": "User added to tenant successfully",
            "user": UserSerializer(user).data
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
        
        if request.user.role == "Admin" and user.role == "Owner":
            return Response({"message": "Cannot remove the owner from the tenant"}, status=400)

        if user.tenant != tenant:
            return Response({"message": "User does not belong to this tenant"}, status=400)

        user.tenant = None
        user.role = 'Member'
        user.save()

        response = {
            "message": "User removed from tenant successfully",
            "user": UserSerializer(user).data
        }
        return Response(response, status=200)

    # Todo: Need pagination
    def get(self,request):
        try:
            tenant = Tenant.objects.get(id=request.user.tenant.id)
        except Tenant.DoesNotExist:
            return Response({"message": "Tenant not found"}, status=404)

        members = User.objects.filter(tenant=tenant)
        serializer = UserSerializer(members, many=True)
        response = {
            "message": "Members retrieved successfully",
            "members": serializer.data
        }
        return Response(response, status=200)
    
class RoleToAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorOwner]
    
    def post(self, request):
        user_email = request.data.get('user_email')
        if not user_email:
            return Response({"message": "User email is required"}, status=400)

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        if user.role == 'Admin':
            return Response({"message": "User is already an admin"}, status=400)

        user.role = 'Admin'
        user.save()

        response = {
            "message": "User promoted to Admin successfully",
            "user": UserSerializer(user).data
        }
        return Response(response, status=200)

class RoleToMemberView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorOwner]
    
    def post(self, request):
        user_email = request.data.get('user_email')
        if not user_email:
            return Response({"message": "User email is required"}, status=400)

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        if user.role == 'Member':
            return Response({"message": "User is already a member"}, status=400)

        user.role = 'Member'
        user.save()

        response = {
            "message": "User demoted to Member successfully",
            "user": UserSerializer(user).data
        }
        return Response(response, status=200)

class RoleToOwnerView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorOwner]
    
    def post(self, request):
        user_email = request.data.get('user_email')
        if not user_email:
            return Response({"message": "User email is required"}, status=400)

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        if user.role == 'Owner':
            return Response({"message": "User is already an owner"}, status=400)

        if request.user.role != 'Owner':
            return Response({"message": "Only the owner can promote a user to Owner"}, status=403)

        user.role = 'Owner'
        user.save()

        response = {
            "message": "User promoted to Owner successfully",
            "user": UserSerializer(user).data
        }
        return Response(response, status=200)

class GenerateUsageReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorOwner]
    
    def get(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"message": "Tenant not found"}, status=404)

        get_usage_data.delay(tenant.id)

        return Response({"message": "Usage report will be sent to your mail shortly"}, status=200)