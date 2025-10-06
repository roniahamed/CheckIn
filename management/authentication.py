from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from management.models import AccessToken

class Authenticated:

    def __init__(self, token=None):
        self.token = token 
    
    @property
    def is_authenticated(self):
        return True 
    @property
    def is_anonymous(self):
        return False
    
    @property
    def pk(self):
        return self.token.token if self.token else None
    

class TokenAuthentication(BaseAuthentication):
    keyword = 'token'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None 
        
        try:
            keyword, token = auth_header.split()
        except ValueError:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        
        try:
            access_token = AccessToken.objects.get(token=token, is_active=True)
        except AccessToken.DoesNotExist:
            raise AuthenticationFailed('Invalid or inactive token.')

        user = Authenticated(token=access_token)
        return (user, None)
    
    def authenticate_header(self, request):
        return self.keyword
    
