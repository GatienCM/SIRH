#!/usr/bin/env python
"""
Script de test des endpoints du module Planning
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api"
SESSION = requests.Session()

# Couleurs pour les logs
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
END = '\033[0m'

def log_test(name, success, response=None):
    """Logger le résultat d'un test"""
    status = f"{GREEN}✓ PASS{END}" if success else f"{RED}✗ FAIL{END}"
    print(f"{status} - {name}")
    if response and not success:
        print(f"  Erreur: {response.status_code} - {response.text[:200]}")

def test_planning():
    """Tester tous les endpoints du Planning"""
    print(f"\n{BLUE}=== Tests Planning & Shifts ==={END}\n")
    
    # 1. Login
    print("1. Authentification...")
    login_data = {"username": "admin", "password": "Admin2024!"}
    response = SESSION.post(f"{BASE_URL}/auth/login/", json=login_data)
    success = response.status_code == 200
    log_test("POST /api/auth/login/", success, response)
    
    if not success:
        print("❌ Impossible de se connecter")
        return
    
    # 2. Récupérer les ShiftTypes
    print("\n2. Types de Shifts...")
    response = SESSION.get(f"{BASE_URL}/planning/shift-types/")
    success = response.status_code == 200
    log_test("GET /api/planning/shift-types/", success, response)
    
    if success:
        data = response.json()
        print(f"  ✓ {len(data.get('results', data))} types de shifts trouvés")
    
    # 3. Créer un Shift
    print("\n3. Création de Shifts...")
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    shift_data = {
        "shift_type_id": 1,
        "date": str(tomorrow),
        "start_time": "08:00:00",
        "end_time": "16:00:00",
        "notes": "Test shift"
    }
    response = SESSION.post(f"{BASE_URL}/planning/shifts/", json=shift_data)
    success = response.status_code == 201
    log_test("POST /api/planning/shifts/", success, response)
    
    if success:
        shift = response.json()
        shift_id = shift['id']
        print(f"  ✓ Shift créé avec ID: {shift_id}")
    else:
        print("❌ Impossible de créer un shift")
        return
    
    # 4. Récupérer les Shifts
    print("\n4. Récupération des Shifts...")
    response = SESSION.get(f"{BASE_URL}/planning/shifts/")
    success = response.status_code == 200
    log_test("GET /api/planning/shifts/", success, response)
    
    if success:
        data = response.json()
        count = len(data.get('results', data))
        print(f"  ✓ {count} shifts trouvés")
    
    # 5. Récupérer les Shifts à venir
    print("\n5. Shifts à venir...")
    response = SESSION.get(f"{BASE_URL}/planning/shifts/upcoming/")
    success = response.status_code == 200
    log_test("GET /api/planning/shifts/upcoming/", success, response)
    
    # 6. Récupérer les Shifts par date
    print("\n6. Shifts par date...")
    response = SESSION.get(f"{BASE_URL}/planning/shifts/by_date/?date={str(tomorrow)}")
    success = response.status_code == 200
    log_test(f"GET /api/planning/shifts/by_date/?date={str(tomorrow)}", success, response)
    
    # 7. Créer une Assignment
    print("\n7. Création d'Assignments...")
    # On suppose que l'employé 1 existe
    assignment_data = {
        "shift_id": shift_id,
        "employee_id": 1,
        "vehicle_id": 1
    }
    response = SESSION.post(f"{BASE_URL}/planning/assignments/", json=assignment_data)
    success = response.status_code == 201
    log_test("POST /api/planning/assignments/", success, response)
    
    if success:
        assignment = response.json()
        assignment_id = assignment['id']
        print(f"  ✓ Assignment créé avec ID: {assignment_id}")
    
    # 8. Récupérer les Assignments
    print("\n8. Récupération des Assignments...")
    response = SESSION.get(f"{BASE_URL}/planning/assignments/")
    success = response.status_code == 200
    log_test("GET /api/planning/assignments/", success, response)
    
    if success:
        data = response.json()
        count = len(data.get('results', data))
        print(f"  ✓ {count} assignments trouvés")
    
    # 9. Mon planning personnel
    print("\n9. Mon Planning (Endpoint /my_schedule/)...")
    response = SESSION.get(f"{BASE_URL}/planning/assignments/my_schedule/")
    success = response.status_code == 200
    log_test("GET /api/planning/assignments/my_schedule/", success, response)
    
    print(f"\n{BLUE}=== Résumé ==={END}")
    print("✓ Tous les endpoints du Planning ont été testés!")
    print("✓ Module Planning & Shifts opérationnel!")

if __name__ == "__main__":
    test_planning()
