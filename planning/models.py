from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from employees.models import Employee
from vehicles.models import Vehicle


class ShiftType(models.Model):
    """Types de shifts disponibles"""
    
    SHIFT_TYPE_CHOICES = [
        ('day', 'Jour'),
        ('night', 'Nuit'),
        ('sunday', 'Dimanche'),
        ('holiday', 'Férié'),
        ('early', 'Tôt'),
        ('late', 'Tard'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=SHIFT_TYPE_CHOICES,
        unique=True,
        help_text='Type de shift'
    )
    description = models.TextField(
        blank=True,
        help_text='Description du type de shift'
    )
    start_hour = models.TimeField(
        help_text='Heure de début standard'
    )
    end_hour = models.TimeField(
        help_text='Heure de fin standard'
    )
    base_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8,
        help_text='Nombre d\'heures de base pour ce type de shift'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Ce type de shift est actif'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Type de shift'
        verbose_name_plural = 'Types de shifts'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.get_name_display()}"


class Shift(models.Model):
    """Shifts individuels (dates/heures)"""
    
    STATUS_CHOICES = [
        ('planned', 'Planifié'),
        ('ongoing', 'En cours'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
    ]
    
    shift_type = models.ForeignKey(
        ShiftType,
        on_delete=models.PROTECT,
        related_name='shifts',
        help_text='Type de shift'
    )
    date = models.DateField(
        help_text='Date du shift'
    )
    start_time = models.TimeField(
        help_text='Heure de début réelle'
    )
    end_time = models.TimeField(
        help_text='Heure de fin réelle'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        help_text='Statut du shift'
    )
    notes = models.TextField(
        blank=True,
        help_text='Notes additionnelles sur le shift'
    )
    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_shifts',
        help_text='Créé par'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shift'
        verbose_name_plural = 'Shifts'
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['date', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'start_time', 'shift_type'],
                name='unique_shift_per_date_time_type'
            )
        ]
    
    def __str__(self):
        return f"Shift {self.get_status_display()} - {self.date} ({self.shift_type.get_name_display()})"
    
    def clean(self):
        """Valider le shift"""
        if self.end_time == self.start_time:
            raise ValidationError('L\'heure de fin doit être différente de l\'heure de début')
    
    @property
    def duration_hours(self):
        """Calculer la durée du shift en heures"""
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        if end < start:  # Cas de nuit dépassant minuit
            end += timedelta(days=1)
        return (end - start).total_seconds() / 3600
    
    @property
    def is_past(self):
        """Vérifier si le shift est passé"""
        start = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time)
        )
        end = timezone.make_aware(
            timezone.datetime.combine(self.date, self.end_time)
        )
        if end <= start:
            end += timedelta(days=1)
        return end < timezone.now()
    
    @property
    def is_ongoing(self):
        """Vérifier si le shift est en cours"""
        now = timezone.now()
        start = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time)
        )
        end = timezone.make_aware(
            timezone.datetime.combine(self.date, self.end_time)
        )
        if end <= start:
            end += timedelta(days=1)
        return start <= now <= end


class Assignment(models.Model):
    """Attribution d'un employé et d'un véhicule à un shift"""
    
    STATUS_CHOICES = [
        ('assigned', 'Assigné'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Complété'),
        ('absent', 'Absent'),
        ('cancelled', 'Annulé'),
    ]
    
    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text='Shift assigné'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text='Employé assigné'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
        help_text='Véhicule assigné (optionnel)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned',
        help_text='Statut de l\'assignment'
    )
    notes = models.TextField(
        blank=True,
        help_text='Notes sur l\'assignment'
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date de confirmation'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-shift__date', 'employee__user__last_name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['employee']),
            models.Index(fields=['shift']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['shift', 'employee'],
                name='unique_assignment_per_shift_employee'
            ),
            models.UniqueConstraint(
                fields=['shift', 'vehicle'],
                condition=models.Q(vehicle__isnull=False),
                name='unique_vehicle_per_shift'
            )
        ]
    
    def __str__(self):
        return f"{self.employee.user.get_full_name() or self.employee.user.username} - {self.shift.date}"
    
    def clean(self):
        """Valider l'assignment"""
        # Vérifier que l'employé a un contrat actif à la date du shift
        from contracts.models import Contract
        active_contract = Contract.objects.filter(
            employee=self.employee,
            start_date__lte=self.shift.date,
            is_active=True
        ).first()
        
        if not active_contract:
            raise ValidationError(
                f'L\'employé {self.employee} n\'a pas de contrat actif à la date du shift'
            )
        
        # Vérifier que l'employé n'a pas d'autre assignment le même jour
        existing = Assignment.objects.filter(
            employee=self.employee,
            shift__date=self.shift.date
        ).exclude(id=self.id)
        
        if existing.exists():
            raise ValidationError(
                f'L\'employé {self.employee} a déjà une assignation le {self.shift.date}'
            )
        
        # Vérifier que le véhicule (s'il existe) n'est pas assigné à un autre employé le même jour
        if self.vehicle:
            vehicle_conflict = Assignment.objects.filter(
                vehicle=self.vehicle,
                shift__date=self.shift.date
            ).exclude(id=self.id).exists()
            
            if vehicle_conflict:
                raise ValidationError(
                    f'Le véhicule {self.vehicle} est déjà assigné pour le {self.shift.date}'
                )
    
    @property
    def is_confirmed(self):
        """Vérifier si l'assignment est confirmé"""
        return self.status in ['confirmed', 'in_progress', 'completed']
