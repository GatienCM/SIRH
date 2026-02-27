from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from accounts.models import CustomUser


class Profession(models.Model):
    """Métiers/Professions disponibles dans l'entreprise"""
    
    PROFESSION_CHOICES = [
        ('ambulancier_dea', 'Ambulancier DEA'),
        ('auxiliaire_ambulancier', 'Auxiliaire ambulancier'),
        ('chauffeur_vsl', 'Chauffeur VSL'),
        ('chauffeur_taxi', 'Chauffeur taxi'),
        ('assistant_rh', 'Assistant RH'),
        ('responsable_rh', 'Responsable RH'),
        ('responsable_exploitation', 'Responsable d\'exploitation'),
        ('comptable', 'Comptable'),
        ('apprenti', 'Apprenti'),
        ('stagiaire', 'Stagiaire'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        choices=PROFESSION_CHOICES,
        help_text='Code unique de la profession'
    )
    label = models.CharField(
        max_length=200,
        help_text='Libellé de la profession'
    )
    description = models.TextField(
        blank=True,
        help_text='Description des responsabilités'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Profession active dans l\'entreprise'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profession'
        verbose_name_plural = 'Professions'
        ordering = ['label']
    
    def __str__(self):
        return self.label


class Employee(models.Model):
    """Modèle pour les salariés"""
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('left', 'Sorti'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Le numéro de téléphone doit être valide'
    )
    
    postal_code_regex = RegexValidator(
        regex=r'^\d{5}$',
        message='Le code postal doit contenir 5 chiffres'
    )
    
    # Informations de base
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='employee',
        help_text='Utilisateur lié au salarié'
    )
    
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text='Numéro/ID interne du salarié'
    )
    
    # Identité
    birth_date = models.DateField(
        help_text='Date de naissance'
    )
    
    birth_place = models.CharField(
        max_length=100,
        blank=True,
        help_text='Lieu de naissance'
    )
    
    nationality = models.CharField(
        max_length=100,
        blank=True,
        default='Français(e)',
        help_text='Nationalité'
    )
    
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
        help_text='Genre (pour les accords dans les contrats)'
    )
    
    # Adresse
    address = models.CharField(
        max_length=200,
        help_text='Adresse du domicile'
    )
    
    postal_code = models.CharField(
        max_length=5,
        validators=[postal_code_regex],
        help_text='Code postal'
    )
    
    city = models.CharField(
        max_length=100,
        help_text='Ville'
    )
    
    country = models.CharField(
        max_length=100,
        default='France',
        help_text='Pays'
    )
    
    # Contact
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        help_text='Numéro de téléphone personnel'
    )
    
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        help_text='Personne à contacter en urgence'
    )
    
    emergency_phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text='Téléphone du contact d\'urgence'
    )
    
    # Documents légaux
    social_security_number = models.CharField(
        max_length=15,
        unique=True,
        help_text='Numéro de sécurité sociale'
    )
    
    rib = models.CharField(
        max_length=27,
        blank=True,
        help_text='RIB (Relevé d\'Identité Bancaire)'
    )
    
    # Professionnel
    profession = models.ForeignKey(
        Profession,
        on_delete=models.PROTECT,
        help_text='Profession/Métier du salarié'
    )
    
    qualification = models.CharField(
        max_length=100,
        blank=True,
        help_text='Qualifications spécifiques (DEA, etc.)'
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text='Statut du salarié'
    )
    
    date_entry = models.DateField(
        help_text='Date d\'entrée dans l\'entreprise'
    )
    
    date_exit = models.DateField(
        blank=True,
        null=True,
        help_text='Date de sortie de l\'entreprise'
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees_created',
        help_text='Utilisateur qui a créé le salarié'
    )
    
    class Meta:
        verbose_name = 'Salarié'
        verbose_name_plural = 'Salariés'
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['status']),
            models.Index(fields=['date_entry']),
        ]
    
    def __str__(self):
        return f'{self.user.get_full_name()} ({self.employee_id})'
    
    def is_active_employee(self):
        """Vérifie si le salarié est actuellement actif"""
        return self.status == 'active' and (self.date_exit is None or self.date_exit > timezone.now().date())
    
    @property
    def age(self):
        """Calcule l'âge du salarié"""
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    @property
    def years_of_service(self):
        """Calcule l'ancienneté en années"""
        today = timezone.now().date()
        return (today - self.date_entry).days / 365.25


class EmployeeDocument(models.Model):
    """Documents associés aux salariés (GED)"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contrat de travail'),
        ('amendment', 'Avenant'),
        ('id_card', 'Pièce d\'identité'),
        ('diploma', 'Diplôme'),
        ('certificate', 'Certificat médical'),
        ('payslip', 'Bulletin de salaire'),
        ('attestation', 'Attestation'),
        ('cpam_attestation', 'Attestation CPAM'),
        ('rib', 'Relevé d\'identité bancaire'),
        ('driving_license', 'Permis de conduire'),
        ('dpae', 'DPAE'),
        ('insurance', 'Assurance'),
        ('other', 'Autre'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='ged_documents',
        verbose_name='Employé'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Type de document'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Titre du document'
    )
    file = models.FileField(
        upload_to='employee_documents/%Y/%m/',
        verbose_name='Fichier'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='Uploadé par'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'upload'
    )
    is_visible_to_employee = models.BooleanField(
        default=True,
        verbose_name='Visible par le salarié'
    )
    
    class Meta:
        verbose_name = 'Document salarié'
        verbose_name_plural = 'Documents salariés'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.employee.user.get_full_name()}"
    
    @property
    def file_size(self):
        """Retourne la taille du fichier en Ko"""
        if self.file:
            return round(self.file.size / 1024, 2)
        return 0


class MedicalVisit(models.Model):
    """Visites médicales des salariés"""
    
    VISIT_TYPE_CHOICES = [
        ('embauche', 'Visite d\'embauche'),
        ('periodique', 'Visite périodique'),
        ('reprise', 'Visite de reprise'),
        ('mi_carriere', 'Visite mi-carrière'),
        ('aptitude', 'Visite d\'aptitude'),
        ('autre', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Planifiée'),
        ('completed', 'Effectuée'),
        ('cancelled', 'Annulée'),
        ('to_schedule', 'À planifier'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='medical_visits',
        verbose_name='Employé'
    )
    visit_type = models.CharField(
        max_length=50,
        choices=VISIT_TYPE_CHOICES,
        verbose_name='Type de visite'
    )
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date prévue'
    )
    completed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date effectuée'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='to_schedule',
        verbose_name='Statut'
    )
    doctor_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Médecin du travail'
    )
    result = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('apte', 'Apte'),
            ('apte_reserve', 'Apte avec réserves'),
            ('inapte', 'Inapte'),
            ('', 'Non renseigné'),
        ],
        verbose_name='Résultat'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes / Observations'
    )
    next_visit_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Prochaine visite prévue'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Mis à jour le')
    
    class Meta:
        verbose_name = 'Visite médicale'
        verbose_name_plural = 'Visites médicales'
        ordering = ['-scheduled_date', '-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.get_visit_type_display()} - {self.scheduled_date or 'Non planifiée'}"
    
    @property
    def is_urgent(self):
        """Visite à planifier dans moins de 30 jours"""
        from datetime import date, timedelta
        if self.scheduled_date:
            return (self.scheduled_date - date.today()).days <= 30
        return False
    
    @property
    def days_until_visit(self):
        """Nombre de jours jusqu'à la visite"""
        from datetime import date
        if self.scheduled_date:
            return (self.scheduled_date - date.today()).days
        return None
