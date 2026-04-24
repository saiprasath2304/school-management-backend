from rest_framework import serializers
from .models import School


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model  = School
        fields = [
            "id", "name", "subdomain", "address", "phone", "email",
            "website", "logo", "tagline", "country", "currency", "timezone",
            "plan", "is_active", "trial_ends_at", "created_at",
        ]
        read_only_fields = ["created_at", "plan", "is_active"]


class SchoolRegisterSerializer(serializers.ModelSerializer):
    """Used for onboarding a new school + its first admin user."""
    admin_first_name = serializers.CharField(write_only=True)
    admin_last_name  = serializers.CharField(write_only=True)
    admin_email      = serializers.EmailField(write_only=True)
    admin_password   = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = School
        fields = [
            "name", "subdomain", "address", "phone", "email",
            "country", "currency", "timezone",
            "admin_first_name", "admin_last_name", "admin_email", "admin_password",
        ]

    def validate_subdomain(self, value):
        if School.objects.filter(subdomain=value).exists():
            raise serializers.ValidationError("This subdomain is already taken.")
        return value

    def create(self, validated_data):
        from accounts.models import User
        from datetime import date, timedelta

        admin_data = {
            "first_name": validated_data.pop("admin_first_name"),
            "last_name":  validated_data.pop("admin_last_name"),
            "email":      validated_data.pop("admin_email"),
            "password":   validated_data.pop("admin_password"),
        }

        school = School.objects.create(**validated_data)
        school.trial_ends_at = date.today() + timedelta(days=30)
        school.save()

        # Create the school's first admin user
        user = User(
            username=f"admin_{school.subdomain}",
            email=admin_data["email"],
            first_name=admin_data["first_name"],
            last_name=admin_data["last_name"],
            role="school_admin",
            is_staff=False,
            school=school,
        )
        user.set_password(admin_data["password"])
        user.save()

        return school
