# SIRH - Système d'Information Ressources Humaines

🚀 **Système complet de gestion RH pour le secteur du transport sanitaire**

Plateforme Django moderne incluant la gestion des employés, planning, feuilles de temps, contrats, véhicules et paie conforme URSSAF 2026.

---

## 🧾 Patch notes (27/02/2026)

### ✨ Nouvelles Fonctionnalités
- **Contrats multi-variantes** : sélection automatique du template selon l'entité, le type (CDD/CDI) et le genre
- **Accords grammaticaux** : gestion des formulations homme/femme dans les contrats

### 👤 Employés
- **Genre** : ajout du champ Masculin/Féminin pour les accords contractuels
- **Validation matricule** : contrôle d'unicité du matricule salarié avant création

### 🎨 Interface Utilisateur
- **Formulaire employé** : ajout du champ Genre dans la création et modification

---

## 🧾 Patch notes (24/02/2026)

### ✨ Nouvelles Fonctionnalités
- **Documents en attente (Dashboard)** : compteur des documents obligatoires manquants (somme sur tous les salariés actifs)
- **Indicateur GED par salarié** : badge "X manquants" / "Dossier complet" dans la liste des employés
- **Aperçu de documents** : visualisation en ligne (nouvel onglet) pour admin et salariés

### 🧾 GED & Documents obligatoires
- **Types GED étendus** : Attestation CPAM, Relevé d'identité bancaire, Permis de conduire, DPAE
- **Documents obligatoires suivis** : Contrat de travail, Pièce d'identité, Diplôme, Attestation, Attestation CPAM, RIB, Permis, DPAE

### 🎨 Interface Utilisateur
- **Dashboard allégé** : retrait des cadres Quarts/Assignations/Feuilles de temps/Paie/Total salaires
- **Accès rapide** : modules Planning/Feuilles de Temps/Paie/Absences retirés de l'UI
- **Navigation** : modules désactivés retirés du menu latéral (admin et salarié)

### 🔧 Technique
- **Calcul des documents manquants** : recalcul à chaque affichage du dashboard (évite les valeurs en cache obsolètes)
- **Routes** : ajout d'un endpoint d'aperçu document

---

## 🧾 Patch notes (13/02/2026)

### ✨ Nouvelles Fonctionnalités
- **Contrats - Génération Word** : Automatisation complète de la création de contrats Word à partir des données du système
- **Prévisualisation de Contrat** : Vérification visuelle avant la création définitive du contrat en base de données
- **Templates Multilingues** : 2 templates Word personnalisés par entité (Nantes Urgences Sansoucy / Ambulances Sansoucy)
- **Sélection d'Entité** : Choix de l'entité lors de la création du contrat pour adapter le template générateur

### 🛠️ Architecture
- **contracts/utils.py** (NEW) : Utilitaires de génération Word avec Jinja2 templating
  * `create_contract_template()` : Générage un template générique HTML avec docx
  * `create_entity_template()` : Crée des templates personnalisés pour chaque entité (SIRET, adresse, représentant)
  * `generate_contract_document()` : Remplissage dynamique du template avec les données du contrat
- **Système de Publipostage** : Jinja2 pour l'interpolation dynamique dans les documents Word (variables `{{ }}` et conditions `{% %}`"

### 💾 Modèles
- **Contract** : Ajout du champ `entity_template` (choix: 'nantes_urgences' ou 'ambulances_sansoucy')
- **Migration** : 0003_contract_entity_template.py pour créer le champ en base de données

### 🎨 Interface Utilisateur
- **Formulaire de Contrat Amélioré** : Ajout d'une sélection visuelle d'entité (cadre bleu, emoji 🏢)
- **Nouveau Bouton** : "👁️ Prévisualiser le Contrat" au lieu de "Enregistrer" directement
- **Page de Prévisualisation** (NEW) : contract_preview.html avec:
  * Récapitulatif complet du contrat
  * Affichage du document Word généré
  * Téléchargement pour vérification manuelle
  * 3 actions : Confirmer, Modifier, Annuler

### 📄 Génération & Stockage
- **Workflow 2-étapes** : Prévisualisation → Validation → Création (évite les contrats mal remplis)
- **Stockage en Session** : Les données et le fichier Word sont temporaires pendant la prévisualisation (encodage base64)
- **Fichier Attaché** : Une fois confirmé, le contrat Word est sauvegardé dans le champ `contract_file`

### 🔧 Techniques
- **python-docx** : Création/manipulation de documents Word
- **docxtpl** : Templating Jinja2 pour Word (publipostage)
- **Formatage Français** : Dates en DD/MM/YYYY, montants avec virgules et espaces
- **Gestion Type** : Conversion sécurisée des strings en dates/montants/nombres

### ✅ Corrigé
- **Conversion de Dates** : Conversion automatique des strings POST en objets `date`
- **Montants Numériques** : Formatage sécurisé (gestion des strings, Decimal, float)
- **Cache Dashboard** : Ajout du cache_key manquant dans la fonction `statistics()` de AdminDashboardViewSet

### ⚙️ Routes API
- `GET/POST /contracts/create/` : Affiche formulaire, lance prévisualisation
- `POST /contracts/preview/` : Génère aperçu, stocke en session
- `GET /contracts/preview/download/` : Télécharge le Word de prévisualisation
- `POST /contracts/create/` (confirmed=true) : Validation finale, création en DB

---

## 🧾 Patch notes (06/02/2026)

### ✅ Corrigé
- **Planning** : gestion correcte des quarts de nuit (statuts passé/en cours et validation horaires).
- **Feuilles de temps** : accès restreint par rôle, auto-remplissage sécurisé, filtres corrigés.
- **Paie** : calcul API aligné sur les règles légales et cohérence PMSS 2026.
- **Contrats** : validation gérée proprement (erreurs contrôlées).
- **Portail salarié** : ajustement automatique des soldes de congés et contrôle d’accès documents/congés.
- **API** : durcissement des permissions pour employés, contrats, véhicules, planning.

### 🎨 Interface
- **Logo** : ajout d’un logo générique et dossier media créé.
- **Paie** : bouton de création visible même lorsqu’une paie existe.

### 🔄 Workflow
- **Contrats** : création automatique d’une visite médicale d’embauche (interface + API).
- **Planning** : blocage des assignations avec véhicule indisponible.
- **Quarts** : détection de conflits d’horaires lors de la création/modification.
- **Feuilles de temps** : auto‑création mensuelle pour tous les salariés + verrouillage si approuvée/payée.
- **Paie** : validation en 2 étapes (calculé → validé → traité par admin).

### 🔔 Notifications & qualité
- **Dashboard** : ajout d’une liste d’actions à faire (todo).
- **Visites médicales** : alertes automatiques en cas de retard.
- **Employés** : création automatique du solde de congés annuel et contrôle d’unicité du NIR.

### 🔧 Données & conformité
- **PMSS 2026** mis à jour à **4 005 €** (4× = 16 020 €, 8× = 32 040 €).
- Seed paie fiabilisé et relancé (création des cotisations manquantes).

### ⚡ Optimisations
- **Requêtes DB** : réduction des N+1 via `select_related` / `prefetch_related`.
- **Index DB** : ajout d’index sur les champs filtrés (dates, statuts, employés).
- **Cache** : mise en cache des statistiques dashboard/admin (60s).

---

## 📦 Installation depuis GitHub

### Prérequis

- **Python 3.10+** ([Télécharger](https://www.python.org/downloads/))
- **Git** ([Télécharger](https://git-scm.com/downloads))
- **Un éditeur de code** (VS Code recommandé)

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/GatienCM/SIRH.git
cd SIRH
```

### 2️⃣ Créer l'environnement virtuel

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer la base de données

```bash
# Créer les tables de la base de données
python manage.py migrate

# Créer un compte administrateur
python manage.py createsuperuser

# Initialiser les cotisations sociales (URSSAF 2026)
python manage.py seed
```

### 5️⃣ Lancer le serveur

```bash
python manage.py runserver
```

🌐 Accédez à l'application : **http://127.0.0.1:8000/**

---

## 🔄 Travailler depuis un autre ordinateur

### Récupérer les dernières modifications

```bash
git pull origin main
```

### Envoyer vos modifications

```bash
# Ajouter tous les fichiers modifiés
git add .

# Créer un commit avec un message descriptif
git commit -m "Description de vos modifications"

# Envoyer vers GitHub
git push origin main
```

### ⚠️ Important : Synchronisation de la base de données

Le fichier `db.sqlite3` (base de données) n'est **pas synchronisé sur GitHub** pour des raisons de sécurité.

**Options :**

1. **Recommencer avec une base vide** (sur le nouvel ordinateur) :
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed
   ```

2. **Copier la base de données existante** :
   - Copier `db.sqlite3` depuis l'ancien ordinateur
   - Le placer dans le dossier racine du projet sur le nouvel ordinateur

---

## 📋 Modules & Fonctionnalités

### 👥 **Gestion des Employés**
- Fiches employés complètes (identité, contact, profession)
- Gestion des documents (contrats, attestations, certificats)
- Suivi des visites médicales
- Professions paramétrables

### 📅 **Planning & Shifts**
- Création de quarts de travail (types personnalisables)
- Assignation des employés
- Vue calendrier complète
- Gestion des statuts (planifié, en cours, complété)

### ⏱️ **Feuilles de Temps**
- Saisie des heures par type (normales, nuit, dimanche, férié, supplémentaires)
- Système d'ajustements et validation
- Export des données
- Calcul automatique des heures

### 💰 **Gestion de la Paie**
- Calcul automatique des cotisations sociales URSSAF 2026
- Support des assiettes abattues (CSG/CRDS 98.25%)
- Gestion des tranches (T1/T2)
- Variables de paie personnalisables
- Taux de cotisation : 22.55% (≤ PMSS) / 16.65% (> PMSS)

### 📄 **Contrats**
- Création de contrats de travail
- Types de contrats (CDI, CDD, Intérim, etc.)
- Suivi des avenants
- Gestion des services de santé au travail

### 🚗 **Véhicules**
- Flotte de véhicules
- Suivi des entretiens
- Assignations

### 🔐 **Authentification & Rôles**
- 3 rôles : Admin, Manager, Employé
- Portail employé dédié
- Permissions granulaires

---

## 🆕 Nouveautés principales (2026)

- **Module Guides & FAQ** :
   - Accès via la barre latérale et le tableau de bord (carte d'accès rapide)
   - Guides d'utilisation détaillés pour chaque module (Planning, Feuilles de temps, Paie, Employés/Contrats, Documents, Profil)
   - FAQ intégrée, adaptée au rôle (admin/manager/employee)
   - Pages de détail pour chaque guide, avec interactions entre modules
   - Affichage contextuel selon le rôle (employé/admin)

- **Navigation améliorée** :
   - Lien Guides & FAQ visible pour tous les rôles
   - Accès rapide depuis le tableau de bord
   - Sidebar adaptée au rôle (employé/admin)

- **Expérience employé** :
   - Guides spécifiques pour les salariés (Mon Planning, Mes Feuilles de temps, Mes Documents, Mon Profil)
   - FAQ adaptée aux besoins salariés (soumission de feuilles, ajustements, accès documents)

- **Expérience admin/manager** :
   - Guides détaillés pour la gestion RH, paie, planning, contrats, etc.
   - FAQ sur la génération de paie, gestion des heures, documents RH

---

## 📋 Structure du projet

```
sirh_project/
├── sirh_core/          # Configuration Django
├── accounts/           # Authentification & rôles
├── employees/          # Gestion des salariés
├── contracts/          # Gestion des contrats
├── vehicles/           # Gestion des véhicules
├── planning/           # Planning & shifts
├── timesheets/         # Temps de travail
├── payroll/            # Gestion de la paie
├── portal/             # Portail salarié
├── static/             # Fichiers statiques
├── media/              # Fichiers uploadés
├── templates/          # Templates HTML
└── manage.py
```

## 🚀 Démarrage rapide (après installation)

```bash
# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Lancer le serveur
python manage.py runserver
```

Accédez à : **http://127.0.0.1:8000/**

---

## 🛠️ Commandes utiles

### Gestion de la base de données
```bash
# Créer une migration après modification des models
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Réinitialiser les cotisations sociales
python manage.py seed
```

### Gestion des utilisateurs
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Accéder à l'admin Django
# http://127.0.0.1:8000/admin/
```

### Tests
```bash
# Lancer tous les tests
python manage.py test

# Tests d'un module spécifique
python manage.py test employees
```

---

## 💡 Guide de démarrage

### Première utilisation

1. **Créer un compte admin** via `createsuperuser`
2. **Initialiser les cotisations** avec `python manage.py seed`
3. **Se connecter** sur http://127.0.0.1:8000/
4. **Créer des professions** (Admin > Professions)
5. **Ajouter des employés** (Employés > Ajouter)
6. **Créer des types de quarts** (Admin > Types de Quarts)
7. **Planifier des shifts** (Planning > Ajouter)

### Workflow typique

1. **Planning** : Créer des quarts et assigner des employés
2. **Feuilles de temps** : Les employés soumettent leurs heures
3. **Validation** : Les managers approuvent les feuilles de temps
4. **Paie** : Générer les bulletins de paie basés sur les heures validées

---

## 🔐 Rôles et permissions

| Rôle | Accès |
|------|-------|
| **Admin** | Accès complet à tous les modules, gestion des utilisateurs |
| **Manager** | Gestion planning, validation feuilles de temps, consultation paie |
| **Employee** | Portail employé : consultation planning, soumission feuilles de temps, accès documents personnels |

---

## 📊 Module Paie - Conformité URSSAF 2026

Le module de paie est **100% conforme** aux taux URSSAF 2026 :

### Cotisations Salariales
- **Vieillesse plafonnée** : 6.90% (sur 1×PMSS = 4005€)
- **Vieillesse déplafonnée** : 0.40% (totalité du salaire)
- **Assurance chômage** : 2.40% (sur 4×PMSS = 16020€)
- **Retraite complémentaire T1** : 3.15% (sur 1×PMSS)
- **CEG T1** : 0.86% (sur 1×PMSS)
- **CSG déductible** : 6.80% sur assiette à 98.25% = 6.68% effectif
- **CSG non déductible** : 2.40% sur assiette à 98.25% = 2.36% effectif
- **CRDS** : 0.50% sur assiette à 98.25% = 0.49% effectif

### Taux effectifs
- **Salaire ≤ 4005€** : ~22.55% de cotisations
- **Salaire > 4005€** : ~16.65% (grâce aux plafonnements)

---

## 🤝 Contribution

### Workflow Git recommandé

```bash
# Créer une branche pour votre fonctionnalité
git checkout -b feature/nouvelle-fonctionnalite

# Faire vos modifications...

# Commiter vos changements
git add .
git commit -m "Ajout de [fonctionnalité]"

# Pousser vers GitHub
git push origin feature/nouvelle-fonctionnalite

# Créer une Pull Request sur GitHub
```

---

## 📝 Technologies utilisées

- **Backend** : Django 4.2.8
- **Frontend** : HTML5, CSS3, JavaScript
- **Base de données** : SQLite (dev) / PostgreSQL (prod recommandée)
- **API** : Django REST Framework
- **Authentification** : Django Auth + rôles personnalisés

---

## 📄 Licence

Ce projet est développé pour un usage interne. Tous droits réservés.

---

## 🆘 Support

En cas de problème :

1. Vérifier que toutes les dépendances sont installées : `pip install -r requirements.txt`
2. Vérifier que les migrations sont à jour : `python manage.py migrate`
3. Consulter les logs du serveur pour les erreurs
4. Vérifier la section **Guides & FAQ** dans l'application

---

## 📞 Contact

**Projet SIRH** - Système de gestion RH pour transport sanitaire
Développé avec Django & Python

### Étapes

1. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Créer le fichier .env**
   ```bash
   cp .env.example .env
   ```

4. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

5. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancer le serveur**
   ```bash
   python manage.py runserver
   ```

L'application sera disponible sur `http://localhost:8000`
L'admin Django sur `http://localhost:8000/admin`


## 📦 Modules principaux

- Authentification & rôles utilisateur
- Gestion des salariés
- Gestion des contrats
- Gestion des véhicules
- Planning & quarts
- Feuilles de temps
- Paie
- Portail salarié
- Admin & audit
- **Guides & FAQ** (nouveau)


## 🔒 Rôles & Permissions

- **Administrateur** : Accès complet à tous les modules, gestion RH, paie, guides, etc.
- **RH** : Gestion salariés, contrats, validation planning, accès guides RH
- **Manager** : Validation planning, suivi heures, accès guides manager
- **Salarié** : Consultation planning, feuilles de temps, documents, guides adaptés


## 📚 Guides & FAQ (fonctionnement)

- Accès via /guides/ ou le menu latéral
- Liste de guides selon le rôle connecté
- Chaque guide propose :
   - Un titre, une description, des étapes clés (bullets)
   - Les interactions avec les autres modules (ex : planning → feuilles de temps → paie)
- FAQ affichée sous les guides, adaptée au rôle
- Navigation retour simple vers la liste des guides

## 📁 Fichiers et templates liés

- `templates/guides_faq.html` : page d'accueil des guides et FAQ
- `templates/guides_detail.html` : page de détail d'un guide
- `sirh_core/views_app.py` : logique d'affichage guides/FAQ, gestion du rôle
- `sirh_core/urls.py` : routes `/guides/` et `/guides/<slug>/`
- Sidebar et dashboard (`base.html`, `dashboard_new.html`) : accès rapide Guides & FAQ
