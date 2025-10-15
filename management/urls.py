from django.urls import path
from .views import PatientView, DoctorView, QueueView, LoginView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('patients/', PatientView.as_view(), name='patient-list'),
    path('doctors/', DoctorView.as_view(), name='doctor-list'),
    path('queue/', QueueView.as_view(), name='queue-list'),
]   