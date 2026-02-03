"""
Recalcul de tous les bulletins de paie avec les cotisations corrigées
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from payroll.models import Payroll

print("=" * 100)
print("🔄 RECALCUL DES BULLETINS DE PAIE")
print("=" * 100)
print()

bulletins = Payroll.objects.all().order_by('-year', '-month')

if not bulletins:
    print("❌ Aucun bulletin trouvé")
else:
    print(f"📋 {bulletins.count()} bulletin(s) trouvé(s)")
    print()
    
    for payroll in bulletins:
        old_deductions = payroll.total_deductions
        old_net = payroll.net_salary
        
        # Supprimer les anciens items
        payroll.items.all().delete()
        
        # Recalculer
        payroll.calculate_with_payroll_rules()
        
        new_deductions = payroll.total_deductions
        new_net = payroll.net_salary
        
        print(f"✅ {payroll.employee.user.get_full_name()} - {payroll.period}")
        print(f"   Salaire brut : {payroll.gross_salary}€")
        print(f"   Cotisations : {old_deductions:.2f}€ → {new_deductions:.2f}€")
        print(f"   Net : {old_net:.2f}€ → {new_net:.2f}€")
        print(f"   Taux effectif : {(new_deductions / payroll.gross_salary * 100):.2f}%")
        print()

print("=" * 100)
print("✅ Recalcul terminé - Actualisez la page pour voir les modifications")
print("=" * 100)
