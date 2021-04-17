from base64 import b64encode
from rest_framework import authentication
from api.models import Connection

# https://stackoverflow.com/a/46428523
# https://stackoverflow.com/a/32846841
# https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication
class ConnectionAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')

        for connection in Connection.objects.all():
            user_pwd = connection.incoming_username + ':' + connection.incoming_password
            expected = b64encode(bytes(user_pwd, 'ASCII')).decode()
            if token_type == 'Basic' and credentials == expected:
                return (connection, None)
        return None