from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from employees.models import Employee
from timesheets.models import TimeSheet
from decimal import Decimal

class SalaryScale(models.Model):
    """Grille salariale avec les tarifs horaires"""
    
    BASE_RATE_CHOICES = [
        ('smic', 'SMIC'),
        ('qualified', 'Qualifié'),
        ('senior', 'Senior'),
        ('manager', 'Manager'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la grille'
    )
    level = models.CharField(
        max_length=20,
        choices=BASE_RATE_CHOICES,
        verbose_name='Niveau'
    )
    base_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Taux horaire de base (€)'
    )
    night_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('1.25'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('3.0'))],
        verbose_name='Multiplicateur nuit'
    )
    sunday_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('1.50'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('3.0'))],
        verbose_name='Multiplicateur dimanche'
    )
    holiday_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('2.00'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('3.0'))],
        verbose_name='Multiplicateur férié'
    )
    overtime_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('1.50'),
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('3.0'))],
        verbose_name='Multiplicateur heures supplémentaires'
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
        verbose_name = 'Grille salariale'
        verbose_name_plural = 'Grilles salariales'
        ordering = ['-level']
    
    def __str__(self):
        return f'{self.name} - {self.level} ({self.base_rate}€/h)'


class Payroll(models.Model):
    """Document de paie mensuelle"""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('calculated', 'Calculée'),
        ('validated', 'Validée'),
        ('processed', 'Traitée'),
        ('paid', 'Payée'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payrolls',
        verbose_name='Employé'
    )
    period = models.CharField(
        max_length=7,
        help_text='Format: YYYY-MM',
        verbose_name='Période (YYYY-MM)'
    )
    year = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        verbose_name='Année'
    )
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='Mois'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut'
    )
    
    # Heures travaillées
    total_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total heures'
    )
    normal_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Heures normales'
    )
    night_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Heures de nuit'
    )
    sunday_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Heures dimanche'
    )
    holiday_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Heures féries'
    )
    overtime_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Heures supplémentaires'
    )
    
    # Salaires bruts
    gross_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salaire brut'
    )
    normal_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salaire normal'
    )
    night_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salaire nuit'
    )
    sunday_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salaire dimanche'
    )
    holiday_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salaire féries'
    )
    overtime_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salaire heures supplémentaires'
    )
    
    # Déductions
    total_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total déductions'
    )
    social_security = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Cotisations sociales'
    )
    taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Impôts'
    )
    other_deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Autres déductions'
    )
    
    # Salaire net
    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salaire net'
    )
    
    # Timestamps
    calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Calculée le'
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Validée le'
    )
    validated_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_payrolls',
        verbose_name='Validée par'
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Payée le'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Mis à jour le'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    
    class Meta:
        verbose_name = 'Fiche de paie'
        verbose_name_plural = 'Fiches de paie'
        ordering = ['-period', 'employee']
        unique_together = [['employee', 'period']]
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['status']),
            models.Index(fields=['employee']),
        ]
    
    def __str__(self):
        return f'{self.employee.user.first_name} {self.employee.user.last_name} - {self.period}'
    
    def populate_hours_from_timesheet(self):
        """
        Remplir les heures de la paie à partir de la feuille de temps de l'employé
        pour la période correspondante (year/month)
        """
        from timesheets.models import TimeSheet
        
        try:
            timesheet = TimeSheet.objects.get(
                employee=self.employee,
                year=self.year,
                month=self.month
            )
            
            # Récupérer les heures par type depuis la timesheet
            self.normal_hours = timesheet.total_normal_hours or Decimal('0.00')
            self.night_hours = timesheet.total_night_hours or Decimal('0.00')
            self.sunday_hours = timesheet.total_sunday_hours or Decimal('0.00')
            self.holiday_hours = timesheet.total_holiday_hours or Decimal('0.00')
            self.overtime_hours = timesheet.total_overtime_hours or Decimal('0.00')
            
            # Calculer le total
            self.total_hours = (
                self.normal_hours +
                self.night_hours +
                self.sunday_hours +
                self.holiday_hours +
                self.overtime_hours
            )
            
            return True
        except TimeSheet.DoesNotExist:
            return False
    
    def calculate_salary(self, salary_scale):
        """Calcule le salaire brut basé sur la grille salariale"""
        self.normal_salary = self.normal_hours * salary_scale.base_rate
        self.night_salary = self.night_hours * salary_scale.base_rate * salary_scale.night_multiplier
        self.sunday_salary = self.sunday_hours * salary_scale.base_rate * salary_scale.sunday_multiplier
        self.holiday_salary = self.holiday_hours * salary_scale.base_rate * salary_scale.holiday_multiplier
        self.overtime_salary = self.overtime_hours * salary_scale.base_rate * salary_scale.overtime_multiplier
        
        self.gross_salary = (
            self.normal_salary +
            self.night_salary +
            self.sunday_salary +
            self.holiday_salary +
            self.overtime_salary
        )
        
        return self.gross_salary
    
    def calculate_deductions(self, social_security_rate=0.08, tax_rate=0.05):
        """Calcule les déductions standards"""
        self.social_security = self.gross_salary * Decimal(str(social_security_rate))
        self.taxes = self.gross_salary * Decimal(str(tax_rate))
        self.total_deductions = self.social_security + self.taxes + self.other_deductions
        self.net_salary = self.gross_salary - self.total_deductions
        
        return self.net_salary

    def calculate_with_payroll_rules(self):
        """
        Calcule les déductions en utilisant les variables et cotisations de la base de données.
        Implémente la logique conforme au guide sémantique :
        - Assiettes abattues (CSG/CRDS à 98.25%)
        - Tranches correctes (T1, T2)
        - Calcul explicite et traçable
        """
        self.social_security = Decimal('0.00')
        self.taxes = Decimal('0.00')
        
        # Récupère les cotisations actives salariales UNIQUEMENT
        active_contributions = PayrollContribution.objects.filter(
            is_active=True,
            is_patronal=False
        )
        
        for contribution in active_contributions:
            rate = contribution.rate / Decimal('100')  # Convertir % en décimal
            
            # 1️⃣ DÉTERMINER L'ASSIETTE selon le type
            if contribution.assiette_type == 'ABATTUE_9825':
                # CSG/CRDS : assiette = 98.25% du brut
                assiette_base = self.gross_salary * Decimal('0.9825')
            else:
                # BRUT ou PLAFONNEE : assiette = brut
                assiette_base = self.gross_salary
            
            # 2️⃣ APPLIQUER LES PLAFONDS ET TRANCHES
            if contribution.tranche_min:
                # Cotisation par TRANCHE (ex: T2 = entre 4005€ et 32040€)
                if contribution.ceiling:
                    # Tranche entre min et max
                    tranche_haute = min(assiette_base, contribution.ceiling)
                    tranche_basse = contribution.tranche_min
                    applicable_base = max(Decimal('0'), tranche_haute - tranche_basse)
                else:
                    # Tranche au-dessus du min sans limite
                    applicable_base = max(Decimal('0'), assiette_base - contribution.tranche_min)
            elif contribution.ceiling:
                # Cotisation PLAFONNÉE (ex: vieillesse, retraite T1)
                applicable_base = min(assiette_base, contribution.ceiling)
            else:
                # Cotisation DÉPLAFONNÉE (ex: CSG, vieillesse déplafonnée)
                applicable_base = assiette_base
            
            # 3️⃣ CALCULER LE MONTANT
            amount = applicable_base * rate
            
            # 4️⃣ AJOUTER AUX DÉDUCTIONS
            self.social_security += amount
            
            # 5️⃣ CRÉER LIGNE DÉTAILLÉE (pour traçabilité)
            PayrollItem.objects.get_or_create(
                payroll=self,
                item_type='deduction',
                description=contribution.name,
                defaults={'amount': amount}
            )
        
        # Calculer les éventuelles variables de paie (primes, indemnités)
        active_variables = PayrollVariable.objects.filter(is_active=True)
        bonus_total = Decimal('0.00')
        
        for variable in active_variables:
            # Ne traiter que les variables en €, pas les %
            if variable.unit == '€' and variable.name in ['Indemnité de transport', 'Prime de production']:
                bonus_total += variable.value
        
        # Appliquer les déductions et bonus
        self.total_deductions = self.social_security + self.taxes + self.other_deductions - bonus_total
        self.net_salary = self.gross_salary - self.total_deductions
        
        return self.net_salary


class PayrollItem(models.Model):
    """Détails d'un élément de paie"""
    
    ITEM_TYPE_CHOICES = [
        ('salary', 'Salaire'),
        ('bonus', 'Prime'),
        ('deduction', 'Déduction'),
        ('advance', 'Avance'),
    ]
    
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Fiche de paie'
    )
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        verbose_name='Type'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Description'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Montant'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    
    class Meta:
        verbose_name = 'Élément de paie'
        verbose_name_plural = 'Éléments de paie'
        ordering = ['payroll', 'item_type']
    
    def __str__(self):
        return f'{self.payroll} - {self.description}: {self.amount}€'

# Variables de paie et cotisations sociales
class PayrollVariable(models.Model):
    """Variables de paie personnalisables"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la variable")
    value = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Valeur")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Unité", help_text="% ou €")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Variable de paie"
        verbose_name_plural = "Variables de paie"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.value}{self.unit})"


class PayrollContribution(models.Model):
    """Cotisations sociales"""
    
    # Choix pour le type d'assiette
    ASSIETTE_BRUT = 'BRUT'
    ASSIETTE_ABATTUE_9825 = 'ABATTUE_9825'
    ASSIETTE_PLAFONNEE = 'PLAFONNEE'
    
    ASSIETTE_CHOICES = [
        (ASSIETTE_BRUT, 'Salaire brut (100%)'),
        (ASSIETTE_ABATTUE_9825, 'Salaire abattu (98.25% du brut)'),
        (ASSIETTE_PLAFONNEE, 'Salaire plafonné'),
    ]
    
    # Choix pour l'organisme collecteur
    ORGANISME_URSSAF = 'URSSAF'
    ORGANISME_AGIRC_ARRCO = 'AGIRC_ARRCO'
    ORGANISME_POLE_EMPLOI = 'POLE_EMPLOI'
    ORGANISME_AUTRE = 'AUTRE'
    
    ORGANISME_CHOICES = [
        (ORGANISME_URSSAF, 'URSSAF'),
        (ORGANISME_AGIRC_ARRCO, 'AGIRC-ARRCO'),
        (ORGANISME_POLE_EMPLOI, 'Pôle Emploi'),
        (ORGANISME_AUTRE, 'Autre'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la cotisation")
    rate = models.DecimalField(max_digits=6, decimal_places=4, verbose_name="Taux (%)")
    ceiling = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Plafond (€)")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_patronal = models.BooleanField(default=False, verbose_name="Cotisation patronale (employeur)", 
                                      help_text="Cochez si c'est une cotisation patronale (à charge de l'employeur)")
    
    # Nouveaux champs pour la cohérence sémantique
    assiette_type = models.CharField(
        max_length=20,
        choices=ASSIETTE_CHOICES,
        default=ASSIETTE_BRUT,
        verbose_name="Type d'assiette",
        help_text="Base de calcul : brut, abattu 98.25% (CSG/CRDS), ou plafonné"
    )
    
    tranche_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Tranche min (€)",
        help_text="Pour les cotisations par tranche (ex: T2 commence à 4005€)"
    )
    
    organisme = models.CharField(
        max_length=20,
        choices=ORGANISME_CHOICES,
        default=ORGANISME_URSSAF,
        verbose_name="Organisme collecteur"
    )
    
    deductible_fiscalement = models.BooleanField(
        default=False,
        verbose_name="Déductible fiscalement",
        help_text="La cotisation réduit-elle le revenu imposable ?"
    )
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotisation sociale"
        verbose_name_plural = "Cotisations sociales"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.rate}%){'[PATRONALE]' if self.is_patronal else '[SALARIALE]'}"