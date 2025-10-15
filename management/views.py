from .models import AccessToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from djangorestframework_simplejwt.tokens import RefreshToken 


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token_str = request.data.get('token')
        password = request.data.get('password')

        if not token_str or not password:
            return Response({'error': 'Please provide both token and password.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            access_token = AccessToken.objects.get(token=token_str, password=password, is_active=True)
        except AccessToken.DoesNotExist:
            return Response({'error': 'Invalid credentials or inactive token.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken()

        refresh['token_pk'] = access_token.token
        refresh['role'] = access_token.role

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': access_token.role,
            }

        return Response(data, status=status.HTTP_200_OK)
