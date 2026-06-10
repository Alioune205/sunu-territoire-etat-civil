import uuid
from django.db import models
from django.conf import settings

class NdiogoyeChatLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ndiogoye_logs'
    )
    session_id = models.CharField(max_length=255, db_index=True)
    message = models.TextField(verbose_name='Message Utilisateur')
    reply = models.TextField(verbose_name='Réponse IA')
    intent = models.CharField(max_length=100, verbose_name='Intention')
    action = models.CharField(max_length=100, blank=True, null=True, verbose_name='Action')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log Ndiogoye'
        verbose_name_plural = 'Logs Ndiogoye'

    def __str__(self):
        return f"Chat {self.session_id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
