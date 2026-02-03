from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserTestCase(TestCase):
    """Tests pour le modèle CustomUser"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123',
            role='employee'
        )
    
    def test_user_creation(self):
        """Vérifie qu'un utilisateur peut être créé"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'employee')
        self.assertEqual(self.user.get_role_display(), 'Salarié')
    
    def test_user_str(self):
        """Teste la représentation en string"""
        expected = 'Test User (Salarié)'
        self.assertEqual(str(self.user), expected)
    
    def test_superuser_creation(self):
        """Vérifie qu'un superuser peut être créé"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
