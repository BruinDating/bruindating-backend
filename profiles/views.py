from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Profile, Settings
from .serializers import ProfileSerializer, SettingsSerializer
from rest_framework.decorators import action

# Create your views here.

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]  # Temporarily allow all access
    queryset = Profile.objects.all()  # Return all profiles

    def get_queryset(self):
        # If you want to filter by anything, do it here
        # For now, return all profiles
        print("Getting all profiles...")
        return Profile.objects.all()

    def perform_create(self, serializer):
        print("Creating profile...")
        # No longer require user
        serializer.save()

    def list(self, request):
        print("Listing all profiles...")
        # Return all profiles
        profiles = self.get_queryset()
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)

    def create(self, request):
        print("Creating profile with data:", request.data)
        # Directly create new Profile (no user binding)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        print("Updating profile with data:", request.data)
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SettingsViewSet(viewsets.ModelViewSet):
    serializer_class = SettingsSerializer
    permission_classes = [permissions.AllowAny]  # 允许所有人访问
    queryset = Settings.objects.all()  # 返回所有设置

    def get_queryset(self):
        print("Getting all settings...")
        # 如果提供了user_id参数，则根据用户ID过滤
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            return Settings.objects.filter(user_id=user_id)
        # 否则返回所有设置记录
        return Settings.objects.all()

    def perform_create(self, serializer):
        print("Creating settings...")
        # No longer require user
        serializer.save()

    def list(self, request):
        print("Listing all settings...")
        # Return all settings
        settings = self.get_queryset()
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)

    def create(self, request):
        print("Creating settings with data:", request.data)
        # 允许创建无用户关联的设置
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        print("Updating settings with data:", request.data)
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'])
    def user_settings(self, request):
        """获取或创建指定用户的设置"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "需要提供user_id参数"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 尝试获取用户的设置
        try:
            settings = Settings.objects.get(user_id=user_id)
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        except Settings.DoesNotExist:
            # 如果设置不存在，创建新的设置
            if request.method == 'POST':
                data = request.data.copy()
                data['user'] = user_id
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # GET请求但没有找到设置，返回404
                return Response({"error": "未找到该用户的设置"}, status=status.HTTP_404_NOT_FOUND)
