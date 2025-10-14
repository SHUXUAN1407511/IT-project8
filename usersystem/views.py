from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from .models import User
from .serializer import UserSerializer

def success(data=None, msg="success", status=200):
    return Response({
        "user": data or {},
        "meta": {"status": status,
                 "message": msg}
    })

def fail(msg="bad request", status=400, data=None):
    return Response({
        "data": data or {},
        "meta": {"status": status,
                 "message": msg}
    })

class RegisterView(APIView):
    """
    POST /api/register
    body: { "username": "abcxyz", "password": "123456","role": "admin" }
    """
    def post(self, request):
        ser = UserSerializer(data=request.data)
        if not ser.is_valid():
            return fail(msg="validation error", status=400, data=ser.errors)

        username = ser.validated_data["username"]
        if User.objects.filter(username=username).exists():
            return fail(msg="username already exists", status=400)

        user = ser.save()
        return success(data={"id": user.id, "username": user.username,"role":user.role}, msg="registered", status=200)

class LoginView(APIView):
    """
    POST /api/login
    body: { "username": "abcxyz", "password": "123456" }
    """
    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "")

        if not username or not password:
            return Response({"message": "username and password required"}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"message": "username or password incorrect"}, status=401)

        if not check_password(password, user.password):
            return Response({"message": "username or password incorrect"}, status=401)

        user_profile = {
            "id": user.id,
            "username": user.username,
            "name": getattr(user, "name", user.username),
            "role": getattr(user, "role", None),
            "status": getattr(user, "status", "active"),
        }

        if not user_profile["role"]:
            return Response({"message": "role missing, login failed"}, status=403)

        return Response({
            "token": None,
            "user": user_profile,
            "message": "login success"
        }, status=200)