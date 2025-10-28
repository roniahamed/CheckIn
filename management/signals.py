from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import AdminGmailList


@receiver(post_save, sender=AdminGmailList)
def clear_sitesettings_cache(sender, instance, **kwargs):
    # No cache currently, function kept for compatibility/extension
    cache.delete("sitesettings_admin_recipients")
