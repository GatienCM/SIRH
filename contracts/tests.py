from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from employees.models import Profession, Employee
from .models import Contract

User = get_user_model()


class ContractTestCase(TestCase):
    """Tests pour le modèle Contract"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='emp001',
            email='emp@example.com',
            first_name='Jean',
            last_name='Dupont',
            password='pass123'
        )
        
        self.profession = Profession.objects.create(
            code='ambulancier_dea',
            label='Ambulancier DEA'
        )
        
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            birth_date='1990-05-15',
            address='123 Rue de la Paix',
            postal_code='75000',
            city='Paris',
            phone='+33612345678',
            social_security_number='1900512345678',
            profession=self.profession,
            date_entry=timezone.now().date()
        )
        
        self.contract = Contract.objects.create(
            employee=self.employee,
            contract_number='CDI-2024-001',
            contract_type='cdi',
            status='active',
            start_date=timezone.now().date(),
            working_hours_per_week=35.0,
            hourly_rate=12.50
        )
    
    def test_contract_creation(self):
        """Vérifie qu'un contrat peut être créé"""
        self.assertEqual(self.contract.contract_number, 'CDI-2024-001')
        self.assertEqual(self.contract.contract_type, 'cdi')
        self.assertTrue(self.contract.is_active)
    
    def test_contract_uniqueness_per_employee(self):
        """Vérifie qu'un salarié ne peut avoir qu'un contrat actif"""
        with self.assertRaises(ValidationError):
            Contract.objects.create(
                employee=self.employee,
                contract_number='CDI-2024-002',
                contract_type='cdi',
                status='active',
                start_date=timezone.now().date(),
                hourly_rate=12.50
            )
    
    def test_contract_invalid_dates(self):
        """Vérifie que les dates invalides sont rejetées"""
        with self.assertRaises(ValidationError):
            Contract.objects.create(
                employee=self.employee,
                contract_number='CDD-2024-001',
                contract_type='cdd',
                status='active',
                start_date=timezone.now().date(),
                end_date=timezone.now().date() - timezone.timedelta(days=1),
                hourly_rate=12.50
            )
