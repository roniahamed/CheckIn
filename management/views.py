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
from .serializers import PatientSerializer, QueueEntrySerializer
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
            # Save patient and create queue entry
            patient = serializer.save()
            queue_entry = QueueEntry.objects.create(patient=patient)


            # Notify via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'queue_group',
                {
                    'type': 'send.queue.update',
                    'event': 'PATIENT_ADDED',
                    'id': queue_entry.id,
                    'patient': {
                        'id': patient.id,
                        'fname': patient.fname,
                        'status': 'waiting',
                        'image': patient.image.url if patient.image else None,
                    },
                    # Ensure datetimes are serialized as strings for websocket payloads
                    'check_in_time': queue_entry.check_in_time.isoformat() if queue_entry.check_in_time else None,
                }
            )

            # Send email asynchronously
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

        if action == 'call_next':
            try:
                with transaction.atomic():
                    entry = (
                        QueueEntry.objects
                        .select_for_update()
                        .select_related('patient')
                        .filter(status=QueueEntry.Status.WAITING)
                        .first()
                    )
                    if not entry:
                        return Response({'error': 'No patients in the waiting.'}, status=status.HTTP_404_NOT_FOUND)

                    # Complete the queue entry immediately upon call_next
                    now_ts = timezone.now()
                    entry.status = QueueEntry.Status.COMPLETED
                    entry.called_at = now_ts
                    entry.check_out_time = now_ts
                    entry.save(update_fields=['status', 'called_at', 'check_out_time'])

                    # Compute and persist waiting time on Patient (called_at - check_in_time)
                    if entry.check_in_time and entry.called_at:
                        wait_delta = entry.called_at - entry.check_in_time
                        entry.patient.wait_time = wait_delta
                        entry.patient.save(update_fields=['wait_time'])

                    patient_data = {
                        'id': entry.patient.id,
                        'fname': entry.patient.fname,
                        'status': QueueEntry.Status.COMPLETED,
                        'image': entry.patient.image.url if entry.patient.image else None,
                    }
                    event_type = 'PATIENT_COMPLETED'
            except Exception:
                return Response({'error': "Could not process the request. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        queue_entries = QueueEntry.objects.select_related('patient').filter(status=QueueEntry.Status.WAITING)
        serializer = QueueEntrySerializer(queue_entries, many=True)
        return Response(serializer.data)
