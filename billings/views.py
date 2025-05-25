from django.shortcuts import render
from tenants.models import Tenant
from .models import Billing
from .serializers import BillingsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.permissions import IsMember, IsOwner, IsAdmin
from billings.subscriptions import SubscriptionTiers_Details

TIER_ORDER = ['Free', 'Pro', 'Enterprise']
class UpgradeView(APIView):
    permission_classes=[IsAuthenticated,IsOwner | IsAdmin]
    """
    View to handle tenant upgrade requests.
    """
    def post(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"message": "User does not belong to any tenant"}, status=400)

        new_tier = request.data.get('new_tier')
        if not new_tier:
            return Response({"message": "New subscription tier is required"}, status=400)

        current_tier = tenant.subscription_tier

        if new_tier not in TIER_ORDER:
            return Response({"message": "Invalid subscription tier"}, status=400)
        if new_tier == current_tier:
            return Response({"message": "You are already on this subscription tier"}, status=400)
        if TIER_ORDER.index(new_tier) <= TIER_ORDER.index(current_tier):
            return Response({"message": "You can only upgrade to a higher subscription tier"}, status=400)

        billing = Billing.objects.filter(tenant=tenant).first()
        billing.subscription_end_date = timezone.now()
        billing.save()

        new_tier_billing = BillingsSerializer(data={
            'tenant': tenant.id,
            'subscription_tier': new_tier,
            'price': SubscriptionTiers_Details[new_tier]['price'],
        })
        
        if new_tier_billing.is_valid():
            new_tier_billing.save()
        else:
            return Response(new_tier_billing.errors, status=400)


        return Response({"message": "Tenant upgraded successfully", "new_tier": new_tier}, status=200)

class DowngradingView(APIView):
    permission_classes=[IsAuthenticated,IsOwner | IsAdmin]
    """
    View to handle tenant downgrade requests.
    """
    def post(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"message": "User does not belong to any tenant"}, status=400)

        new_tier = request.data.get('new_tier')
        if not new_tier:
            return Response({"message": "New subscription tier is required"}, status=400)

        current_tier = tenant.subscription_tier

        if new_tier not in TIER_ORDER:
            return Response({"message": "Invalid subscription tier"}, status=400)
        if new_tier == current_tier:
            return Response({"message": "You are already on this subscription tier"}, status=400)
        if TIER_ORDER.index(new_tier) >= TIER_ORDER.index(current_tier):
            return Response({"message": "You can only downgrade to a lower subscription tier"}, status=400)

        billing = Billing.objects.filter(tenant=tenant, subscription_start_date__lt=timezone.now(),subscription_end_date__gt=timezone.now()).first()
        billing.subscription_cancel_date = timezone.now()
        billing.save()

        

        new_tier_billing = BillingsSerializer(data={
            'tenant': tenant.id,
            'subscription_tier': new_tier,
            'subscription_start_date': billing.subscription_end_date,
            'price': SubscriptionTiers_Details[new_tier]['price'],
        })
        
        if new_tier_billing.is_valid():
            new_tier_billing.save()
        else:
            return Response(new_tier_billing.errors, status=400)

        return Response({"message": "Tenant downgraded successfully", "new_tier": new_tier}, status=200)