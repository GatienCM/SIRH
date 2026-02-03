from django.test import TestCase
from django.utils import timezone
from datetime import time, timedelta
from django.contrib.auth import get_user_model
from employees.models import Employee, Profession
from contracts.models import Contract
from vehicles.models import Vehicle
from .models import ShiftType, Shift, Assignment

User = get_user_model()


class ShiftTypeTestCase(TestCase):
    """Tests pour ShiftType"""
    
    def setUp(self):
        """Créer les données de test"""
        self.shift_type = ShiftType.objects.create(
            name='day',
            description='Shift de jour',
            start_hour=time(8, 0),
            end_hour=time(16, 0),
            base_hours=8
        )
    
    def test_create_shift_type(self):
        """Tester la création d'un type de shift"""
        self.assertEqual(ShiftType.objects.count(), 1)
        self.assertEqual(self.shift_type.name, 'day')
        self.assertEqual(self.shift_type.base_hours, 8)
    
    def test_shift_type_str(self):
        """Tester la représentation string"""
        self.assertEqual(str(self.shift_type), 'Jour')


class ShiftTestCase(TestCase):
    """Tests pour Shift"""
    
    def setUp(self):
        """Créer les données de test"""
        self.user = User.objects.create_user(
            username='admin',
            password='test123',
            role='admin'
        )
        
        self.shift_type = ShiftType.objects.create(
            name='day',
            start_hour=time(8, 0),
            end_hour=time(16, 0),
            base_hours=8
        )
        
        self.shift = Shift.objects.create(
            shift_type=self.shift_type,
            date=timezone.now().date() + timedelta(days=1),
            start_time=time(8, 0),
            end_time=time(16, 0),
            created_by=self.user
        )
    
    def test_create_shift(self):
        """Tester la création d'un shift"""
        self.assertEqual(Shift.objects.count(), 1)
        self.assertEqual(self.shift.status, 'planned')
    
    def test_shift_duration(self):
        """Tester le calcul de la durée"""
        self.assertEqual(self.shift.duration_hours, 8)
    
    def test_invalid_shift_times(self):
        """Tester que les heures invalides sont rejetées"""
        from django.core.exceptions import ValidationError
        invalid_shift = Shift(
            shift_type=self.shift_type,
            date=timezone.now().date(),
            start_time=time(16, 0),
            end_time=time(8, 0),
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            invalid_shift.full_clean()


class AssignmentTestCase(TestCase):
    """Tests pour Assignment"""
    
    def setUp(self):
        """Créer les données de test"""
        # Créer utilisateur
        self.user = User.objects.create_user(
            username='employee1',
            password='test123',
            role='employee'
        )
        
        # Créer profession et employé
        self.profession = Profession.objects.create(
            name='ambulancier_dea',
            label='Ambulancier DEA'
        )
        
        self.employee = Employee.objects.create(
            user=self.user,
            profession=self.profession
        )
        
        # Créer contrat actif
        self.contract = Contract.objects.create(
            employee=self.employee,
            contract_type='CDI',
            start_date=timezone.now().date(),
            salary=2000
        )
        
        # Créer véhicule
        self.vehicle = Vehicle.objects.create(
            registration='75-ABC-123',
            vehicle_type='ambulance'
        )
        
        # Créer shift type et shift
        self.shift_type = ShiftType.objects.create(
            name='day',
            start_hour=time(8, 0),
            end_hour=time(16, 0),
            base_hours=8
        )
        
        admin_user = User.objects.create_user(
            username='admin',
            password='test123',
            role='admin'
        )
        
        self.shift = Shift.objects.create(
            shift_type=self.shift_type,
            date=timezone.now().date() + timedelta(days=1),
            start_time=time(8, 0),
            end_time=time(16, 0),
            created_by=admin_user
        )
    
    def test_create_assignment(self):
        """Tester la création d'une assignation"""
        assignment = Assignment.objects.create(
            shift=self.shift,
            employee=self.employee,
            vehicle=self.vehicle
        )
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertEqual(assignment.status, 'assigned')
    
    def test_unique_assignment_constraint(self):
        """Tester que l'employé ne peut pas avoir deux assignations le même jour"""
        from django.core.exceptions import ValidationError
        
        # Première assignation
        Assignment.objects.create(
            shift=self.shift,
            employee=self.employee,
            vehicle=self.vehicle
        )
        
        # Créer deuxième shift le même jour
        shift2 = Shift.objects.create(
            shift_type=self.shift_type,
            date=self.shift.date,
            start_time=time(16, 0),
            end_time=time(20, 0),
            created_by=self.shift.created_by
        )
        
        # Essayer de créer une deuxième assignation le même jour
        assignment2 = Assignment(
            shift=shift2,
            employee=self.employee,
            vehicle=self.vehicle
        )
        
        with self.assertRaises(ValidationError):
            assignment2.full_clean()
    
    def test_confirm_assignment(self):
        """Tester la confirmation d'une assignation"""
        assignment = Assignment.objects.create(
            shift=self.shift,
            employee=self.employee,
            vehicle=self.vehicle
        )
        assignment.status = 'confirmed'
        assignment.confirmed_at = timezone.now()
        assignment.save()
        
        self.assertTrue(assignment.is_confirmed)
