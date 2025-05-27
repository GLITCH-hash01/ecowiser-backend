from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from .serializers import UserSerializer
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateDestroyAPIView
from .permissions import AdminOwnerPrivilages



class UsersCreateView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        print("Routes is working")
        data = request.data
        if 'password' not in data or not data['password']:
            return Response({"message": "Password is required"}, status=400)
        try:
            validate_password(data['password'])
        except Exception as e:
            return Response({"message": "Password validation failed", "errors": str(e)}, status=400)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "User created successfully",
                "user": serializer.data
            }
            return Response(response, status=201)
        response = {
            "message": "User creation failed",
            "errors": serializer.errors
        }
        return Response(response, status=400)
    

class UsersRView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,AdminOwnerPrivilages]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


class SelfRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user