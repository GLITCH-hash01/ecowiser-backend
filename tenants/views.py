from rest_framework.views import  APIView
from rest_framework.response import Response
from .serializers import TenantSerializer
from .models import Tenant
from users.models import User
from users.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsMember,IsOwner,IsAdminorOwner
from billings.serializers import SubscriptionSerializer,InvoicesSerializer
from django.db import transaction
from rest_framework.serializers import ValidationError
from .tasks import get_usage_data
from billings.tasks import mail_invoice
from ecowiser.settings import SUBSCRIPTION_TIERS_DETAILS
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination


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

class TenantsRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = TenantSerializer
    def get_object(self):
        return self.request.user.tenant

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
        if user.tenant != tenant:
            return Response({"message": "User does not belong to this tenant"}, status=400)
        
        if request.user.role == "Admin" and user.role == "Owner":
            return Response({"message": "Cannot remove the owner from the tenant"}, status=400)


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

        members = User.objects.filter(tenant=tenant).order_by('role')

        paginator= PageNumberPagination()
        paginator.page_size = 5
        result_page= paginator.paginate_queryset(members, request)
        serializer = UserSerializer(result_page, many=True)
      
        return paginator.get_paginated_response(serializer.data)


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