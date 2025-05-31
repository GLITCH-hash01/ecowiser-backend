from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password

class TenantSerializer(serializers.Serializer):
    id=serializers.UUIDField()
    name= serializers.CharField(max_length=100)

class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[('Owner', 'Owner'), ('Admin', 'Admin'), ('Member', 'Member')], default='Member')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'Member')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, required=False, allow_blank=False)
  
  class Meta:
    model = User
    fields = ['id', 'username','password', 'email','current_password', 'first_name', 'last_name', 'role','tenant']
    read_only_fields = ['id']

  def update(self, instance, validated_data):
      if 'email' in validated_data:
        raise serializers.ValidationError({"email": "Changing email is not allowed."})
      password = validated_data.pop('password', None)
      current_password = validated_data.pop('current_password', None)
      if password:
        if not current_password:
           raise serializers.ValidationError({"current_password": "Current password is required to change the password."})
        if not instance.check_password(current_password):
           raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        try:
            validate_password(password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        instance.set_password(password)
  

      for attr,value in validated_data.items():
        setattr(instance, attr, value)

      instance.save()
      return instance

class UserGetSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'tenant']

