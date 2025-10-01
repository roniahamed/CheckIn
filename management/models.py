from django.db import models
import random, string

TOKEN_LENGTH = 8 

def generate_token(length=TOKEN_LENGTH):
    while True:
        PossibleToken = string.digits
        token = ''.join(random.choices(PossibleToken, k=length))
        if not AccessToken.objects.filter(key=token).exists():
            return token

class AccessToken(models.Model):
    token = models.CharField(max_length=100, default=generate_token, unique=True)
    role = models.Choices(
        ('staff', 'Staff'),
        ('doctor', 'Doctor'),
        ('display', 'Display')
    )
    role = models.CharField(max_length=20, choices=role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.token