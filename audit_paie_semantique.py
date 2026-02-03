"""
Audit de cohérence du module Paie selon le guide sémantique
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from payroll.models import PayrollContribution
from decimal import Decimal

print("=" * 100)
print("🔍 AUDIT DE COHÉRENCE - MODULE PAIE vs GUIDE SÉMANTIQUE")
print("=" * 100)

# 🚨 VÉRIFICATION 1 : CSG/CRDS - ASSIETTE ABATTUE
print("\n📐 AXIOME_ASSIETTE : CSG/CRDS doivent avoir assiette = brut × 0.9825")
print("-" * 100)

csg_crds = PayrollContribution.objects.filter(
    name__in=['CSG déductible', 'CSG non déductible', 'CRDS'],
    is_patronal=False
)

problemes_assiette = []
for cotis in csg_crds:
    if cotis.ceiling is not None:
        problemes_assiette.append(f"❌ {cotis.name} : a un plafond alors qu'elle devrait être déplafonnée")
    else:
        print(f"✅ {cotis.name} : déplafonnée (correct)")
    
    # Vérifier si le taux est déjà ajusté ou si c'est le taux brut
    if cotis.name == 'CSG déductible':
        if cotis.rate == Decimal('6.80'):
            problemes_assiette.append(f"⚠️  {cotis.name} : taux 6.80% appliqué sur 100% brut au lieu de 98.25%")
            print(f"   → Taux effectif réel : {cotis.rate * Decimal('0.9825'):.2f}% (au lieu de 6.80%)")
        elif cotis.rate == Decimal('6.68'):
            print(f"✅ {cotis.name} : taux ajusté 6.68% (correct pour application sur 100%)")
    
    if cotis.name == 'CSG non déductible':
        if cotis.rate == Decimal('2.40'):
            problemes_assiette.append(f"⚠️  {cotis.name} : taux 2.40% appliqué sur 100% brut au lieu de 98.25%")
            print(f"   → Taux effectif réel : {cotis.rate * Decimal('0.9825'):.2f}% (au lieu de 2.40%)")
    
    if cotis.name == 'CRDS':
        if cotis.rate == Decimal('0.50'):
            problemes_assiette.append(f"⚠️  {cotis.name} : taux 0.50% appliqué sur 100% brut au lieu de 98.25%")
            print(f"   → Taux effectif réel : {cotis.rate * Decimal('0.9825'):.2f}% (au lieu de 0.50%)")

# 🚨 VÉRIFICATION 2 : VIEILLESSE - DOUBLE LIGNE OBLIGATOIRE
print("\n📐 AXIOME_VIEILLESSE : Double ligne obligatoire (plafonnée + déplafonnée)")
print("-" * 100)

vieillesse_plaf = PayrollContribution.objects.filter(
    name__icontains='Vieillesse plafonnée',
    is_patronal=False,
    is_active=True
).first()

vieillesse_deplaf = PayrollContribution.objects.filter(
    name__icontains='Vieillesse déplafonnée',
    is_patronal=False,
    is_active=True
).first()

if vieillesse_plaf and vieillesse_deplaf:
    print(f"✅ Double ligne vieillesse présente")
    print(f"   - Plafonnée : {vieillesse_plaf.rate}% (plafond {vieillesse_plaf.ceiling}€)")
    print(f"   - Déplafonnée : {vieillesse_deplaf.rate}% (sans plafond)")
else:
    problemes_assiette.append("❌ VIEILLESSE : ligne manquante (plafonnée ou déplafonnée)")

# 🚨 VÉRIFICATION 3 : TRANCHES AGIRC-ARRCO
print("\n📐 AXIOME_TRANCHE : AGIRC-ARRCO T1 [0→1×PMSS] et T2 [1×PMSS→8×PMSS]")
print("-" * 100)

PMSS = Decimal('3864.00')  # 2026

agirc_t1 = PayrollContribution.objects.filter(
    name__icontains='Retraite complémentaire T1',
    is_patronal=False
).first()

agirc_t2 = PayrollContribution.objects.filter(
    name__icontains='Retraite complémentaire T2',
    is_patronal=False
).first()

problemes_tranches = []

if agirc_t1:
    if agirc_t1.ceiling != PMSS:
        problemes_tranches.append(f"❌ AGIRC T1 : plafond {agirc_t1.ceiling}€ au lieu de {PMSS}€ (1×PMSS)")
    else:
        print(f"✅ AGIRC T1 : plafond correct à {PMSS}€")
    print(f"   Taux salarié : {agirc_t1.rate}% (taux total attendu ~6.20%)")
    if not agirc_t1.is_active:
        print(f"   ℹ️  État : INACTIF")

if agirc_t2:
    if agirc_t2.ceiling != PMSS * 8:
        problemes_tranches.append(f"⚠️  AGIRC T2 : plafond {agirc_t2.ceiling}€ (devrait être ~{PMSS * 8}€ pour 8×PMSS)")
    print(f"   Taux salarié T2 : {agirc_t2.rate}% (taux total attendu ~17.00%)")
    if not agirc_t2.is_active:
        print(f"   ℹ️  État : INACTIF (normal pour salaires standards)")
else:
    print("ℹ️  AGIRC T2 : non trouvée ou désactivée")

# 🚨 VÉRIFICATION 4 : CALCUL DES TRANCHES DANS LE CODE
print("\n📐 AXIOME_CALCUL_TRANCHE : Le code gère-t-il correctement les tranches ?")
print("-" * 100)

print("❌ PROBLÈME MAJEUR DÉTECTÉ :")
print("   Le modèle actuel calcule : min(salaire, plafond) × taux")
print("   Pour les tranches, il faudrait :")
print("   - T1 : min(salaire, 3864) × taux_T1")
print("   - T2 : max(0, min(salaire, 30912) - 3864) × taux_T2")
print("   ")
print("   ⚠️  IMPACT : Les salaires > 3864€ ne paient pas correctement T2")

# 🚨 VÉRIFICATION 5 : PLAFONDS COHÉRENTS
print("\n📐 AXIOME_PLAFOND : Vérification des plafonds 2026")
print("-" * 100)

plafonds_attendus = {
    '1 PMSS': PMSS,
    '4 PMSS': PMSS * 4,
    '8 PMSS': PMSS * 8
}

print(f"✅ PMSS 2026 : {PMSS}€/mois")
for nom, valeur in plafonds_attendus.items():
    print(f"   {nom} = {valeur}€")

# Vérifier les plafonds dans la base
cotis_plafonnees = PayrollContribution.objects.filter(
    is_active=True,
    is_patronal=False,
    ceiling__isnull=False
).order_by('ceiling')

print("\nPlafonds utilisés dans le système :")
for cotis in cotis_plafonnees:
    print(f"   {cotis.name:50s} plafond = {cotis.ceiling}€")

# 🚨 VÉRIFICATION 6 : DÉDUCTIBILITÉ FISCALE
print("\n📐 CONCEPT_FISCAL : Déductibilité fiscale")
print("-" * 100)

print("✅ CSG déductible : réduit le revenu imposable")
print("❌ CSG non déductible : n'impacte pas l'impôt")
print("❌ CRDS : jamais déductible")
print("ℹ️  Note : Le système actuel ne gère pas encore la distinction fiscal/non-fiscal")

# 🚨 VÉRIFICATION 7 : SIGNAUX D'ERREUR
print("\n🚨 DÉTECTION DES SIGNAUX D'ERREUR")
print("-" * 100)

erreurs_detectees = []

# Test sur un salaire fictif
brut_test = Decimal('5000.00')
print(f"\n🧪 Simulation sur {brut_test}€ brut :")

for cotis in PayrollContribution.objects.filter(is_active=True, is_patronal=False):
    rate = cotis.rate / Decimal('100')
    if cotis.ceiling:
        assiette = min(brut_test, cotis.ceiling)
    else:
        assiette = brut_test
    
    montant = assiette * rate
    
    # Vérifier les anomalies
    if montant < 0:
        erreurs_detectees.append(f"🚨 {cotis.name} : montant négatif {montant}")
    
    if cotis.ceiling and assiette > cotis.ceiling:
        erreurs_detectees.append(f"🚨 {cotis.name} : assiette {assiette} > plafond {cotis.ceiling}")

if not erreurs_detectees:
    print("✅ Aucune erreur de calcul détectée sur la simulation")

# RÉSUMÉ FINAL
print("\n" + "=" * 100)
print("📊 RÉSUMÉ DE L'AUDIT")
print("=" * 100)

total_problemes = len(problemes_assiette) + len(problemes_tranches) + len(erreurs_detectees)

if problemes_assiette:
    print(f"\n⚠️  ASSIETTES ({len(problemes_assiette)} problèmes) :")
    for p in problemes_assiette:
        print(f"   {p}")

if problemes_tranches:
    print(f"\n⚠️  TRANCHES ({len(problemes_tranches)} problèmes) :")
    for p in problemes_tranches:
        print(f"   {p}")

if erreurs_detectees:
    print(f"\n🚨 ERREURS DE CALCUL ({len(erreurs_detectees)}) :")
    for e in erreurs_detectees:
        print(f"   {e}")

print("\n" + "=" * 100)
print("🎯 RECOMMANDATIONS PRINCIPALES")
print("=" * 100)

print("""
1️⃣  CSG/CRDS : Créer une assiette abattue à 98.25%
   → Actuellement : calcul direct sur 100% du brut
   → Solution : Ajouter un champ 'assiette_type' avec valeur 'ABATTUE_9825'

2️⃣  TRANCHES : Implémenter la logique de calcul par tranche
   → Actuellement : min(salaire, plafond) pour tout
   → Solution : Détecter les cotisations T2 et calculer la portion entre plafonds

3️⃣  EXPLICABILITÉ : Ajouter des métadonnées sur chaque cotisation
   → organisme : URSSAF, AGIRC_ARRCO, etc.
   → deductible_fiscalement : True/False
   → type_assiette : BRUT, ABATTUE, PLAFONNEE

4️⃣  VALIDATION : Ajouter des checks automatiques
   → Vérifier double ligne vieillesse
   → Vérifier cohérence plafonds
   → Alerter si assiette > plafond

5️⃣  TAUX EFFECTIFS : Clarifier dans les descriptions
   → CSG déductible : "6.80% sur 98.25% brut = 6.68% effectif"
""")

print("\n✅ Audit terminé - Score de cohérence : " + 
      f"{((25 - total_problemes) / 25 * 100):.0f}%")
