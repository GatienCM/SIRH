from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from accounts.models import CustomUser


class AuditLog(models.Model):
    """Journal d'audit de toutes les actions dans le système"""
    
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('approve', 'Approbation'),
        ('reject', 'Refus'),
        ('submit', 'Soumission'),
        ('cancel', 'Annulation'),
        ('view', 'Consultation'),
        ('export', 'Exportation'),
        ('other', 'Autre'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='Utilisateur'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Action'
    )
    
    # Pour lier à n'importe quel modèle
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Type de contenu'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID de l\'objet'
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Représentation de l\'objet'
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Modifications'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Adresse IP'
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='User Agent'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Horodatage'
    )
    
    class Meta:
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journaux d\'audit'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"


class SystemSetting(models.Model):
    """Paramètres système configurables"""
    
    SETTING_TYPE_CHOICES = [
        ('string', 'Chaîne de caractères'),
        ('integer', 'Nombre entier'),
        ('float', 'Nombre décimal'),
        ('boolean', 'Booléen'),
        ('json', 'JSON'),
    ]
    
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Clé'
    )
    value = models.TextField(
        verbose_name='Valeur'
    )
    setting_type = models.CharField(
        max_length=20,
        choices=SETTING_TYPE_CHOICES,
        default='string',
        verbose_name='Type'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    is_sensitive = models.BooleanField(
        default=False,
        verbose_name='Sensible'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Mis à jour le'
    )
    
    class Meta:
        verbose_name = 'Paramètre système'
        verbose_name_plural = 'Paramètres système'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value if not self.is_sensitive else '***'}"
    
    def get_value(self):
        """Retourne la valeur convertie selon le type"""
        if self.setting_type == 'integer':
            return int(self.value)
        elif self.setting_type == 'float':
            return float(self.value)
        elif self.setting_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes', 'oui']
        elif self.setting_type == 'json':
            import json
            return json.loads(self.value)
        return self.value
