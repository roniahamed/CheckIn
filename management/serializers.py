from rest_framework import serializers
from .models import Patient
from datetime import date
import re


# US state postal abbreviations for basic validation
US_STATE_ABBREVS = {
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA',
    'ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK',
    'OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'
}


class PatientSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    formatted_address = serializers.SerializerMethodField(read_only=True)
    insurance_display = serializers.SerializerMethodField(read_only=True)
    race_display = serializers.SerializerMethodField(read_only=True)
    id_card_display = serializers.SerializerMethodField(read_only=True)
    pronoun_display = serializers.SerializerMethodField(read_only=True)
    pref_service_display = serializers.SerializerMethodField(read_only=True)
    employed_display = serializers.SerializerMethodField(read_only=True)
    shower_display = serializers.SerializerMethodField(read_only=True)
    hungry_display = serializers.SerializerMethodField(read_only=True)
    homeless_display = serializers.SerializerMethodField(read_only=True)

    dob = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Patient
        exclude = ('wait_time',)
        read_only_fields = ('created_at', 'updated_at')

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_formatted_address(self, obj):
        parts = [obj.street1 or '', obj.street2 or '']
        city_state = ', '.join(filter(None, [obj.city, obj.state]))
        if obj.zip:
            city_state = f"{city_state} {obj.zip}".strip()
        if city_state:
            parts.append(city_state)
        return ', '.join([p for p in [p.strip() for p in parts] if p])

    # Choice display getters
    def _get_display(self, obj, field):
        try:
            return getattr(obj, f'get_{field}_display')()
        except Exception:
            return getattr(obj, field)

    def get_insurance_display(self, obj):
        return self._get_display(obj, 'insurance')

    def get_race_display(self, obj):
        return self._get_display(obj, 'race')

    def get_id_card_display(self, obj):
        return self._get_display(obj, 'id_card')

    def get_pronoun_display(self, obj):
        return self._get_display(obj, 'pronoun')

    def get_pref_service_display(self, obj):
        return self._get_display(obj, 'pref_service')

    def _bool_display(self, value):
        if value is None:
            return None
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        # Fallback for non-boolean fields that store choices
        return str(value)

    def get_employed_display(self, obj):
        return self._bool_display(obj.employed)

    def get_shower_display(self, obj):
        return self._bool_display(obj.shower)

    def get_hungry_display(self, obj):
        return self._bool_display(obj.hungry)

    def get_homeless_display(self, obj):
        return self._bool_display(obj.homeless)

    # Validators tailored for US formats
    def validate_ssn(self, value):
        if value in (None, ''):
            return value
        digits = re.sub(r"\D", "", str(value))
        if len(digits) != 9:
            raise serializers.ValidationError('SSN must contain 9 digits.')
        if digits == '000000000':
            raise serializers.ValidationError('Invalid SSN.')
        # Block obviously invalid ranges (basic check)
        if digits.startswith(('000', '666')) or 900 <= int(digits[:3]) <= 999:
            raise serializers.ValidationError('Invalid SSN prefix.')
        return digits

    def validate_phone(self, value):
        if value in (None, ''):
            return value
        digits = re.sub(r"\D", "", str(value))
        # Accept 10-digit (US) or 11-digit starting with '1'
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        if len(digits) != 10:
            raise serializers.ValidationError('Enter a valid US phone number with 10 digits (area code + number).')
        # Basic area code and exchange checks (cannot start with 0 or 1)
        if digits[0] in ('0', '1') or digits[3] in ('0', '1'):
            # Warning: this may reject some valid historical numbers but works for common validation
            raise serializers.ValidationError('Enter a valid US phone number (invalid area or exchange code).')
        # Return standardized format: (XXX) XXX-XXXX
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"

    def validate_zip(self, value):
        if value in (None, ''):
            return value
        v = str(value).strip()
        # Accept 5-digit or 5+4 (12345 or 12345-6789)
        if re.fullmatch(r"\d{5}(-\d{4})?", v):
            return v
        raise serializers.ValidationError('Enter a valid US ZIP code (12345 or 12345-6789).')

    def validate_state(self, value):
        if value in (None, ''):
            return value
        v = str(value).strip().upper()
        if v not in US_STATE_ABBREVS:
            raise serializers.ValidationError('Enter a valid US state postal abbreviation (e.g., NY, CA).')
        return v

    def validate_dob(self, value):
        if value is None:
            return value
        if value > date.today():
            raise serializers.ValidationError('Date of birth cannot be in the future.')
        age = (date.today() - value).days / 365.25
        if age > 120:
            raise serializers.ValidationError('Age seems unrealistic.')
        return value


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ('wait_time', 'created_at', 'updated_at')