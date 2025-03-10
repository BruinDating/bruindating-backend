from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
import requests
import google_auth_oauthlib.flow
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

UCLA_EMAIL_DOMAINS = ["@ucla.edu", "@g.ucla.edu"]


@csrf_exempt
@api_view(["POST"])
def google_login(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_CLIENT_SECRETS_FILE,
        scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"],
    )

    redirect_uri = f"{settings.BACKEND_URL}/auth/callback"
    flow.redirect_uri = redirect_uri

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account",
    )

    request.session["oauth_state"] = state

    return JsonResponse({"auth_url": authorization_url})


@csrf_exempt
def google_callback(request):
    if "error" in request.GET:
        return JsonResponse({"error": request.GET.get("error")}, status=400)

    code = request.GET.get("code")
    state = request.GET.get("state")

    stored_state = request.session.get("oauth_state")
    if not stored_state or state != stored_state:
        return JsonResponse({"error": "Invalid state parameter"}, status=400)

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_CLIENT_SECRETS_FILE,
        scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"],
        state=state,
    )

    redirect_uri = f"{settings.BACKEND_URL}/auth/callback"
    flow.redirect_uri = redirect_uri

    flow.fetch_token(code=code)

    credentials = flow.credentials

    userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {credentials.token}"}

    userinfo_response = requests.get(userinfo_endpoint, headers=headers)

    if userinfo_response.status_code != 200:
        return JsonResponse({"error": "Failed to obtain user info"}, status=400)

    user_data = userinfo_response.json()

    email = user_data.get("email", "")
    is_ucla_email = any(domain in email for domain in UCLA_EMAIL_DOMAINS)

    if not is_ucla_email:
        return JsonResponse({"error": "You must use a UCLA email address to sign in", "provided_email": email}, status=403)

    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(email=email)
        user.google_id = user_data.get("sub")
        user.profile_picture = user_data.get("picture")
        user.is_ucla_verified = True
        user.save()
    except User.DoesNotExist:
        username = email.split("@")[0]

        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=user_data.get("given_name", ""),
            last_name=user_data.get("family_name", ""),
            google_id=user_data.get("sub"),
            profile_picture=user_data.get("picture"),
            is_ucla_verified=True,
        )

    refresh = RefreshToken.for_user(user)
    tokens = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

    login(request, user)

    frontend_url = settings.FRONTEND_URL
    return redirect(f"{frontend_url}/auth/callback?access_token={tokens['access']}&refresh_token={tokens['refresh']}&username={user.username}")


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": user.profile_picture,
            "is_ucla_verified": user.is_ucla_verified,
        }
    )


@api_view(["POST"])
def token_refresh(request):
    from rest_framework_simplejwt.views import TokenRefreshView

    return TokenRefreshView.as_view()(request)
