from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import AccessToken, Patient, QueueEntry, AdminGmailList
from unfold.admin import ModelAdmin
from .tasks import send_patient_checkin_email


# AccessToken admin (existing)
@admin.register(AccessToken)
class AccessTokenAdmin(ModelAdmin):
    list_display = ('token', 'role', 'created_at', 'is_active')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('token',)
    ordering = ('-created_at',)
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
    list_display = ('id', 'fname', 'phone', 'city', 'state', 'zip', 'insurance', 'created_at', 'image_preview')
    list_filter = ('city', 'state', 'insurance', 'race', 'employed', 'homeless')
    search_fields = ('fname', 'phone', 'ssn', 'medicaid_no')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
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
            'fields': ('image', 'image_preview', 'wait_time', 'created_at', 'updated_at')
        }),
    )

    actions = ['send_checkin_email']

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" style="max-width:120px; height:auto; border-radius:4px;" />', obj.image.url)
        return '(No image)'

    image_preview.short_description = 'Image'

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

