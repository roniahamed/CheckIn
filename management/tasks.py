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
        'Phone': patient.phone,
        'SSN': patient.ssn,
        'Address': f"{patient.street1}, {patient.city}, {patient.state} {patient.zip}",
        'Medicaid No': patient.medicaid_no,
        'Insurance': patient.insurance,
        'Race': patient.race,
        
    }
    
    # একটি HTML টেমপ্লেট ব্যবহার করে ইমেইলের বডি তৈরি করুন
    # এটি সাধারণ টেক্সটের চেয়ে অনেক বেশি প্রফেশনাল দেখাবে
    html_message = render_to_string('emails/patient_details.html', {'patient': patient_data})
    
    subject = f"New Patient Check-in: {patient.fname}"
    message = f"A new patient has checked in. Details are attached." # Plain text fallback
    from_email = 'your_email@gmail.com'
    recipient_list = ['admin_email@example.com'] # অ্যাডমিনের ইমেইল

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message # HTML কন্টেন্ট যোগ করুন
    )
    return f"Detailed email sent for patient {patient.fname}"