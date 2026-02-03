from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """Utilisateur personnalisé avec rôles et permissions étendues"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('rh', 'RH'),
        ('manager', 'Manager/Responsable exploitation'),
        ('employee', 'Salarié'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        help_text='Rôle de l\'utilisateur dans l\'application'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Le numéro de téléphone doit être valide'
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text='Numéro de téléphone'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='L\'utilisateur peut se connecter'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'
    
    def has_permission(self, permission):
        """Vérifie si l'utilisateur a une permission"""
        if self.is_superuser:
            return True
        return self.groups.filter(permissions__codename=permission).exists()
