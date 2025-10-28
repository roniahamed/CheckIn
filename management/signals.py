from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import SiteSettings


@receiver(post_save, sender=SiteSettings)
def clear_sitesettings_cache(sender, instance, **kwargs):
    cache.delete("sitesettings_admin_recipients")
