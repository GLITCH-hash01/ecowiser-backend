from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password

class TenantSerializer(serializers.Serializer):
    name= serializers.CharField(max_length=100)

class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, required=False, allow_blank=False)
  current_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
  tenant= TenantSerializer(read_only=True)
  class Meta:
    model = User
    fields = ['id', 'username','password', 'email','current_password', 'first_name', 'last_name', 'role','tenant']
    read_only_fields = ['id']

  def create(self, validated_data):
      validated_data.pop('current_password', None)  # Remove current_password if it exists
      user = User(**validated_data)
      user.set_password(validated_data['password'])
      user.save()
      return user

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