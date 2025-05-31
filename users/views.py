from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from .serializers import UserSerializer, UserSignupSerializer,UserGetSerializer
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateDestroyAPIView
from .permissions import AdminOwnerPrivilages
import time
from django.db import IntegrityError

# View to handle user creation
class UsersCreateView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        data = request.data
        password = data.get("password")
        if not password:
            return Response({"message": "Password is required"}, status=400)

        try:
            validate_password(password)
        except Exception as e:
            return Response({"message": "Password validation failed", "errors": str(e)}, status=400)

        serializer = UserSignupSerializer(data=data)
        start = time.time()
        if serializer.is_valid():
            print("Validation time:", time.time() - start)
            try:
                start = time.time()
                user = serializer.save()
                print("Save time:", time.time() - start)
            except IntegrityError:
                return Response({"error": "A user with this email already exists."}, status=400)

            return Response({
                "message": "User created successfully",
                "user": user.id
            }, status=201)

        return Response({
            "message": "User creation failed",
            "errors": serializer.errors
        }, status=400)

# View to handle user retrieval
class UsersRView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,AdminOwnerPrivilages]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

# View to handle user retrieval, update, and deletion for self
class SelfRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = UserGetSerializer
    def get_object(self):
        return self.request.user