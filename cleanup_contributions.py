#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from payroll.models import PayrollContribution

# Supprimer l'ancienne cotisation mal nommée
old = PayrollContribution.objects.filter(name__icontains='Cotisations patronales URSSAF')
if old.exists():
    print(f'Suppression de {old.count()} cotisation(s) mal nommée(s)')
    old.delete()

# Afficher toutes les cotisations pour vérifier
print('\n✅ Cotisations actuelles:')
for c in PayrollContribution.objects.all().order_by('name'):
    patronal = '[PATRONALE]' if c.is_patronal else '[SALARIALE]'
    print(f'  {c.name:45} {patronal:12} {c.rate:6.2f}%')
