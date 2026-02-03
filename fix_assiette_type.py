"""
Correction rapide des assiette_type pour les cotisations plafonnées
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from payroll.models import PayrollContribution

print("=" * 100)
print("🔧 CORRECTION DES ASSIETTE_TYPE")
print("=" * 100)
print()

# Liste des cotisations qui doivent avoir assiette_type='PLAFONNEE'
cotisations_plafonnees = [
    'Vieillesse plafonnée (T1)',
    'Assurance chômage',
    'Retraite complémentaire T1',
    'Retraite complémentaire T2',
    'CEG (Contribution d\'Équilibre Général)',
    'CEG T2'
]

for nom in cotisations_plafonnees:
    contrib = PayrollContribution.objects.filter(name=nom).first()
    if contrib:
        old_type = contrib.assiette_type
        contrib.assiette_type = 'PLAFONNEE'
        contrib.save()
        print(f"✅ {nom}")
        print(f"   {old_type} → PLAFONNEE")
    else:
        print(f"❌ {nom} : NON TROUVÉE")
    print()

print("=" * 100)
print("✅ Correction terminée - Relancez vos calculs")
print("=" * 100)
