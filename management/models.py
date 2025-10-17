from django.db import models
import random, string
from django.utils import timezone

TOKEN_LENGTH = 8 

def generate_token(length=TOKEN_LENGTH):
    while True:
        PossibleToken = string.digits
        token = ''.join(random.choices(PossibleToken, k=length))
        if not AccessToken.objects.filter(token=token).exists():
            return token

class AccessToken(models.Model):
    token = models.CharField(max_length=100, default=generate_token, unique=True)
    password = models.CharField(max_length=100)
    class Role(models.TextChoices):
        STAFF = 'form', 'Form'
        DOCTOR = 'doctor', 'Doctor'
        QUEUE = 'queue', 'Queue'
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.token
    


class Patient(models.Model):
    # Personal Information
    fname = models.CharField(max_length=255, blank=True, null=True) # Full Name
    dob = models.DateField(blank=True, null=True) # Date of Birth
    gender = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    pronoun = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('he/him', 'He/Him'),
        ('she/her', 'She/Her'),])
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=255, blank=True, null=True)
    ssn = models.CharField(max_length=9, blank=True, null=True) # Social Security Number

    # Address Information
    street1 = models.CharField(max_length=255, blank=True, null=True)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    last_known_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    
    # Medical & Other Info
    medicaid_no = models.CharField(max_length=100, blank=True, null=True)
    id_card = models.CharField(max_length=100, blank=True, null=True, choices=[('yes', 'Yes'), ('no', 'No'),('lost/stolen', 'LOST/STOLEN'),], help_text='Do you have a valid ID card?')
    insurance = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('humana', 'Humana'),
            ('aetna', 'Aetna'),
            ('magellan', 'Magellan'),
            ('anthem', 'Anthem'),
            ('sentara', 'Sentara'),
            ('united', 'United'),
        ]
    )
    race = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Race (e.g., Asian, Black/African American, etc.)',
        choices=[
            ('black_african_american', 'Black/African American'),
            ('caucasian', 'Caucasian'),
            ('hispanic_latino', 'Hispanic/Latino'),
            ('american_indian_or_alaskan_native', 'American Indian or Alaskan Native'),
            ('biracial', 'Biracial'),
            ('asian', 'Asian'),
            ('hawaiian_pacific_islander', 'Hawaiian/Pacific Islander'),
        ]
    )
    pref_service = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('yes', 'YES'),
            ('yes', 'NO'),
            ('lost/stolen', 'LOST/STOLEN'),
        ]
    )
    pref_service_area = models.CharField(max_length=255, blank=True, null=True)
    
    # Status
    employed = models.CharField( max_length=100, default='NO', choices=[('yes', 'Yes'), ('no', 'No'), ('disabled','Disabled')], help_text='Are you employed?', blank=True, null=True)
    shower = models.CharField(default='No', max_length=100, choices=[('yes', 'Yes'), ('no', 'No')], help_text='Do you need a shower?', blank=True, null=True)
    hungry = models.CharField(default='No', max_length=100, choices=[('yes', 'Yes'), ('no', 'No')], help_text='Are you hungry?', blank=True, null=True)
    homeless = models.CharField(default='Yes', max_length=100, choices=[('yes', 'Yes'), ('no', 'No'), ('staying/someone', 'Staying / Someone')], help_text='Are you homeless?', blank=True, null=True)

    # System Fields
    image = models.ImageField(upload_to='patient_images/', blank=True, null=True)
    wait_time = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fname


class QueueEntry(models.Model):
    class Status(models.TextChoices):
        waiting = 'waiting', 'Waiting'
        in_consultation = 'in_consultation', 'In Progress'
        completed = 'completed', 'Completed'

    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='queue_entry')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.waiting)
    check_in_time = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['check_in_time'] 

    def __str__(self):
        return f"{self.patient.fname} - {self.status}"