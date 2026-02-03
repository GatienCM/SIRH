from django.db import models
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta, time
from employees.models import Employee
from planning.models import Assignment, ShiftType
from accounts.models import CustomUser


class TimeSheet(models.Model):
    """Feuille de temps mensuelle d'un employé"""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('paid', 'Payé'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='timesheets',
        verbose_name='Employé',
        help_text='Employé'
    )
    year = models.IntegerField(
        verbose_name='Année',
        help_text='Année'
    )
    month = models.IntegerField(
        verbose_name='Mois',
        help_text='Mois (1-12)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut',
        help_text='Statut de la feuille de temps'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text='Notes additionnelles'
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Soumis le',
        help_text='Date de soumission'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Approuvé le',
        help_text='Date d\'approbation'
    )
    approved_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timesheets',
        verbose_name='Approuvé par',
        help_text='Approuvé par'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Mis à jour le')
    
    class Meta:
        verbose_name = 'Feuille de temps'
        verbose_name_plural = 'Feuilles de temps'
        ordering = ['-year', '-month', 'employee__user__last_name']
        unique_together = ['employee', 'year', 'month']
    
    def __str__(self):
        return f"Feuille de temps {self.employee} - {self.month}/{self.year}"
    
    @property
    def total_hours(self):
        """Calculer le total d'heures du mois"""
        entries = self.entries.all()
        return entries.aggregate(total=Sum('hours_worked'))['total'] or 0
    
    @property
    def total_normal_hours(self):
        """Calculer le total d'heures normales"""
        return self.entries.filter(hour_type='normal').aggregate(total=Sum('hours_worked'))['total'] or 0
    
    @property
    def total_night_hours(self):
        """Calculer le total d'heures de nuit"""
        return self.entries.filter(hour_type='night').aggregate(total=Sum('hours_worked'))['total'] or 0
    
    @property
    def total_sunday_hours(self):
        """Calculer le total d'heures du dimanche"""
        return self.entries.filter(hour_type='sunday').aggregate(total=Sum('hours_worked'))['total'] or 0
    
    @property
    def total_holiday_hours(self):
        """Calculer le total d'heures de féries"""
        return self.entries.filter(hour_type='holiday').aggregate(total=Sum('hours_worked'))['total'] or 0
    
    @property
    def total_overtime_hours(self):
        """Calculer le total d'heures supplémentaires"""
        return self.entries.filter(hour_type='overtime').aggregate(total=Sum('hours_worked'))['total'] or 0
    
    def get_last_day_of_month(self):
        """Retourner le dernier jour du mois"""
        from calendar import monthrange
        from datetime import date
        last_day = monthrange(self.year, self.month)[1]
        return date(self.year, self.month, last_day)
    
    @property
    def is_submitted(self):
        """Vérifier si la feuille est soumise"""
        return self.status in ['submitted', 'approved', 'paid']
    
    def auto_fill_from_assignments(self):
        """Remplir automatiquement les entrées à partir des quarts assignés"""
        from datetime import datetime, timedelta, time
        from calendar import monthrange
        from contracts.models import Contract
        
        # Récupérer le contrat actif de l'employé pour le taux horaire
        active_contract = None
        today = datetime.now().date()
        for contract in Contract.objects.filter(employee=self.employee, end_date__gte=today):
            if contract.hourly_rate:
                active_contract = contract
                break
        
        if not active_contract or not active_contract.hourly_rate:
            return 0  # Pas de contrat actif ou pas de taux horaire
        
        # Récupérer le nombre de jours dans le mois
        days_in_month = monthrange(self.year, self.month)[1]
        
        # Récupérer les assignments de l'employé pour ce mois
        assignments = Assignment.objects.filter(
            employee=self.employee,
            shift__date__year=self.year,
            shift__date__month=self.month,
            status__in=['assigned', 'confirmed', 'in_progress', 'completed']
        ).select_related('shift')
        
        # Supprimer uniquement les entrées existantes liées à des assignments (pas les ajustements)
        self.entries.filter(assignment__isnull=False).delete()
        
        # Créer une entrée pour chaque assignment
        entries_created = 0
        for assignment in assignments:
            shift = assignment.shift
            
            # Calculer les heures
            start = datetime.combine(shift.date, shift.start_time)
            end = datetime.combine(shift.date, shift.end_time)
            
            # Gérer les quarts de nuit (passant minuit)
            if end < start:
                end += timedelta(days=1)
            
            hours = (end - start).total_seconds() / 3600
            
            # Déterminer le type d'heures (comparer directement les objets time)
            hour_type = 'normal'
            if shift.date.weekday() == 6:  # Dimanche
                hour_type = 'sunday'
            elif shift.start_time >= time(21, 0) or shift.end_time <= time(7, 0):
                hour_type = 'night'
            
            # Créer l'entrée
            TimeSheetEntry.objects.create(
                timesheet=self,
                assignment=assignment,
                date=shift.date,
                hour_type=hour_type,
                hours_worked=hours,
                hourly_rate=active_contract.hourly_rate,
                notes=f"Auto-généré du quart {shift.shift_type}"
            )
            entries_created += 1
        
        return entries_created


class TimeSheetEntry(models.Model):
    """Entrée détaillée dans une feuille de temps"""
    
    HOUR_TYPE_CHOICES = [
        ('normal', 'Heures normales'),
        ('night', 'Heures de nuit'),
        ('sunday', 'Heures dimanche'),
        ('holiday', 'Heures féries'),
        ('overtime', 'Heures supplémentaires'),
    ]
    
    timesheet = models.ForeignKey(
        TimeSheet,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name='Feuille de temps',
        help_text='Feuille de temps'
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timesheet_entries',
        verbose_name='Assignment',
        help_text='Assignment lié'
    )
    date = models.DateField(
        verbose_name='Date',
        help_text='Date du travail'
    )
    hour_type = models.CharField(
        max_length=20,
        choices=HOUR_TYPE_CHOICES,
        verbose_name='Type d\'heures',
        help_text='Type d\'heures'
    )
    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Heures travaillées',
        help_text='Nombre d\'heures travaillées'
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Taux horaire',
        help_text='Taux horaire'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text='Notes additionnelles'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Mis à jour le')
    
    class Meta:
        verbose_name = 'Entrée feuille de temps'
        verbose_name_plural = 'Entrées feuille de temps'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.timesheet.employee} - {self.date} ({self.get_hour_type_display()})"
    
    @property
    def amount(self):
        """Calculer le montant pour cette entrée"""
        return self.hours_worked * self.hourly_rate


class AbsenceRecord(models.Model):
    """Enregistrement d'absences"""
    
    ABSENCE_TYPE_CHOICES = [
        ('sick', 'Maladie'),
        ('vacation', 'Congés'),
        ('unpaid', 'Absent non justifié'),
        ('maternal', 'Congé maternité'),
        ('paternal', 'Congé paternité'),
        ('personal', 'Raison personnelle'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='absences',
        verbose_name='Employé',
        help_text='Employé'
    )
    date_start = models.DateField(
        verbose_name='Date de début',
        help_text='Date de début'
    )
    date_end = models.DateField(
        verbose_name='Date de fin',
        help_text='Date de fin'
    )
    absence_type = models.CharField(
        max_length=20,
        choices=ABSENCE_TYPE_CHOICES,
        verbose_name='Type d\'absence',
        help_text='Type d\'absence'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text='Notes (certificat médical, etc.)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Mis à jour le')
    
    class Meta:
        verbose_name = 'Absence'
        verbose_name_plural = 'Absences'
        ordering = ['-date_start']
    
    def __str__(self):
        return f"{self.employee} - {self.get_absence_type_display()} ({self.date_start} à {self.date_end})"
    
    @property
    def duration_days(self):
        """Calculer la durée en jours"""
        return (self.date_end - self.date_start).days + 1

class TimeSheetAdjustment(models.Model):
    """Ajustement d'heures sur une feuille de temps (heures supplémentaires ou réductions)"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente de validation'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    HOUR_TYPE_CHOICES = [
        ('normal', 'Heures normales'),
        ('night', 'Heures de nuit'),
        ('sunday', 'Heures dimanche'),
        ('holiday', 'Heures féries'),
        ('overtime', 'Heures supplémentaires'),
    ]
    
    timesheet = models.ForeignKey(
        TimeSheet,
        on_delete=models.CASCADE,
        related_name='adjustments',
        verbose_name='Feuille de temps',
        help_text='Feuille de temps'
    )
    
    hours_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Ajustement d\'heures',
        help_text='Nombre d\'heures à ajouter (positif) ou retirer (négatif). Exemple: +2.5 ou -1'
    )
    
    hour_type = models.CharField(
        max_length=20,
        choices=HOUR_TYPE_CHOICES,
        default='overtime',
        verbose_name='Type d\'heures',
        help_text='Type d\'heures ajustées'
    )
    
    reason = models.CharField(
        max_length=200,
        verbose_name='Raison',
        help_text='Raison de l\'ajustement (ex: Heures supplémentaires, Erreur de saisie, etc.)'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut',
        help_text='Statut de l\'ajustement'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notes de l\'admin',
        help_text='Notes additionnelles de l\'administrateur'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_adjustments',
        verbose_name='Approuvé par',
        help_text='Administrateur qui a approuvé'
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Approuvé le'
    )
    
    class Meta:
        verbose_name = 'Ajustement feuille de temps'
        verbose_name_plural = 'Ajustements feuilles de temps'
        ordering = ['-created_at']
    
    def __str__(self):
        sign = '+' if self.hours_adjustment >= 0 else ''
        return f"{self.timesheet.employee} - {sign}{self.hours_adjustment}h ({self.reason}) - {self.get_status_display()}"