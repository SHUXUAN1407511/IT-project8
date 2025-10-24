from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from usersystem.models import User


class BearerTokenAuthentication(BaseAuthentication):
    keyword = 'bearer'

    def authenticate(self, request):
        header = request.headers.get('Authorization')
        if not header:
            return None
        parts = header.strip().split(' ', 1)
        if len(parts) != 2 or parts[0].lower() != self.keyword:
            raise AuthenticationFailed('Invalid Authorization header.')
        token = parts[1].strip()
        if not token:
            raise AuthenticationFailed('Missing token.')
        try:
            user = User.objects.get(auth_token=token, status=User.STATUS_ACTIVE)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed('Invalid token.') from exc
        return user, token

