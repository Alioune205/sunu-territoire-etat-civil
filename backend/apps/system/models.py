from django.db import models

class GlobalSettings(models.Model):
    """
    Singleton model to store global system settings.
    """
    biometric_auth_enabled = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(GlobalSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
