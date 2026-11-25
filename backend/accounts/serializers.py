from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "role",
            "role_display", "business_name", "phone", "address", "is_approved",
        ]
        read_only_fields = ["id", "role", "role_display", "is_approved"]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "business_name", "phone", "address"]

    def create(self, validated_data):
        email = validated_data["email"].lower()
        return User.objects.create_user(
            username=email,
            email=email,
            role=User.Role.WHOLESALER,
            is_approved=True,
            **{key: value for key, value in validated_data.items() if key != "email"},
        )


class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

        from .models import User

        user_record = User.objects.filter(email__iexact=attrs["email"]).first()
        user = authenticate(
            request=self.context.get("request"),
            username=user_record.username if user_record else attrs["email"].lower(),
            password=attrs["password"],
        )
        if not user or not user.is_active:
            raise serializers.ValidationError("Email or password is incorrect.")
        if user.role == User.Role.WHOLESALER and not user.is_approved:
            raise serializers.ValidationError("This wholesaler account is awaiting approval.")
        token = TokenObtainPairSerializer.get_token(user)
        data = {"refresh": str(token), "access": str(token.access_token)}
        data["user"] = UserSerializer(user).data
        return data
