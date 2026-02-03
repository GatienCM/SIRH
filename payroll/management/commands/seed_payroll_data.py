from django.core.management.base import BaseCommand
from decimal import Decimal
from payroll.models import PayrollVariable, PayrollContribution


class Command(BaseCommand):
    help = "Seed payroll variables and contributions with French legal rates"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔄 Initialisation des variables et cotisations obligatoires..."))

        # ========== VARIABLES DE PAIE ==========
        variables = [
            {
                'name': 'Taux horaire SMIC',
                'value': Decimal('11.65'),
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
        contributions = [
            {
                'name': 'URSSAF - Cotisation salariale',
                'rate': Decimal('8.03'),
                'ceiling': Decimal('3666.67'),
                'description': 'Assurance maladie, maternité, invalidité, décès (salarié) - Taux réduit < SMIC+43%',
                'is_active': True
            },
            {
                'name': 'CSG non déductible',
                'rate': Decimal('2.40'),
                'ceiling': None,
                'description': 'Contribution Sociale Généralisée non déductible - s/assiette brute',
                'is_active': True
            },
            {
                'name': 'CSG déductible',
                'rate': Decimal('5.10'),
                'ceiling': None,
                'description': 'Contribution Sociale Généralisée déductible - s/assiette brute',
                'is_active': True
            },
            {
                'name': 'CRDS',
                'rate': Decimal('0.95'),
                'ceiling': None,
                'description': 'Contribution au Remboursement de la Dette Sociale',
                'is_active': True
            },
            {
                'name': 'Retraite complémentaire (Agirc-Arrco)',
                'rate': Decimal('6.20'),
                'ceiling': Decimal('14999.00'),
                'description': 'Cotisation retraite complémentaire obligatoire - sur assiette plafonnée',
                'is_active': True
            },
            {
                'name': 'Cotisations patronales URSSAF',
                'rate': Decimal('42.0'),
                'ceiling': None,
                'description': 'Cotisations patronales sociales et allocations familiales (coût pour employeur)',
                'is_active': True
            },
            {
                'name': 'Mutuelle santé',
                'rate': Decimal('4.0'),
                'ceiling': None,
                'description': 'Mutuelle obligatoire - taux moyen (à adapter)',
                'is_active': False
            },
            {
                'name': 'Prévoyance',
                'rate': Decimal('1.5'),
                'ceiling': None,
                'description': 'Assurance prévoyance - taux moyen (à adapter)',
                'is_active': False
            },
            {
                'name': 'Cotisation retraite additionnelle',
                'rate': Decimal('0.50'),
                'ceiling': None,
                'description': 'Cotisation retraite supplémentaire (facultatif)',
                'is_active': False
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
                    'is_active': contrib_data['is_active']
                }
            )
            if created:
                created_contribs += 1
                self.stdout.write(f"  ✓ Cotisation créée: {contrib.name}")
            else:
                self.stdout.write(f"  ↻ Cotisation mise à jour: {contrib.name}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Initialistion terminée!"))
        self.stdout.write(f"   {created_vars} variables de paie")
        self.stdout.write(f"   {created_contribs} cotisations sociales")
        self.stdout.write(self.style.WARNING("\n💡 Les taux peuvent être modifiés via Paie > Variables & Cotisations"))
