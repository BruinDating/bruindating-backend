from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Profile, Settings
from .serializers import ProfileSerializer, SettingsSerializer
from auth_app.models import UCLAUser


# Create your views here.
@api_view(["GET"])
@permission_classes([AllowAny])
def profile_list(request):
    profiles = Profile.objects.values("user__email", "bio", "major", "year", "interests", "gender", "location")
    return JsonResponse({"profiles": list(profiles)}, safe=False)

@api_view(["GET"])
@permission_classes([AllowAny])  
def debug_user(request):
    user = request.user  

    return JsonResponse({
        "is_authenticated": user.is_authenticated,
        "user": str(user),
        "user_id": getattr(user, "id", "No ID (AnonymousUser)"),
        "user_type": str(type(user)), 
        "headers": dict(request.headers), 
    })


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    queryset = Profile.objects.all()

    def get_queryset(self):
        return Profile.objects.all()

    @action(detail=False, methods=['get'])
    def by_email(self, request):
        """Get profile by email"""
        email = request.query_params.get('email', None)
        if not email:
            return Response(
                {'error': 'Email parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = UCLAUser.objects.get(email=email)
            profile = Profile.objects.get(user=user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UCLAUser.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        print("Received profile creation request with data:", request.data)
        
        # Get or create a user based on the email
        email = request.data.get('email', 'default@ucla.edu')
        user, created = UCLAUser.objects.get_or_create(
            email=email,
            defaults={'username': email.split('@')[0]}
        )
        print(f"User {'created' if created else 'found'}: {user.email}")

        # Check if profile already exists
        existing_profile = Profile.objects.filter(user=user).first()
        if existing_profile:
            print(f"Updating existing profile for {user.email}")
            serializer = self.get_serializer(existing_profile, data=request.data, partial=True)
        else:
            print(f"Creating new profile for {user.email}")
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        
        # Save the profile and associate it with the user
        profile = serializer.save(user=user)
        print(f"Profile saved successfully for {user.email}")
        
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class SettingsViewSet(viewsets.ModelViewSet):
    serializer_class = SettingsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Settings.objects.all() #filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request):
        settings, created = Settings.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def create(self, request):
        settings, created = Settings.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, pk=None):
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

