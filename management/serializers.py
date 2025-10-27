from rest_framework import serializers
from .models import Patient
from datetime import date
import re

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'fname', 'dob', 'gender', 'pronoun', 'phone', 'emergency_contact', 'ssn',
            'street1', 'street2', 'last_known_address', 'city', 'state', 'zip',
            'medicaid_no', 'id_card', 'insurance', 'race', 'pref_service_area',
            'employed', 'shower', 'hungry', 'homeless',
            'image', 'wait_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'wait_time', 'created_at', 'updated_at']
        extra_kwargs = {
            # Personal Information
            'fname': {'required': True, 'allow_blank': False},
            'dob': {'required': True},
            'gender': {'required': True, 'allow_blank': False},
            'pronoun': {'required': True, 'allow_blank': False},
            'phone': {'required': True, 'allow_blank': False},
            'emergency_contact': {'required': True, 'allow_blank': False},
            'ssn': {'required': True, 'allow_blank': False},
            # Address Information
            'street1': {'required': True, 'allow_blank': False},
            'street2': {'required': False, 'allow_blank': True}, # Street 2 is often optional
            'last_known_address': {'required': True, 'allow_blank': False},
            'city': {'required': True, 'allow_blank': False},
            'state': {'required': True, 'allow_blank': False},
            'zip': {'required': True, 'allow_blank': False},
            # Medical & Other Info
            'medicaid_no': {'required': False, 'allow_blank': True, 'allow_null': True}, # Explicitly optional
            'id_card': {'required': True, 'allow_blank': False},
            'insurance': {'required': True, 'allow_blank': False},
            'race': {'required': True, 'allow_blank': False},
            'pref_service_area': {'required': True, 'allow_blank': False},
            # Status
            'employed': {'required': True, 'allow_blank': False},
            'shower': {'required': True, 'allow_blank': False},
            'hungry': {'required': True, 'allow_blank': False},
            'homeless': {'required': True, 'allow_blank': False},
            # System
            'image': {'required': False},
        }

    def validate_ssn(self, value):
        """
        Validates that the SSN is exactly 10 digits.
        """
        if value:
            # Allow SSN with or without hyphens, but strip them for validation and storage.
            cleaned_value = value.replace('-', '')
            if not re.fullmatch(r'\d{10}', cleaned_value):
                raise serializers.ValidationError("SSN must be a 10-digit number.")
            return cleaned_value
        return value

    def validate_dob(self, value):
        """
        Validates that the date of birth is not in the future.
        """
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_phone(self, value):
        """
        Validates that the phone number is exactly 10 digits.
        """
        if value:
            # Allow phone number with common formatting, but strip non-digits.
            cleaned_value = re.sub(r'\D', '', value)
            if not re.fullmatch(r'\d{10}', cleaned_value):
                raise serializers.ValidationError("Phone number must be a 10-digit number.")
            return cleaned_value
        return value

    def validate_zip(self, value):
        """
        Validates that the ZIP code is 5 digits.
        """
        if value:
            if not re.fullmatch(r'\d{5}', value):
                raise serializers.ValidationError("ZIP code must be a 5-digit number.")
        return value
    def validate_medicaid_no(self, value):
        """
        Validates that the Medicaid number is 10 digits.
        """
        if value:
            cleaned_value = re.sub(r'\D', '', value)
            if not re.fullmatch(r'\d{10}', cleaned_value):
                raise serializers.ValidationError("Medicaid number must be a 12-digit number.")
            return cleaned_value
        return value

    # def validate_state(self, value):
    #     """
    #     Validates that the state is a valid 2-letter US state abbreviation.
    #     """
    #     if value:
    #         # Normalize to uppercase and check against the set of valid abbreviations
    #         if value.upper() not in US_STATES:
    #             raise serializers.ValidationError("Please enter a valid 2-letter US state abbreviation.")
    #         return value.upper()
    #     return value
    
    def validate_image(self, value):
        """
        Validates that the uploaded image is of an acceptable type and size.
        """
        if value:
            valid_mime_types = ['image/jpeg', 'image/png']
            file_mime_type = value.file.content_type
            if file_mime_type not in valid_mime_types:
                raise serializers.ValidationError("Unsupported image type. Only JPEG and PNG are allowed.")
            if value.size > 5 * 1024 * 1024:  # 5 MB limit
                raise serializers.ValidationError("Image size should not exceed 5 MB.")
        return value
    
    def _validate_choice_field(self, value, field_name):
        """Helper to validate a value against a model's choice field."""
        # Get all valid choice keys from the model field
        valid_choices = [choice[0] for choice in self.Meta.model._meta.get_field(field_name).choices]
        if value not in valid_choices:
            # Provide a helpful error message with the available options
            raise serializers.ValidationError(f"Invalid choice. Available options are: {', '.join(valid_choices)}.")
        return value

    def validate_gender(self, value): return self._validate_choice_field(value, 'gender')
    def validate_pronoun(self, value): return self._validate_choice_field(value, 'pronoun')
    def validate_id_card(self, value): return self._validate_choice_field(value, 'id_card')
    def validate_insurance(self, value): return self._validate_choice_field(value, 'insurance')
    def validate_race(self, value): return self._validate_choice_field(value, 'race')
    def validate_pref_service_area(self, value): return self._validate_choice_field(value, 'pref_service_area')
    def validate_employed(self, value): return self._validate_choice_field(value, 'employed')
    def validate_shower(self, value): return self._validate_choice_field(value, 'shower')
    def validate_hungry(self, value): return self._validate_choice_field(value, 'hungry')
    def validate_homeless(self, value): return self._validate_choice_field(value, 'homeless')
