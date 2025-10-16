from .models import AccessToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken 
from .permissions import IsFormManager, IsDoctor, IsQueueManager
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Patient, QueueEntry
from .serializers import PatientSerializer
from .tasks import send_patient_checkin_email


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

        refresh['token_pk'] = access_token.pk
        refresh['role'] = access_token.role

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': access_token.role,
            }

        return Response(data, status=status.HTTP_200_OK)


# View for form patient management
class FormPatientView(APIView):
    permission_classes = [IsFormManager]

    def post(self, request, *args, **kwargs):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()

            QueueEntry.objects.create(patient=patient)

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                'queue_group',
                {
                    'type': 'send.queue.update',
                    'event': 'PATIENT_ADDED',
                    'patient': {
                        'id': patient.id,
                        'name':patient.fname,
                        'status': 'WAITING',

                    }
                }
            )
            send_patient_checkin_email.delay(patient.id)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def get(self, request):
        # Logic for form patient management
        return Response({'message': f'Welcome Form User (Token: {request.user.token})! You can access the patient form.'})

# View for doctor patient management
class DoctorPatientView(APIView):
    permission_classes = [IsDoctor]

    def get(self, request):
        # Logic for doctor patient management
        return Response({'message': f'Welcome Doctor (Token: {request.user.token})! You can access the doctor patient management.'})


# View for queue management
class QueueManagementView(APIView):
    permission_classes = [IsQueueManager]

    def get(self, request):
        # Logic for queue management
        return Response({'message': f'Welcome Queue Manager (Token: {request.user.token})! You can access the queue management.'})
