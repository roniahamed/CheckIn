from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken 
from django.contrib.auth.models import User
from management.models import AccessToken


class CustomJWTAuthentication(JWTAuthentication):

    def get_header(self, request):

        header = request.headers.get('Roni-Authorization')
        if header is None:
            return None
        return header
    
    def get_user(self, validated_token):

        try:
            token_pk = validated_token['token_pk']
            user = AccessToken.objects.get(pk=token_pk, is_active=True)
            return user 
        except AccessToken.DoesNotExist:
            raise AuthenticationFailed('User not found or inactive.', code='user_not_found')
        except KeyError:
            raise InvalidToken('Token is missing required claims (e.g., token_pk).')
        


