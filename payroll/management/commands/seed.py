from django.core.management.base import BaseCommand
from decimal import Decimal
from payroll.models import PayrollVariable, PayrollContribution


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔄 Initialisation des variables et cotisations obligatoires..."))

        PMSS = Decimal('4005.00')
        PASS_4 = PMSS * 4
        PASS_8 = PMSS * 8

        # ========== VARIABLES DE PAIE ==========
        variables = [
            {
                'name': 'Taux horaire SMIC',
                'value': Decimal('11.88'),
                'unit': '€',
                'description': 'Salaire Minimum Interprofessionnel de Croissance 2026',
                'is_active': True
            },
            {
                'name': 'Taux nuit (heures 22h-6h)',
                'value': Decimal('125'),
                'unit': '%',
                'description': 'Majoration minimale pour heures de nuit',
                'is_active': True
            },
            {
                'name': 'Taux dimanche',
                'value': Decimal('150'),
                'unit': '%',
                'description': 'Majoration minimale pour dimanche',
                'is_active': True
            },
            {
                'name': 'Taux jours fériés',
                'value': Decimal('200'),
                'unit': '%',
                'description': 'Majoration minimale pour jour férié',
                'is_active': True
            },
            {
                'name': 'Taux heures supplémentaires',
                'value': Decimal('150'),
                'unit': '%',
                'description': 'Majoration minimale pour heures supplémentaires',
                'is_active': True
            },
            {
                'name': 'Congés payés',
                'value': Decimal('10'),
                'unit': '%',
                'description': 'Taux de droits à congés payés par rapport aux heures travaillées',
                'is_active': True
            },
            {
                'name': 'Indemnité de panier',
                'value': Decimal('3.50'),
                'unit': '€',
                'description': 'Indemnité journalière de panier si travail de plus de 6 heures',
                'is_active': False
            },
            {
                'name': 'Indemnité de transport',
                'value': Decimal('50'),
                'unit': '€',
                'description': 'Allocation transport mensuelle',
                'is_active': False
            },
            {
                'name': 'Prime de production',
                'value': Decimal('0'),
                'unit': '€',
                'description': 'Prime de production mensuelle (à ajuster)',
                'is_active': False
            },
            {
                'name': 'Prime d\'ancienneté',
                'value': Decimal('0'),
                'unit': '%',
                'description': 'Pourcentage de prime d\'ancienneté',
                'is_active': False
            },
        ]

        # ========== COTISATIONS SOCIALES OBLIGATOIRES ==========
        # Plafond Sécurité Sociale Mensuel 2026 : 4 005€
        # Source : URSSAF & Décret annuel du plafond SS
        
        contributions = [
            # ===== COTISATIONS SALARIALES (déduites du salaire brut) =====
            
            # --- ASSURANCE VIEILLESSE ---
            {
                'name': 'Vieillesse plafonnée (T1)',
                'rate': Decimal('6.90'),
                'ceiling': Decimal('4005.00'),  # 1 PASS mensuel 2026
                'description': 'Assurance vieillesse de base - tranche 1 (≤ PASS)',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': None,
                'organisme': 'URSSAF',
                'deductible_fiscalement': True
            },
            {
                'name': 'Vieillesse déplafonnée',
                'rate': Decimal('0.40'),
                'ceiling': None,
                'description': 'Assurance vieillesse - part déplafonnée (totalité salaire)',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'BRUT',
                'tranche_min': None,
                'organisme': 'URSSAF',
                'deductible_fiscalement': True
            },
            
            # --- ASSURANCE CHÔMAGE ---
            {
                'name': 'Assurance chômage',
                'rate': Decimal('2.40'),
                'ceiling': PASS_4,  # 4 PASS mensuel
                'description': 'Pôle Emploi - contribution salarié (≤ 4 PASS)',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': None,
                'organisme': 'POLE_EMPLOI',
                'deductible_fiscalement': False
            },
            {
                'name': 'Retraite complémentaire T1',
                'rate': Decimal('3.15'),
                'ceiling': PMSS,  # Tranche 1 : ≤ 1 PASS
                'description': 'Agirc-Arrco tranche 1 (≤ PASS) - taux contractuel 6.20% dont 3.15% salarié',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': None,
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': True
            },
            {
                'name': 'Retraite complémentaire T2',
                'rate': Decimal('8.64'),
                'ceiling': PASS_8,  # Tranche 2 : entre 1 et 8 PASS
                'description': 'Agirc-Arrco tranche 2 (1-8 PASS) - taux contractuel 17.00% dont 8.64% salarié',
                'is_active': False,  # À activer pour salaires > 4005€
                'is_patronal': False,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': PMSS,  # Commence au-dessus de T1
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': True
            },
            {
                'name': 'CEG (Contribution d\'Équilibre Général)',
                'rate': Decimal('0.86'),
                'ceiling': PMSS,  # T1 uniquement
                'description': 'Contribution équilibre général Agirc-Arrco T1',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': None,
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': True
            },
            {
                'name': 'CEG T2',
                'rate': Decimal('1.08'),
                'ceiling': PASS_8,  # T2
                'description': 'Contribution équilibre général Agirc-Arrco T2',
                'is_active': False,  # À activer pour salaires > 4005€
                'is_patronal': False,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': PMSS,
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': True
            },
            {
                'name': 'CSG déductible',
                'rate': Decimal('6.80'),
                'ceiling': None,
                'description': 'CSG déductible - 6.80% sur 98.25% du brut (soit 6.68% effectif)',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'ABATTUE_9825',  # 🔑 ASSIETTE SPÉCIALE
                'tranche_min': None,
                'organisme': 'URSSAF',
                'deductible_fiscalement': True  # Réduit l'impôt
            },
            {
                'name': 'CSG non déductible',
                'rate': Decimal('2.40'),
                'ceiling': None,
                'description': 'CSG non déductible - 2.40% sur 98.25% du brut (soit 2.36% effectif)',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'ABATTUE_9825',  # 🔑 ASSIETTE SPÉCIALE
                'tranche_min': None,
                'organisme': 'URSSAF',
                'deductible_fiscalement': False  # N'impacte pas l'impôt
            },
            {
                'name': 'CRDS',
                'rate': Decimal('0.50'),
                'ceiling': None,
                'description': 'CRDS - 0.50% sur 98.25% du brut (soit 0.49% effectif)',
                'is_active': True,
                'is_patronal': False,
                'assiette_type': 'ABATTUE_9825',  # 🔑 ASSIETTE SPÉCIALE
                'tranche_min': None,
                'organisme': 'URSSAF',
                'deductible_fiscalement': False  # Jamais déductible
            },
            
            # --- PRÉVOYANCE / MUTUELLE (optionnelles mais courantes) ---
            {
                'name': 'Mutuelle santé obligatoire',
                'rate': Decimal('2.50'),
                'ceiling': None,
                'description': 'Mutuelle d\'entreprise - part salariale (taux indicatif à adapter)',
                'is_active': False,
                'is_patronal': False
            },
            {
                'name': 'Prévoyance',
                'rate': Decimal('0.75'),
                'ceiling': None,
                'description': 'Assurance prévoyance (décès/invalidité) - part salariale',
                'is_active': False,
                'is_patronal': False
            },
            
            # ===== COTISATIONS PATRONALES (à charge de l'employeur) =====
            
            # --- ASSURANCE MALADIE ---
            {
                'name': 'Assurance maladie',
                'rate': Decimal('13.00'),
                'ceiling': None,
                'description': 'Maladie-maternité-invalidité-décès - taux général (ou 7% si ≤2.5 SMIC)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- ASSURANCE VIEILLESSE PATRONALE ---
            {
                'name': 'Vieillesse plafonnée patronale',
                'rate': Decimal('8.55'),
                'ceiling': PMSS,
                'description': 'Assurance vieillesse patronale - tranche 1 (≤ PASS)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            {
                'name': 'Vieillesse déplafonnée patronale',
                'rate': Decimal('1.90'),
                'ceiling': None,
                'description': 'Assurance vieillesse patronale - part déplafonnée',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- ALLOCATIONS FAMILIALES ---
            {
                'name': 'Allocations familiales',
                'rate': Decimal('3.45'),
                'ceiling': None,
                'description': 'Allocations familiales - taux réduit (5.25% si ≥ 3.5 SMIC)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- ASSURANCE CHÔMAGE PATRONALE ---
            {
                'name': 'Assurance chômage patronale',
                'rate': Decimal('4.05'),
                'ceiling': PASS_4,  # 4 PASS
                'description': 'Pôle Emploi - contribution employeur (≤ 4 PASS)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'organisme': 'POLE_EMPLOI',
                'deductible_fiscalement': False
            },
            
            # --- AGS (Garantie des salaires) ---
            {
                'name': 'AGS (Garantie des salaires)',
                'rate': Decimal('0.15'),
                'ceiling': PASS_4,  # 4 PASS
                'description': 'Association pour la Gestion du régime de garantie des Salaires',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'organisme': 'AUTRE',
                'deductible_fiscalement': False
            },
            
            # --- RETRAITE COMPLÉMENTAIRE PATRONALE ---
            {
                'name': 'Retraite complémentaire T1 patronale',
                'rate': Decimal('4.72'),
                'ceiling': PMSS,
                'description': 'Agirc-Arrco T1 patronal (taux total 6.20% - part patronale 4.72%)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': False
            },
            {
                'name': 'Retraite complémentaire T2 patronale',
                'rate': Decimal('12.95'),
                'ceiling': PASS_8,
                'description': 'Agirc-Arrco T2 patronal (taux total 17.00% - part patronale 12.95%)',
                'is_active': False,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': PMSS,
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': False
            },
            {
                'name': 'CEG patronale T1',
                'rate': Decimal('1.29'),
                'ceiling': PMSS,
                'description': 'Contribution équilibre général Agirc-Arrco T1 - part patronale',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': False
            },
            {
                'name': 'CEG patronale T2',
                'rate': Decimal('1.62'),
                'ceiling': PASS_8,
                'description': 'Contribution équilibre général Agirc-Arrco T2 - part patronale',
                'is_active': False,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'tranche_min': PMSS,
                'organisme': 'AGIRC_ARRCO',
                'deductible_fiscalement': False
            },
            
            # --- FNAL (Fonds National Aide au Logement) ---
            {
                'name': 'FNAL tranche 1',
                'rate': Decimal('0.10'),
                'ceiling': PMSS,
                'description': 'FNAL - Fonds National d\'Aide au Logement (≤ PASS)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'PLAFONNEE',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            {
                'name': 'FNAL tranche 2',
                'rate': Decimal('0.50'),
                'ceiling': None,
                'description': 'FNAL supplémentaire (entreprises ≥50 salariés) - totalité salaire',
                'is_active': False,  # Activer si ≥50 salariés
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- CONTRIBUTION SOLIDARITÉ AUTONOMIE ---
            {
                'name': 'Contribution solidarité autonomie',
                'rate': Decimal('0.30'),
                'ceiling': None,
                'description': 'CSA - Contribution Solidarité Autonomie (personnes âgées/handicapées)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- FORMATION PROFESSIONNELLE ---
            {
                'name': 'Formation professionnelle',
                'rate': Decimal('1.00'),
                'ceiling': None,
                'description': 'Contribution formation continue (1% si ≥11 salariés, 0.55% si <11)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- TAXE D'APPRENTISSAGE ---
            {
                'name': 'Taxe d\'apprentissage',
                'rate': Decimal('0.68'),
                'ceiling': None,
                'description': 'Taxe d\'apprentissage (0.68% masse salariale)',
                'is_active': True,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- CONTRIBUTION UNIQUE FORMATION PROFESSIONNELLE & ALTERNANCE ---
            {
                'name': 'Contribution CPF-CDD',
                'rate': Decimal('1.00'),
                'ceiling': None,
                'description': 'Contribution CPF pour les CDD (1% masse salariale CDD)',
                'is_active': False,  # Uniquement pour CDD
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- VERSEMENT MOBILITÉ (ex-Versement Transport) ---
            {
                'name': 'Versement mobilité',
                'rate': Decimal('1.80'),
                'ceiling': None,
                'description': 'Versement transport/mobilité (varie selon commune - taux indicatif Paris)',
                'is_active': False,  # À activer selon localisation
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'URSSAF',
                'deductible_fiscalement': False
            },
            
            # --- COMPLÉMENTAIRES OPTIONNELLES ---
            {
                'name': 'Mutuelle santé patronale',
                'rate': Decimal('2.50'),
                'ceiling': None,
                'description': 'Mutuelle d\'entreprise - part patronale (≥50% prise en charge légale)',
                'is_active': False,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'AUTRE',
                'deductible_fiscalement': False
            },
            {
                'name': 'Prévoyance patronale',
                'rate': Decimal('1.25'),
                'ceiling': None,
                'description': 'Assurance prévoyance - part patronale',
                'is_active': False,
                'is_patronal': True,
                'assiette_type': 'BRUT',
                'organisme': 'AUTRE',
                'deductible_fiscalement': False
            },
        ]

        # Créer les variables
        created_vars = 0
        for var_data in variables:
            var, created = PayrollVariable.objects.update_or_create(
                name=var_data['name'],
                defaults={
                    'value': var_data['value'],
                    'unit': var_data['unit'],
                    'description': var_data['description'],
                    'is_active': var_data['is_active']
                }
            )
            if created:
                created_vars += 1
                self.stdout.write(f"  ✓ Variable créée: {var.name}")
            else:
                self.stdout.write(f"  ↻ Variable mise à jour: {var.name}")

        # Créer les cotisations
        created_contribs = 0
        for contrib_data in contributions:
            contrib, created = PayrollContribution.objects.update_or_create(
                name=contrib_data['name'],
                defaults={
                    'rate': contrib_data['rate'],
                    'ceiling': contrib_data['ceiling'],
                    'description': contrib_data['description'],
                    'is_active': contrib_data['is_active'],
                    'is_patronal': contrib_data['is_patronal'],
                    'assiette_type': contrib_data.get('assiette_type', 'BRUT'),
                    'tranche_min': contrib_data.get('tranche_min'),
                    'organisme': contrib_data.get('organisme', 'URSSAF'),
                    'deductible_fiscalement': contrib_data.get('deductible_fiscalement', False)
                }
            )
            if created:
                created_contribs += 1
                self.stdout.write(f"  ✓ Cotisation créée: {contrib.name}")
            else:
                self.stdout.write(f"  ↻ Cotisation mise à jour: {contrib.name}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Initialisation terminée!"))
        self.stdout.write(f"   {created_vars} variables de paie")
        self.stdout.write(f"   {created_contribs} cotisations sociales")
        self.stdout.write(self.style.WARNING("\n💡 Les taux peuvent être modifiés via Paie > Variables & Cotisations"))
