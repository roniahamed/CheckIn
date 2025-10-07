from django.db import models
import random, string

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
        STAFF = 'staff', 'Staff'
        DOCTOR = 'doctor', 'Doctor'
        QUEUE = 'queue', 'Queue'
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.token