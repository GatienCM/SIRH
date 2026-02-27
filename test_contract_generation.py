"""
Script de test pour la génération de contrats
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from contracts.models import Contract
from contracts.utils import generate_contract_document


def test_contract_generation():
    """Test de génération d'un contrat"""
    
    # Récupérer le premier contrat disponible
    contracts = Contract.objects.all()
    
    if not contracts.exists():
        print("[ERREUR] Aucun contrat trouve dans la base de donnees")
        print("Creez d'abord un contrat via l'interface admin")
        return
    
    for contract in contracts[:3]:  # Tester les 3 premiers contrats
        print(f"\n{'='*60}")
        print(f"Test du contrat: {contract.contract_number}")
        print(f"  - Employe: {contract.employee}")
        print(f"  - Type: {contract.get_contract_type_display()}")
        print(f"  - Entite: {contract.entity_template or 'nantes_urgences'}")
        print(f"  - Genre: {contract.employee.gender}")
        print(f"{'='*60}")
        
        try:
            # Générer le document
            filename, file_content = generate_contract_document(contract)
            
            # Sauvegarder temporairement pour vérification
            test_output_dir = os.path.join('media', 'test_contracts')
            os.makedirs(test_output_dir, exist_ok=True)
            
            output_path = os.path.join(test_output_dir, filename)
            with open(output_path, 'wb') as f:
                f.write(file_content)
            
            print(f"[OK] Document genere avec succes!")
            print(f"   Fichier: {filename}")
            print(f"   Taille: {len(file_content) / 1024:.2f} Ko")
            print(f"   Chemin: {output_path}")
            
            # Afficher le contexte utilisé
            print(f"\n   Donnees employe:")
            print(f"   - Nom: {contract.employee.user.first_name} {contract.employee.user.last_name}")
            print(f"   - Date naissance: {contract.employee.birth_date}")
            print(f"   - Lieu naissance: {contract.employee.birth_place}")
            print(f"   - N SS: {contract.employee.social_security_number}")
            print(f"   - Adresse : {contract.employee.address}")
            
            print(f"\n   Donnees contrat:")
            print(f"   - Date debut: {contract.start_date}")
            print(f"   - Date fin: {contract.end_date}")
            print(f"   - Periode essai: {contract.trial_end_date}")
            print(f"   - Taux horaire: {contract.hourly_rate} euros")
            print(f"   - Salaire mensuel: {contract.monthly_salary} euros")
            
        except FileNotFoundError as e:
            print(f"[ERREUR] Template introuvable: {e}")
        except Exception as e:
            print(f"[ERREUR] Erreur lors de la generation: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    print("="*60)
    print("TEST DE GÉNÉRATION DE CONTRATS")
    print("="*60)
    test_contract_generation()
    print("\n" + "="*60)
    print("FIN DES TESTS")
    print("="*60)
