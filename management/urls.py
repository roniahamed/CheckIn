from django.urls import path
from .views import FormPatientView, DoctorPatientView, QueueManagementView, LoginView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('patients/', FormPatientView.as_view(), name='patient-list'),
    path('doctors/', DoctorPatientView.as_view(), name='doctor-list'),
    path('queue/', QueueManagementView.as_view(), name='queue-list'),
]   