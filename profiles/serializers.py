from rest_framework import serializers
from .models import Profile, Settings


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'email',
            'name',
            'age',
            'gender',
            'major',
            'profile_picture',
            'hobbies'
        ]
        read_only_fields = ['id', 'email']

    def to_representation(self, instance):
        # Get the basic representation
        data = super().to_representation(instance)
        
        # If profile_picture is not None, ensure it's a full URL
        if data['profile_picture']:
            if not data['profile_picture'].startswith('http'):
                request = self.context.get('request')
                if request:
                    data['profile_picture'] = request.build_absolute_uri(data['profile_picture'])
        
        return data


class SettingsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = Settings
        fields = [
            "id",
            "email",
            "name",
            "email_notifications",
            "match_notifications",
            "message_notifications",
            "profile_visibility",
            "show_online_status",
            "max_distance",
            "age_min",
            "age_max",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
