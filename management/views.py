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
from django.db import transaction

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
            # Use select_related for related objects if PatientSerializer creates related objects
            patient = serializer.save()

            # No related objects to select here, but if you query for patient later, use select_related
            QueueEntry.objects.create(patient=patient)

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                'queue_group',
                {
                    'type': 'send.queue.update',
                    'event': 'PATIENT_ADDED',
                    'patient': {
                        'id': patient.id,
                        'name': patient.fname,
                        'status': 'waiting',
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

    def post(self, request, *args, **kwargs):
        action = request.data.get('action')
        patient_id = request.data.get('patient_id')

        if action == 'call_next':
            try:
                with transaction.atomic():
                    entry = QueueEntry.objects.select_for_update().select_related('patient').filter(status='waiting').first()
                    if not entry:
                        return Response({'error': 'No patients in the waiting.'}, status=status.HTTP_404_NOT_FOUND)

                    entry.status = 'in_consultation'
                    entry.called_at = timezone.now()
                    entry.save()

                    patient_data = { 'id': entry.patient.id, 'name': entry.patient.fname, 'status': 'in_consultation' }
                    event_type = 'PATIENT_CALLED'
            except Exception as e:
                return Response({'error': "Could not process the request. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif action == 'complete':
            try:
                entry = QueueEntry.objects.select_related('patient').get(patient_id=patient_id, status=QueueEntry.Status.in_consultation)
            except QueueEntry.DoesNotExist:
                return Response({'error': 'Patient is not currently in progress.'}, status=status.HTTP_400_BAD_REQUEST)

            entry.status = QueueEntry.Status.completed
            entry.check_out_time = timezone.now()
            entry.save()

            patient = entry.patient
            wait_time = entry.check_out_time - entry.check_in_time
            patient.wait_time = wait_time
            patient.save()

            patient_data = { 'id': patient.id, 'name': patient.fname, 'status': 'completed' }
            event_type = 'PATIENT_COMPLETED'
        else:
            return Response({'error': 'Invalid action or missing patient.'}, status=status.HTTP_400_BAD_REQUEST)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'queue_group',
            {
                'type': 'send.queue.update',
                'event': event_type,
                'patient': patient_data
            }
        )

        return Response({'message': 'Action successful.', 'patient': patient_data})

    def get(self, request):
        return Response({'message': f'Welcome Doctor (Token: {request.user.token})! You can access the doctor patient management.'})


# View for queue management
class QueueManagementView(APIView):
    # permission_classes = [IsQueueManager]

    def get(self, request):
        queue_entries = QueueEntry.objects.select_related('patient').exclude(status=QueueEntry.Status.completed)

        data = [
            {
                'id': entry.patient.id,
                'name': entry.patient.fname,
                'status': entry.status,
                'check_in_time': entry.check_in_time,
            }
            for entry in queue_entries  
        ]
        return Response(data)
