from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from employees.models import Employee
from decimal import Decimal


class LeaveRequest(models.Model):
    """Demandes de congés des employés"""
    
    LEAVE_TYPE_CHOICES = [
        ('vacation', 'Congés payés'),
        ('sick', 'Congé maladie'),
        ('unpaid', 'Congé sans solde'),
        ('maternity', 'Congé maternité'),
        ('paternity', 'Congé paternité'),
        ('personal', 'Raison personnelle'),
        ('training', 'Formation'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Refusée'),
        ('cancelled', 'Annulée'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name='Employé'
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
        verbose_name='Type de congé'
    )
    start_date = models.DateField(
        verbose_name='Date de début'
    )
    end_date = models.DateField(
        verbose_name='Date de fin'
    )
    days_requested = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.5'))],
        verbose_name='Nombre de jours'
    )
    reason = models.TextField(
        verbose_name='Motif'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests',
        verbose_name='Approuvé par'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Approuvé le'
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='Motif de refus'
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
        verbose_name = 'Demande de congé'
        verbose_name_plural = 'Demandes de congés'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.start_date} - {self.end_date})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date < self.start_date:
            raise ValidationError('La date de fin doit être après la date de début')


class TimeOffBalance(models.Model):
    """Solde de congés des employés"""
    
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='time_off_balance',
        verbose_name='Employé'
    )
    year = models.IntegerField(
        default=timezone.now().year,
        verbose_name='Année'
    )
    vacation_days_total = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('25.0'),
        verbose_name='Total congés payés'
    )
    vacation_days_taken = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        verbose_name='Congés payés pris'
    )
    sick_days_taken = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        verbose_name='Jours maladie pris'
    )
    other_days_taken = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        verbose_name='Autres jours pris'
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
        verbose_name = 'Solde de congés'
        verbose_name_plural = 'Soldes de congés'
        unique_together = [['employee', 'year']]
        ordering = ['-year', 'employee']
    
    def __str__(self):
        return f"{self.employee} - {self.year}"
    
    @property
    def vacation_days_remaining(self):
        """Jours de congés payés restants"""
        return self.vacation_days_total - self.vacation_days_taken


class Document(models.Model):
    """Documents personnels des employés"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contrat de travail'),
        ('payslip', 'Fiche de paie'),
        ('certificate', 'Attestation'),
        ('medical', 'Document médical'),
        ('id', 'Pièce d\'identité'),
        ('diploma', 'Diplôme'),
        ('other', 'Autre'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Employé'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Type de document'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Titre'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        verbose_name='Fichier'
    )
    uploaded_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='Téléchargé par'
    )
    is_confidential = models.BooleanField(
        default=False,
        verbose_name='Confidentiel'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    
    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.employee}"


class Notification(models.Model):
    """Notifications pour les employés"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('success', 'Succès'),
        ('error', 'Erreur'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Employé'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='info',
        verbose_name='Type'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Titre'
    )
    message = models.TextField(
        verbose_name='Message'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Lu'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Lu le'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.employee}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
