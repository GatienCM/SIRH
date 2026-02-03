from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Vehicle

User = get_user_model()


class VehicleTestCase(TestCase):
    """Tests pour le modèle Vehicle"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.vehicle = Vehicle.objects.create(
            vehicle_id='VEH-001',
            registration_number='AB-123-CD',
            vehicle_type='ambulance',
            brand='Mercedes',
            model='Sprinter',
            year=2022,
            seats_count=3,
            stretcher_capacity=1,
            purchase_date='2022-01-15',
            entry_date='2022-02-01',
            status='available',
            created_by=self.user
        )
    
    def test_vehicle_creation(self):
        """Vérifie qu'un véhicule peut être créé"""
        self.assertEqual(self.vehicle.vehicle_id, 'VEH-001')
        self.assertEqual(self.vehicle.vehicle_type, 'ambulance')
        self.assertTrue(self.vehicle.is_available)
    
    def test_vehicle_str(self):
        """Teste la représentation en string"""
        expected = 'VEH-001 - Mercedes Sprinter (AB-123-CD)'
        self.assertEqual(str(self.vehicle), expected)
    
    def test_vehicle_age_calculation(self):
        """Vérifie le calcul de l'âge du véhicule"""
        age = self.vehicle.age_years
        self.assertGreaterEqual(age, 3)  # En 2026, il a au moins 3 ans
    
    def test_vehicle_mileage(self):
        """Vérifie le calcul du kilométrage"""
        self.vehicle.initial_mileage = 1000
        self.vehicle.current_mileage = 5000
        self.vehicle.save()
        self.assertEqual(self.vehicle.total_mileage, 4000)
    
    def test_vehicle_maintenance_needed(self):
        """Vérifie la propriété is_maintenance_needed"""
        self.vehicle.next_maintenance_date = timezone.now().date()
        self.assertTrue(self.vehicle.is_maintenance_needed)
