from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import AccessToken, Patient, QueueEntry, AdminGmailList
from unfold.admin import ModelAdmin
from .tasks import send_patient_checkin_email

# Dynamic filters that show only values present in data for choice fields
from django.contrib import admin as dj_admin

class DynamicChoicesFilter(dj_admin.SimpleListFilter):
    """
    Base class for filters that show only values that exist in the database.
    - Shows only unique values (no duplicates)
    - Hides filter if no data exists
    - When other filters are applied, shows only relevant values
    """
    title = ''
    parameter_name = ''
    field_name = ''

    def lookups(self, request, model_admin):
        # Get the base queryset (respects other filters in changelist)
        qs = model_admin.get_queryset(request)
        
        # Apply all OTHER active filters (not this one)
        # This ensures we only show values that exist given current filter state
        for key, value in request.GET.items():
            if key != self.parameter_name and key != 'o':  # 'o' is ordering
                try:
                    qs = qs.filter(**{key: value})
                except Exception:
                    pass
        
        # Get field choices mapping
        field = model_admin.model._meta.get_field(self.field_name)
        choice_map = dict(field.choices) if field.choices else {}
        
        # Get distinct values that actually exist in filtered queryset
        values = (
            qs.values_list(self.field_name, flat=True)
              .distinct()
              .order_by(self.field_name)
        )
        
        # Build result list
        result = []
        for val in values:
            # Skip None/empty values
            if val in (None, ''):
                continue
            # Use choice label if available, otherwise use value
            label = choice_map.get(val, str(val))
            result.append((val, label))
        
        # Return empty list if no values (filter will be hidden)
        return result

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.field_name: self.value()})
        return queryset

class PronounFilter(DynamicChoicesFilter):
    title = 'Pronoun'
    parameter_name = 'pronoun'
    field_name = 'pronoun'

class GenderFilter(DynamicChoicesFilter):
    title = 'Gender'
    parameter_name = 'gender'
    field_name = 'gender'

class InsuranceFilter(DynamicChoicesFilter):
    title = 'Insurance'
    parameter_name = 'insurance'
    field_name = 'insurance'

class RaceFilter(DynamicChoicesFilter):
    title = 'Race'
    parameter_name = 'race'
    field_name = 'race'

class StateFilter(DynamicChoicesFilter):
    title = 'State'
    parameter_name = 'state'
    field_name = 'state'

class ServiceAreaFilter(DynamicChoicesFilter):
    title = 'Preferred Service Area'
    parameter_name = 'pref_service_area'
    field_name = 'pref_service_area'

class EmployedFilter(DynamicChoicesFilter):
    title = 'Employed'
    parameter_name = 'employed'
    field_name = 'employed'

class ShowerFilter(DynamicChoicesFilter):
    title = 'Shower'
    parameter_name = 'shower'
    field_name = 'shower'

class HungryFilter(DynamicChoicesFilter):
    title = 'Hungry'
    parameter_name = 'hungry'
    field_name = 'hungry'

class HomelessFilter(DynamicChoicesFilter):
    title = 'Homeless'
    parameter_name = 'homeless'
    field_name = 'homeless'

class IdCardFilter(DynamicChoicesFilter):
    title = 'ID Card'
    parameter_name = 'id_card'
    field_name = 'id_card'


# AccessToken admin (existing)
@admin.register(AccessToken)
class AccessTokenAdmin(ModelAdmin):
    list_display = ('token', 'role', 'created_at', 'is_active')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('token',)
    ordering = ('-created_at',)
    # Pagination
    list_per_page = 50
    list_max_show_all = 200
    actions = ['deactivate_tokens', 'activate_tokens']

    def deactivate_tokens(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected tokens have been deactivated.")

    def activate_tokens(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected tokens have been activated.")

    deactivate_tokens.short_description = "Deactivate selected tokens"
    activate_tokens.short_description = "Activate selected tokens"


@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    list_display = (
        'id', 'fname', 'phone', 'city', 'state', 'zip', 'insurance',
        'wait_time_display', 'created_at', 'image_preview'
    )
    list_filter = (
        StateFilter,
        'city',
        InsuranceFilter,
        RaceFilter,
        EmployedFilter,
        HomelessFilter,
        PronounFilter,
        GenderFilter,
        ServiceAreaFilter,
        IdCardFilter,
        ShowerFilter,
        HungryFilter,
        'created_at',
    )
    search_fields = ('fname', 'phone', 'ssn', 'medicaid_no')
    ordering = ('-created_at',)
    # Pagination
    list_per_page = 25
    list_max_show_all = 200
    show_full_result_count = False
    # Drill-down by created date
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'image_preview', 'wait_time_display')
    fieldsets = (
        ('Personal Information', {
            'fields': ('fname', 'dob', 'gender', 'pronoun', 'phone', 'emergency_contact', 'ssn')
        }),
        ('Address', {
            'fields': ('street1', 'street2', 'city', 'state', 'zip', 'last_known_address')
        }),
        ('Medical & Other', {
            'fields': ('medicaid_no', 'id_card', 'insurance', 'race', 'pref_service_area')
        }),
        ('Status', {
            'fields': ('employed', 'shower', 'hungry', 'homeless')
        }),
        ('System', {
            'fields': ('image', 'image_preview', 'wait_time', 'wait_time_display', 'created_at', 'updated_at')
        }),
    )

    actions = ['send_checkin_email']

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" style="max-width:120px; height:auto; border-radius:4px;" />', obj.image.url)
        return '(No image)'

    image_preview.short_description = 'Image'

    def wait_time_display(self, obj):
        """Human-readable wait_time as: X days, Y hours, Z minutes."""
        wt = getattr(obj, 'wait_time', None)
        if not wt:
            return '-'
        # Ensure we handle negative or zero durations gracefully
        total_seconds = int(wt.total_seconds())
        if total_seconds < 0:
            total_seconds = 0

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        # Always show minutes (even if 0) to match requested format
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

        return ", ".join(parts)

    wait_time_display.short_description = 'Wait Time'
    wait_time_display.admin_order_field = 'wait_time'

    def send_checkin_email(self, request, queryset):
        count = 0
        for patient in queryset:
            try:
                send_patient_checkin_email.delay(patient.id)
                count += 1
            except Exception:
                # don't fail the entire action if one fails
                continue
        self.message_user(request, f"Queued check-in email for {count} patient(s).")

    send_checkin_email.short_description = 'Send check-in email (async) for selected patients'


@admin.register(QueueEntry)
class QueueEntryAdmin(ModelAdmin):
    list_display = ('id', 'patient_link', 'status', 'check_in_time', 'called_at', 'check_out_time')
    list_filter = ('status', 'check_in_time')
    search_fields = ('patient__fname', 'patient__phone')
    ordering = ('-check_in_time',)
    readonly_fields = ('check_in_time', 'called_at', 'check_out_time')
    # Pagination
    list_per_page = 50
    list_max_show_all = 200
    show_full_result_count = False

    def get_queryset(self, request):
        # optimize queries for admin list view
        qs = super().get_queryset(request)
        return qs.select_related('patient')

    def patient_link(self, obj):
        if obj.patient:
            return mark_safe(f"<a href='/admin/management/patient/{obj.patient.id}/change/'>{obj.patient.fname}</a>")
        return '-'

    patient_link.short_description = 'Patient'
    

@admin.register(AdminGmailList)
class AdminGmailListAdmin(ModelAdmin):
    list_display = ("__str__", "updated_at")
    # Pagination (not usually needed for singleton, harmless)
    list_per_page = 25
    fieldsets = (
        ("Admin Notifications", {
            "fields": ("admin_recipients",),
            "description": "Enter a comma-separated list of email addresses to receive admin notifications.",
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        # Allow adding only if there is no existing record
        from .models import AdminGmailList
        if AdminGmailList.objects.exists():
            return False
        return super().has_add_permission(request)

