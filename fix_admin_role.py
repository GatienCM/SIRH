#!/usr/bin/env python
"""Script pour mettre à jour le rôle de l'utilisateur admin"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from accounts.models import CustomUser

try:
    user = CustomUser.objects.get(username='admin')
    print(f'Utilisateur trouvé: {user.username}')
    print(f'Rôle actuel: {user.role}')
    
    if user.role != 'admin':
        user.role = 'admin'
        user.save()
        print(f'✅ Rôle mis à jour: {user.role}')
    else:
        print('✅ Le rôle est déjà défini sur "admin"')
        
except CustomUser.DoesNotExist:
    print('❌ Utilisateur "admin" non trouvé')
