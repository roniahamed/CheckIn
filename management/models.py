from django.db import models
import random, string
from django.contrib.auth.hashers import make_password, check_password
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
    password = models.CharField(max_length=128)  # Increased length for hashed password
    # name = models.CharField(max_length=255)
    class Role(models.TextChoices):
        STAFF = 'form', 'Form'
        DOCTOR = 'doctor', 'Doctor'
        QUEUE = 'queue', 'Queue'
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


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
    phone = models.CharField(max_length=10, blank=True, null=True)
    emergency_contact = models.CharField(max_length=255, blank=True, null=True)
    ssn = models.CharField(max_length=10, blank=True, null=True) # Social Security Number

    # Address Information
    street1 = models.CharField(max_length=255, blank=True, null=True)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    last_known_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    
    # Medical & Other Info
    medicaid_no = models.CharField(max_length=12, blank=True, null=True)
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
            ('other', 'Other'),
        ]
    )
    # pref_service = models.CharField(
    #     max_length=255,
    #     blank=True,
    #     null=True,
    #     choices=[
    #         ('yes', 'YES'),
    #         ('yes', 'NO'),
    #         ('lost/stolen', 'LOST/STOLEN'),
    #     ]
    # )

    pref_service_area = models.CharField(max_length=255, blank=True, null=True, help_text='Preferred Service Area', choices=[
        ('east_end', 'East End'),
        ('west_end', 'West End'),
        ('chesterfield', 'Chesterfield'),
        ('chester', 'Chester'),
        ('colonial_heights', 'Colonial Heights'),
        ('north_side_richmond', 'North side Richmond'),
        ('southside_richmond', 'Southside Richmond'),
        ('church_hill', 'Church Hill'),
        ('ashland', 'Ashland'),
        ('hopewell', 'Hopewell'),
        ])
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
        return self.fname or "Unnamed Patient"


class QueueEntry(models.Model):
    class Status(models.TextChoices):
        WAITING = 'waiting', 'Waiting'
        IN_CONSULTATION = 'in_consultation', 'In Consultation'
        COMPLETED = 'completed', 'Completed'

    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='queue_entry')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    check_in_time = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['check_in_time'] 

    def __str__(self):
        return f"{self.patient.fname} - {self.status}"


class AdminGmailList(models.Model):
    """Admin-editable singleton list of notification emails.

    Database-level singleton enforced via a unique constant key.
    Use AdminGmailList.get_admin_recipients() to obtain the emails.
    """
    # Enforce one row at DB level: all rows would have value 1, unique constraint prevents duplicates
    singleton_key = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)

    admin_recipients = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated list of recipient email addresses for admin notifications.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Gmail List"
        verbose_name_plural = "Admin Gmail List"

    def __str__(self):
        return "Admin Gmail List"

    def recipients_list(self):
        return [e.strip() for e in self.admin_recipients.split(',') if e.strip()]

    @classmethod
    def get_current(cls):
        """Return the most recently updated record with non-empty recipients, else any record, or create one."""
        obj = (
            cls.objects
            .exclude(admin_recipients__isnull=True)
            .exclude(admin_recipients__exact="")
            .order_by('-updated_at', '-id')
            .first()
        )
        if obj is None:
            obj = cls.objects.order_by('-updated_at', '-id').first()
        if obj is None:
            obj = cls.objects.create()
        return obj

    @classmethod
    def get_admin_recipients(cls):
        from django.conf import settings as django_settings

        try:
            obj = cls.get_current()
            recipients = obj.recipients_list()
        except Exception:
            recipients = []

        if not recipients:
            recipients = getattr(django_settings, "ADMIN_RECIPIENTS", [])
        return recipients