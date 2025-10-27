from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Patient

@shared_task
def send_patient_checkin_email(patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return "Patient not found."

    patient_data = {
        'ID': patient.id,
        'Full Name': patient.fname,
        'Date of Birth': patient.dob,
        'Gender': patient.gender,
        'Pronoun': patient.pronoun,
        'Phone': patient.phone,
        'Emergency Contact': patient.emergency_contact,
        'SSN': patient.ssn,
        'Address': f"{patient.street1 or ''} {patient.street2 or ''}, {patient.city or ''}, {patient.state or ''} {patient.zip or ''}",
        'Last Known Address': patient.last_known_address,
        'Medicaid No': patient.medicaid_no,
        'ID Card': patient.id_card,
        'Insurance': patient.insurance,
        'Race': patient.race,
        'Preferred Service Area': patient.pref_service_area,
        'Employed': patient.employed,
        'Shower': patient.shower,
        'Hungry': patient.hungry,
        'Homeless': patient.homeless,
        'Image': patient.image.url if patient.image else None,
        'Created At': patient.created_at,
        'Updated At': patient.updated_at,
    }
    
    html_message = render_to_string('emails/patient_details.html', {'patient': patient_data})
    
    subject = f"New Patient Check-in: {patient.fname}"
    message = f"A new patient has checked in. Details are attached." 
    from_email = 'no-reply@yourdomain.com'  # Use a configured sender email
    recipient_list = ['admin-notifications@yourdomain.com']  # Use a configured recipient list

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message 
    )
    return f"Detailed email sent for patient {patient.fname}"