# SIRH - Système d'Information Ressources Humaines


Projet Django pour gestion RH du transport sanitaire.

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

## 🚀 Installation & Démarrage

### Prérequis
- Python 3.11+
- pip

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
