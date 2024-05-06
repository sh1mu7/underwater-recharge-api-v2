import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.response import Response

from coreapp import roles
from coreapp.models import Document, User
from coreapp.utils import auth_utils, otp_utils

UserModel = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = (
            'first_name', 'last_name', 'dob', 'email', 'mobile', 'password', 'confirm_password',
            'gender'
        )

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': [_("Passwords do not match"), ]})
        return data

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password')
        user = UserModel.objects.create(**validated_data)
        user.set_password(confirm_password)
        user.is_approved = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = auth_utils.get_user_by_email(email)
            auth_utils.validate_user(user)
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist")]})


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        new_password = attrs['password']
        confirm_password = attrs['confirm_password']
        if new_password != confirm_password:
            raise serializers.ValidationError({'confirm_password': [_("Passwords do not match"), ]})
        auth_utils.validate_password(new_password)
        return attrs


class ForgetPassSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = auth_utils.get_user_by_email(email)
            auth_utils.validate_user(user)
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class ForgetPassConfirmSerializer(serializers.Serializer):
    email = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        code = attrs['code']
        try:
            user = auth_utils.get_user_by_email(email)
            if not otp_utils.is_code_valid(user, code):
                raise serializers.ValidationError({'code': [_("Invalid code"), ]})
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class AccountVerifySerializer(serializers.Serializer):
    email = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        code = attrs['code']
        try:
            user = auth_utils.get_user_by_email(email)
            if not otp_utils.is_code_valid(user, code):
                raise serializers.ValidationError({'code': [_("Invalid code"), ]})
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = auth_utils.get_user_by_email(email)
            auth_utils.validate_user(user)
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email': [_(f"User with email {email} does not exist"), ]})


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source='get_image_url', read_only=True)

    class Meta:
        model = UserModel
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'mobile',
            'image',
            'image_url',
            'bio',
        )
        read_only_fields = ('id', 'email', 'mobile')


class DocumentSerializer(serializers.ModelSerializer):
    doc_url = serializers.CharField(read_only=True, source="get_url")

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('owner',)


class UserListSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source='get_image_url', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'dob', 'last_name','gender', 'email', 'mobile', 'role', 'image_url')


class UserCreateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'dob', 'mobile', 'email', 'password', 'confirm_password',
                  'gender', 'role')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': [_("Passwords do not match"), ]})
        return data

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password')
        role = validated_data.pop('role')
        user = User.objects.create(**validated_data)
        if confirm_password != validated_data['password']:
            raise serializers.ValidationError({'detail': (_['Password do not match'])})
        user.set_password(confirm_password)
        if role == roles.UserRoles.USER:
            user.role = roles.UserRoles.USER
            user.is_verified = True
            user.is_approved = True
            user.save()
            return user

        elif role == roles.UserRoles.ADMIN:
            user.role = roles.UserRoles.ADMIN
            user.is_superuser = True
            user.is_verified = True
            user.is_approved = True
            user.is_staff = True
            user.save()
            return user
        else:
            raise serializers.ValidationError({'detail': (_['Specify a valid role'])})


class UserUpdateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'dob', 'mobile', 'email', 'password', 'confirm_password', 'gender', 'role',
            'image'
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)
        role = validated_data.get('role', None)

        # Update user role based on provided role
        if role == roles.UserRoles.USER:
            instance.role = roles.UserRoles.USER
            instance.is_verified = True
            instance.is_approved = True
            instance.is_superuser = False
            instance.is_staff = False
            instance.is_active = True
        elif role == roles.UserRoles.ADMIN:
            instance.role = roles.UserRoles.ADMIN
            instance.is_superuser = True
            instance.is_verified = True
            instance.is_approved = True
            instance.is_staff = True
            instance.is_active = True

        # Set password if provided and matches confirm_password
        if password and confirm_password and password == confirm_password:
            instance.set_password(password)
        elif password or confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
