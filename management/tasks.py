from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Patient
from django.conf import settings

@shared_task
def send_patient_checkin_email(patient_id):
    print("Sending detailed email for patient ID:", patient_id)
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return "Patient not found."

    # Prepare patient data as a list of dictionaries for easier template iteration
    patient_display_data = []
    for field in patient._meta.fields:
        patient_display_data.append({
            'label': field.verbose_name,
            'value': getattr(patient, field.name)
        })

    # Handle image URL separately and ensure it's an absolute URL for email clients
    image_url = None
    if patient.image:
        # request object is not available in celery task, so we build the URL manually
        image_url = f"{settings.SITE_DOMAIN}{patient.image.url}"

    context = {
        'patient_display_data': patient_display_data, 
        'image_url': image_url
    }

    html_message = render_to_string('emails/patient_details.html', context)
    
    subject = f"New Patient Check-in: {patient.fname}"
    message = f"A new patient has checked in. Details are attached." 
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = settings.ADMIN_RECIPIENTS 

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message 
    )
    return f"Detailed email sent for patient {patient.fname}"