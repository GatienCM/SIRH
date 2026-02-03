from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from accounts.models import CustomUser


class Vehicle(models.Model):
    """Modèle pour les véhicules (ambulances, VSL, taxis)"""
    
    VEHICLE_TYPE_CHOICES = [
        ('ambulance', 'Ambulance'),
        ('vsl', 'VSL - Véhicule Sanitaire Léger'),
        ('taxi', 'Taxi'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('maintenance', 'En maintenance'),
        ('out_of_service', 'Hors service'),
        ('retired', 'Retiré du service'),
    ]
    
    # Identification
    vehicle_id = models.CharField(
        max_length=50,
        unique=True,
        help_text='Identifiant interne du véhicule'
    )
    
    registration_number = models.CharField(
        max_length=10,
        unique=True,
        help_text='Immatriculation du véhicule (ex: AB-123-CD)'
    )
    
    # Type et caractéristiques
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        help_text='Type de véhicule'
    )
    
    brand = models.CharField(
        max_length=100,
        help_text='Marque du véhicule (ex: Mercedes, Renault)'
    )
    
    model = models.CharField(
        max_length=100,
        help_text='Modèle du véhicule'
    )
    
    year = models.IntegerField(
        help_text='Année de fabrication'
    )
    
    color = models.CharField(
        max_length=50,
        blank=True,
        help_text='Couleur du véhicule'
    )
    
    # Capacités
    seats_count = models.IntegerField(
        default=3,
        help_text='Nombre de places (y compris conducteur)'
    )
    
    stretcher_capacity = models.IntegerField(
        default=1,
        help_text='Nombre de brancards pouvant être transportés'
    )
    
    # Kilométrage
    initial_mileage = models.IntegerField(
        default=0,
        help_text='Kilométrage initial (entrée en service)'
    )
    
    current_mileage = models.IntegerField(
        default=0,
        help_text='Kilométrage actuel'
    )
    
    # Motorisation
    fuel_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Type de carburant (essence, diesel, électrique, etc.)'
    )
    
    consumption_per_100km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Consommation moyenne (l/100km)'
    )
    
    # Dates
    purchase_date = models.DateField(
        help_text='Date d\'achat du véhicule'
    )
    
    entry_date = models.DateField(
        help_text='Date d\'entrée en service'
    )
    
    exit_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date de sortie du service'
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        help_text='Statut actuel du véhicule'
    )
    
    # Maintenance
    last_maintenance_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date de la dernière maintenance'
    )
    
    next_maintenance_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date prévue de la prochaine maintenance'
    )
    
    last_inspection_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date du dernier contrôle technique'
    )
    
    next_inspection_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date du prochain contrôle technique'
    )
    
    # Assurance
    insurance_policy_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Numéro de police d\'assurance'
    )
    
    insurance_expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date d\'expiration de l\'assurance'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text='Notes et observations sur le véhicule'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vehicles_created',
        help_text='Utilisateur qui a créé le véhicule'
    )
    
    class Meta:
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        ordering = ['vehicle_id']
        indexes = [
            models.Index(fields=['vehicle_id']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['status']),
            models.Index(fields=['vehicle_type']),
        ]
    
    def __str__(self):
        return f'{self.vehicle_id} - {self.brand} {self.model} ({self.registration_number})'
    
    @property
    def is_available(self):
        """Vérifie si le véhicule est disponible"""
        return (
            self.status == 'available' and
            (self.exit_date is None or self.exit_date > timezone.now().date())
        )
    
    @property
    def age_years(self):
        """Calcule l'âge du véhicule en années"""
        today = timezone.now().date()
        return today.year - self.year
    
    @property
    def total_mileage(self):
        """Total du kilométrage parcouru"""
        return self.current_mileage - self.initial_mileage
    
    @property
    def is_maintenance_needed(self):
        """Vérifie si une maintenance est prévue"""
        if not self.next_maintenance_date:
            return False
        return self.next_maintenance_date <= timezone.now().date()
    
    @property
    def is_inspection_needed(self):
        """Vérifie si un contrôle technique est prévue"""
        if not self.next_inspection_date:
            return False
        return self.next_inspection_date <= timezone.now().date()
    
    @property
    def is_insurance_valid(self):
        """Vérifie si l'assurance est valide"""
        if not self.insurance_expiry_date:
            return False
        return self.insurance_expiry_date > timezone.now().date()
