"""
Signals for the Users app.
Auto-creates a CitizenProfile when a citizen user is created.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, CitizenProfile


@receiver(post_save, sender=User)
def create_citizen_profile(sender, instance, created, **kwargs):
    """
    Automatically create a CitizenProfile when a new citizen user is created.
    """
    if created and instance.role == User.Role.CITIZEN:
        CitizenProfile.objects.get_or_create(user=instance)
