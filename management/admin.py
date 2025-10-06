from django.contrib import admin
from .models import AccessToken
from unfold.admin import ModelAdmin
# Register your models here.

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
    
