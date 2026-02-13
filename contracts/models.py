from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from employees.models import Employee
from accounts.models import CustomUser


class Contract(models.Model):
    """Modèle pour les contrats de travail"""
    
    CONTRACT_TYPE_CHOICES = [
        ('cdi', 'CDI - Contrat à Durée Indéterminée'),
        ('cdd', 'CDD - Contrat à Durée Déterminée'),
        ('apprenticeship', 'Contrat d\'apprentissage'),
        ('professionalization', 'Contrat de professionnalisation'),
        ('internship', 'Stage'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('terminated', 'Terminé'),
        ('expired', 'Expiré'),
    ]
    
    CONTRACT_STATUS_CHOICES = [
        ('trial', 'Période d\'essai'),
        ('confirmed', 'Confirmé'),
    ]
    
    ENTITY_TEMPLATE_CHOICES = [
        ('nantes_urgences', 'Nantes Urgences Sansoucy'),
        ('ambulances_sansoucy', 'Ambulances Sansoucy'),
    ]
    
    # Identification
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='contracts',
        help_text='Salarié associé au contrat'
    )
    
    contract_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Numéro unique du contrat'
    )
    
    # Type et statut
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPE_CHOICES,
        help_text='Type de contrat'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text='Statut du contrat'
    )
    
    contract_status = models.CharField(
        max_length=20,
        choices=CONTRACT_STATUS_CHOICES,
        default='trial',
        help_text='Phase du contrat (essai ou confirmé)'
    )
    
    entity_template = models.CharField(
        max_length=30,
        choices=ENTITY_TEMPLATE_CHOICES,
        blank=True,
        null=True,
        help_text='Entité pour laquelle générer le contrat'
    )
    
    # Dates
    start_date = models.DateField(
        help_text='Date de début du contrat'
    )
    
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date de fin du contrat (pour CDD, stage, etc.)'
    )
    
    trial_end_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date de fin de la période d\'essai'
    )
    
    # Conditions de travail
    working_hours_per_week = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=35.0,
        help_text='Nombre d\'heures de travail par semaine'
    )
    
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Taux horaire'
    )
    
    monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Salaire mensuel'
    )
    
    # Convention collective
    collective_agreement = models.CharField(
        max_length=200,
        default='Convention collective du transport sanitaire',
        help_text='Convention collective applicable'
    )
    
    collective_agreement_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date de la convention collective'
    )
    
    # Médecine du travail
    occupational_health_service = models.CharField(
        max_length=200,
        blank=True,
        help_text="Service de médecine du travail (nom, organisme, etc.)"
    )
    # Notes et documents
    notes = models.TextField(
        blank=True,
        help_text='Notes spécifiques sur le contrat'
    )
    
    contract_file = models.FileField(
        upload_to='contracts/',
        blank=True,
        null=True,
        help_text='Fichier du contrat (PDF)'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contracts_created',
        help_text='Utilisateur qui a créé le contrat'
    )
    
    class Meta:
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_date__lte=models.F('end_date')) | models.Q(end_date__isnull=True),
                name='check_contract_dates'
            ),
            models.CheckConstraint(
                check=models.Q(working_hours_per_week__gt=0),
                name='check_positive_hours'
            ),
        ]
    
    def __str__(self):
        return f'{self.contract_number} - {self.employee} ({self.get_contract_type_display()})'
    
    def clean(self):
        """Validations personnalisées"""
        super().clean()
        
        # Vérifier que end_date est après start_date pour les contrats avec fin
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('La date de fin doit être après la date de début')
        
        # Vérifier la période d'essai
        if self.trial_end_date:
            if self.trial_end_date < self.start_date:
                raise ValidationError('La fin d\'essai doit être après le début du contrat')
            if self.end_date and self.trial_end_date > self.end_date:
                raise ValidationError('La fin d\'essai ne peut pas dépasser la fin du contrat')
        
        # Vérifier qu'un salarié ne peut avoir qu'un seul contrat actif à la fois
        active_contracts = Contract.objects.filter(
            employee=self.employee,
            status='active'
        ).exclude(pk=self.pk)
        
        if active_contracts.exists():
            raise ValidationError(
                f'Le salarié {self.employee} a déjà un contrat actif. '
                'Un seul contrat actif par salarié est autorisé.'
            )
        
        # Vérifier le salaire ou le taux horaire
        if not self.hourly_rate and not self.monthly_salary:
            raise ValidationError('Vous devez spécifier soit un taux horaire, soit un salaire mensuel')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Vérifie si le contrat est actuellement actif"""
        # Si des dates manquent, on considère le contrat comme inactif pour éviter les erreurs
        if self.status != 'active':
            return False
        if not self.start_date:
            return False
        today = timezone.now().date()
        return (
            self.start_date <= today and
            (self.end_date is None or self.end_date >= today)
        )
    
    @property
    def is_trial_period(self):
        """Vérifie si le salarié est en période d'essai"""
        if not self.trial_end_date:
            return False
        today = timezone.now().date()
        return today < self.trial_end_date
    
    @property
    def duration_days(self):
        """Calcule la durée du contrat en jours"""
        if not self.start_date:
            return None
        end = self.end_date or timezone.now().date()
        return (end - self.start_date).days
    
    @property
    def days_remaining(self):
        """Calcule les jours restants avant la fin du contrat"""
        if self.end_date:
            today = timezone.now().date()
            remaining = (self.end_date - today).days
            return max(0, remaining)
        return None
