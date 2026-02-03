from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Profession, Employee

User = get_user_model()


class ProfessionTestCase(TestCase):
    """Tests pour le modèle Profession"""
    
    def setUp(self):
        self.profession = Profession.objects.create(
            code='ambulancier_dea',
            label='Ambulancier DEA',
            description='Professionnel du transport sanitaire avec DEA'
        )
    
    def test_profession_creation(self):
        """Vérifie qu'une profession peut être créée"""
        self.assertEqual(self.profession.label, 'Ambulancier DEA')
        self.assertTrue(self.profession.is_active)
    
    def test_profession_str(self):
        """Teste la représentation en string"""
        self.assertEqual(str(self.profession), 'Ambulancier DEA')


class EmployeeTestCase(TestCase):
    """Tests pour le modèle Employee"""
    
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
    
    def test_employee_creation(self):
        """Vérifie qu'un salarié peut être créé"""
        self.assertEqual(self.employee.employee_id, 'EMP001')
        self.assertEqual(self.employee.status, 'active')
    
    def test_employee_age_calculation(self):
        """Vérifie le calcul de l'âge"""
        age = self.employee.age
        self.assertGreater(age, 0)
    
    def test_is_active_employee(self):
        """Vérifie la propriété is_active_employee"""
        self.assertTrue(self.employee.is_active_employee())
