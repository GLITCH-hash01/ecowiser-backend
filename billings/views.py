from .models import Invoices
from .serializers import InvoicesSerializer,SubscriptionSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.permissions import IsOwner, IsAdmin
from .tasks import upgrade_tier
from rest_framework.generics import ListAPIView

TIER_ORDER = ['Free', 'Pro', 'Enterprise']

class SubscriptionUpgradeView(APIView):
    permission_classes = [IsAuthenticated, IsOwner | IsAdmin]

    def post(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"error": "Tenant not found"}, status=404)
        
        current_tier = tenant.subscriptions.subscription_tier
        new_tier = request.data.get('subscription_tier', None)
        if not new_tier:
            return Response({"error": "Subscription tier not provided"}, status=400)
        
        if new_tier not in TIER_ORDER:
            return Response({"error": "Invalid subscription tier"}, status=400)

        if TIER_ORDER.index(new_tier) <= TIER_ORDER.index(current_tier):
            return Response({"error": "You can only upgrade to a higher subscription tier"}, status=400)
        
        start= tenant.subscriptions.current_cycle_start_date
        end= tenant.subscriptions.current_cycle_end_date

        if end-start < timezone.timedelta(days=10):
            return Response({"error": "You can only upgrade subscription 10 days before the end of the current cycle"}, status=400)

        upgrade_tier.delay(tenant.id, new_tier)

        return Response({"message": f"Subscription upgraded to {new_tier}"}, status=200)
    
class SubscriptionDowngradeView(APIView):
    permission_classes = [IsAuthenticated, IsOwner | IsAdmin]

    def post(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"error": "Tenant not found"}, status=404)
        
        current_tier = tenant.subscriptions.subscription_tier
        new_tier = request.data.get('subscription_tier', None)
        if not new_tier:
            return Response({"error": "Subscription tier not provided"}, status=400)
        
        if new_tier not in TIER_ORDER:
            return Response({"error": "Invalid subscription tier"}, status=400)

        if TIER_ORDER.index(new_tier) >= TIER_ORDER.index(current_tier):
            return Response({"error": "You can only downgrade to a lower subscription tier"}, status=400)

        tenant.subscriptions.next_subscription_tier = new_tier
        tenant.subscriptions.save()

        return Response({"message": f"Subscription will be downgraded to {new_tier} in the next billing cycle."}, status=200)


class SubscriptionDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsOwner | IsAdmin]

    def get(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"error": "Tenant not found"}, status=404)

        serializer = SubscriptionSerializer(tenant.subscriptions)
        return Response(serializer.data, status=200)

class InvoiceListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsOwner | IsAdmin]
    serializer_class = InvoicesSerializer

    def get_queryset(self):
        tenant = self.request.user.tenant
        if not tenant:
            return Invoices.objects.none()
        return Invoices.objects.filter(tenant=tenant).order_by('-issued_at')