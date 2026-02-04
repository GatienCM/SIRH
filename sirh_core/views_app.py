
from django.contrib.auth.decorators import login_required
from sirh_core.decorators import admin_required, employee_required
from django.test import RequestFactory

# (À placer APRÈS tous les imports et définitions de vues principales)

@login_required(login_url='login')
@admin_required
def payroll_settings_view(request):
    """Page de gestion des variables de paie et cotisations"""
    from payroll.models import PayrollVariable, PayrollContribution
    
    variables = PayrollVariable.objects.all()
    contributions = PayrollContribution.objects.all()
    
    # Créer une variable
    if request.method == 'POST' and 'add_variable' in request.POST:
        try:
            PayrollVariable.objects.create(
                name=request.POST.get('var_name'),
                value=request.POST.get('var_value'),
                unit=request.POST.get('var_unit', ''),
                description=request.POST.get('var_description', '')
            )
            messages.success(request, '✅ Variable de paie créée !')
            return redirect('payroll_settings')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    # Créer une cotisation
    if request.method == 'POST' and 'add_contribution' in request.POST:
        try:
            PayrollContribution.objects.create(
                name=request.POST.get('contrib_name'),
                rate=request.POST.get('contrib_rate'),
                ceiling=request.POST.get('contrib_ceiling') or None,
                description=request.POST.get('contrib_description', '')
            )
            messages.success(request, '✅ Cotisation créée !')
            return redirect('payroll_settings')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    # Activer/désactiver une variable
    if request.method == 'POST' and 'toggle_variable' in request.POST:
        try:
            var_id = request.POST.get('var_id')
            variable = PayrollVariable.objects.get(id=var_id)
            variable.is_active = not variable.is_active
            variable.save()
            status = 'activée' if variable.is_active else 'désactivée'
            messages.success(request, f'✅ Variable "{variable.name}" {status}')
            return redirect('payroll_settings')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    # Activer/désactiver une cotisation
    if request.method == 'POST' and 'toggle_contribution' in request.POST:
        try:
            contrib_id = request.POST.get('contrib_id')
            contribution = PayrollContribution.objects.get(id=contrib_id)
            contribution.is_active = not contribution.is_active
            contribution.save()
            status = 'activée' if contribution.is_active else 'désactivée'
            messages.success(request, f'✅ Cotisation "{contribution.name}" {status}')
            return redirect('payroll_settings')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    # Modifier une variable
    if request.method == 'POST' and 'update_variable' in request.POST:
        try:
            var_id = request.POST.get('edit_var_id')
            variable = PayrollVariable.objects.get(id=var_id)
            variable.name = request.POST.get('edit_var_name')
            variable.value = request.POST.get('edit_var_value')
            variable.unit = request.POST.get('edit_var_unit', '')
            variable.description = request.POST.get('edit_var_description', '')
            variable.save()
            messages.success(request, f'✅ Variable "{variable.name}" modifiée')
            return redirect('payroll_settings')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    # Modifier une cotisation
    if request.method == 'POST' and 'update_contribution' in request.POST:
        try:
            contrib_id = request.POST.get('edit_contrib_id')
            contribution = PayrollContribution.objects.get(id=contrib_id)
            contribution.name = request.POST.get('edit_contrib_name')
            contribution.rate = request.POST.get('edit_contrib_rate')
            contribution.ceiling = request.POST.get('edit_contrib_ceiling') or None
            contribution.description = request.POST.get('edit_contrib_description', '')
            contribution.is_patronal = 'edit_contrib_is_patronal' in request.POST
            contribution.save()
            messages.success(request, f'✅ Cotisation "{contribution.name}" modifiée')
            return redirect('payroll_settings')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    context = {
        'user': request.user,
        'variables': variables,
        'contributions': contributions,
        'page_title': '⚙️ Variables de paie & Cotisations'
    }
    return render(request, 'payroll_settings.html', context)

# Vue admin : simuler l'espace salarié d'un employé (iframe)
@login_required(login_url='login')
@admin_required
def employee_portal_simulate(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    user = employee.user
    today = date.today()
    current_month = today.month
    current_year = today.year
    # Contrats actuels
    contracts = Contract.objects.filter(
        employee=employee,
        status='active'
    ).order_by('-start_date')
    # Récupérer tous les shifts du salarié (mois en cours et passés)
    shifts = Shift.objects.filter(
        assignments__employee=employee,
        date__lte=today
    ).distinct().order_by('-date')[:30]  # Les 30 derniers shifts
    # Mettre à jour le statut dynamiquement si besoin
    for shift in shifts:
        if shift.status == 'planned' and shift.date < today:
            shift.status = 'completed'  # Optionnel : ou 'passé' si tu veux un autre statut
        elif shift.status == 'ongoing' and shift.date < today:
            shift.status = 'completed'
    # Feuille de temps du mois
    current_timesheet = TimeSheet.objects.filter(
        employee=employee,
        year=current_year,
        month=current_month
    ).first()
    context = {
        'user': user,
        'employee': employee,
        'contracts': contracts,
        'shifts': shifts,
        'current_timesheet': current_timesheet,
        'page_title': f"Vue salariée : {user.get_full_name()}"
    }
    return render(request, 'employee_portal.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q, F
from django.db import IntegrityError
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import CustomUser
from employees.models import Employee, Profession, EmployeeDocument, MedicalVisit
from contracts.models import Contract
from planning.models import Shift, Assignment, ShiftType
from timesheets.models import TimeSheet
from payroll.models import Payroll, PayrollItem
from vehicles.models import Vehicle
from sirh_core.models import AuditLog, SystemSetting
from sirh_core.decorators import admin_required, employee_required


def home(request):
    """Page d'accueil du SIRH"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Nom d\'utilisateur ou mot de passe incorrect'
            })
    
    return render(request, 'login.html')


@login_required(login_url='login')
def dashboard(request):
    """Dashboard principal - adapté au rôle"""
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Si c'est un employé, l'envoyer sur son portail personnel
    if request.user.role == 'employee':
        return redirect('employee_portal')
    
    # Récupérer les statistiques (pour admins/managers)
    upcoming_30_days = today + timedelta(days=30)
    
    stats = {
        'employees': Employee.objects.count(),
        'shifts_today': Shift.objects.filter(date=today).count(),
        'assignments_today': Assignment.objects.filter(
            shift__date=today
        ).count(),
        'timesheets_pending': TimeSheet.objects.filter(
            status='submitted',
            year=current_year,
            month=current_month
        ).count(),
        'payrolls_pending': Payroll.objects.filter(
            status='calculated'
        ).count(),
        'total_salaries': round(float(Payroll.objects.filter(
            year=current_year,
            month=current_month,
            status__in=['calculated', 'validated', 'paid']
        ).aggregate(total=Sum('net_salary'))['total'] or 0), 2),
    }
    
    # Visites médicales urgentes (à faire dans les 30 prochains jours)
    urgent_medical_visits = MedicalVisit.objects.filter(
        scheduled_date__gte=today,
        scheduled_date__lte=upcoming_30_days,
        status='scheduled'
    ).select_related('employee__user').order_by('scheduled_date')[:5]
    
    # Visites à planifier
    visits_to_schedule = MedicalVisit.objects.filter(
        status='to_schedule'
    ).select_related('employee__user').order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'stats': stats,
        'urgent_medical_visits': urgent_medical_visits,
        'visits_to_schedule': visits_to_schedule,
        'page_title': '📊 Tableau de Bord',
    }
    
    return render(request, 'dashboard_new.html', context)


@login_required(login_url='login')
def guides_faq(request):
    """Guides d'utilisation et FAQ"""
    if request.user.role == 'employee':
        guides = [
            {
                'title': 'Mon Planning',
                'description': 'Voir mes quarts, statuts et horaires.',
                'slug': 'planning'
            },
            {
                'title': 'Mes Feuilles de Temps',
                'description': 'Saisir, soumettre et suivre mes heures, demander des ajustements.',
                'slug': 'timesheets'
            },
            {
                'title': 'Mes Documents',
                'description': 'Accéder et télécharger mes documents RH.',
                'slug': 'documents'
            },
            {
                'title': 'Mon Profil',
                'description': 'Vérifier mes informations et identifiants de connexion.',
                'slug': 'profile'
            },
        ]

        faqs = [
            {
                'question': 'Comment soumettre ma feuille de temps ?',
                'answer': 'Ouvrez votre feuille du mois, sélectionnez le statut “Soumis” puis enregistrez.'
            },
            {
                'question': 'Comment demander des heures supplémentaires ou un ajustement ?',
                'answer': 'Depuis la feuille de temps, ajoutez un ajustement avec le type d’heure (supplémentaire, nuit, dimanche, férié) puis attendez l’approbation.'
            },
            {
                'question': 'Je ne vois pas mes quarts dans la feuille de temps ?',
                'answer': 'Cliquez sur “auto-fill” dans la feuille de temps pour importer vos quarts planifiés.'
            },
            {
                'question': 'Où récupérer mes fiches de paie ?',
                'answer': 'Consultez la section Documents ou contactez l’administrateur pour l’export PDF.'
            },
        ]
    else:
        guides = [
            {
                'title': 'Planning',
                'description': 'Créer, modifier et assigner des quarts, gérer les indisponibilités et les statuts.',
                'slug': 'planning'
            },
            {
                'title': 'Feuilles de temps',
                'description': 'Saisir, soumettre et faire valider les heures, ajouter des ajustements et suivre les statuts.',
                'slug': 'timesheets'
            },
            {
                'title': 'Paie',
                'description': 'Générer les fiches de paie à partir des feuilles validées et exporter en PDF.',
                'slug': 'payroll'
            },
            {
                'title': 'Employés et contrats',
                'description': 'Créer un employé, associer un contrat et gérer les documents RH.',
                'slug': 'employees'
            },
            {
                'title': 'Variables de Paie & Cotisations',
                'description': 'Configurer les variables de paie et les cotisations sociales pour les calculs salariaux.',
                'slug': 'payroll_variables'
            },
        ]

        faqs = [
            {
                'question': 'Pourquoi ma paie ne se génère pas ?',
                'answer': 'Seules les feuilles de temps avec statut Soumis ou Approuvé sont prises en compte. Vérifiez aussi que le contrat a un taux horaire.'
            },
            {
                'question': 'Comment ajouter des heures supplémentaires ?',
                'answer': 'Ouvrez la feuille de temps, ajoutez un ajustement en choisissant "Heures supplémentaires", puis faites-le approuver.'
            },
            {
                'question': 'Puis-je modifier un quart déjà planifié ?',
                'answer': 'Oui, via Planning > Éditer. Si le quart est en cours ou passé, mettez à jour le statut pour garder l’historique.'
            },
            {
                'question': 'Où télécharger les documents d’un employé ?',
                'answer': 'Allez dans Documents, filtrez par employé, ou utilisez la fiche Employé > Documents.'
            },
        ]

    context = {
        'page_title': '📘 Guides & FAQ',
        'guides': guides,
        'faqs': faqs,
    }
    return render(request, 'guides_faq.html', context)


@login_required(login_url='login')
def guide_detail(request, slug):
    """Page détail d'un guide module"""
    admin_guides = {
        'planning': {
            'title': 'Guide Planning',
            'subtitle': 'Créer, éditer, assigner et suivre vos quarts',
            'bullets': [
                'Créer un quart : Planning > Ajouter, puis définir date, heures et type de quart.',
                'Assigner des employés : Éditer un quart puis sélectionner les employés et leur statut.',
                'Suivre l’avancement : les statuts (Planifié, En cours, Complété, Annulé) se mettent à jour visuellement.',
                'Aide express : la colonne “Total heures” calcule automatiquement la durée du quart (gère le passage de minuit).'
            ],
            'interactions': [
                'Les quarts créés alimentent l’auto-remplissage des feuilles de temps (TimeSheets).',
                'Les assignations impactent les heures calculées dans la paie via les feuilles de temps.',
                'Les statuts des assignations (confirmé, en cours, complété) aident au suivi opérationnel et RH.'
            ]
        },
        'timesheets': {
            'title': 'Guide Feuilles de temps',
            'subtitle': 'Saisir, soumettre, ajuster et faire valider les heures',
            'bullets': [
                'Soumettre : passez la feuille de temps en “Soumis” pour la faire valider.',
                'Ajustements : ajoutez des heures (supplémentaires, nuit, dimanche, fériés) puis faites-les approuver.',
                'Auto-remplissage : depuis la feuille, utilisez “auto-fill” pour importer les quarts planifiés.',
                'Statuts : seule une feuille Soumise ou Approuvée est prise en paie (les brouillons/rejets sont ignorés).'
            ],
            'interactions': [
                'Les entrées proviennent des quarts (Planning) via l’auto-fill ou des ajustements manuels.',
                'Les feuilles Soumises/Approuvées sont les seules prises en compte lors de la génération de la paie.',
                'Les ajustements approuvés créent des entrées d’heures (supplémentaires, nuit, dimanche, fériés) utilisées par la paie.'
            ]
        },
        'payroll': {
            'title': 'Guide Paie',
            'subtitle': 'Générer et contrôler les fiches de paie',
            'bullets': [
                'Prérequis : la feuille de temps du mois doit être Soumise ou Approuvée.',
                'Génération : Paie > Générer, choisit mois/année. Les heures normales, nuit, dimanche, fériés et supp sont calculées.',
                'Ajustements : les ajustements approuvés sont injectés en heures correspondantes (supplémentaires, nuit, etc.).',
                'Export : chaque fiche peut être exportée en PDF depuis le détail.'
            ],
            'interactions': [
                'La paie lit uniquement les feuilles de temps Soumises/Approuvées.',
                'Les heures viennent des entrées de feuilles (issues des quarts ou ajustements).',
                'Les contrats fournissent le taux horaire ou salaire; sans contrat actif, la paie est ignorée.'
            ]
        },
        'employees': {
            'title': 'Guide Employés & Contrats',
            'subtitle': 'Créer un collaborateur et son dossier RH',
            'bullets': [
                'Créer un employé : saisir identité, rôle et login (ID/mot de passe).',
                'Associer un contrat : ajoutez un contrat actif avec taux horaire ou salaire mensuel.',
                'Documents : utilisez le module Documents (GED) pour charger et classer les pièces.',
                'Sécurité : seuls les rôles autorisés accèdent aux écrans d’administration.'
            ],
            'interactions': [
                'Un employé doit avoir un contrat actif (avec taux horaire) pour que sa paie soit générée.',
                'Les informations employé/contrat apparaissent dans Planning (assignations) et Paie (fiche salariale).',
                'Les documents RH associés restent accessibles dans le module Documents.'
            ]
        },
        'payroll_variables': {
            'title': 'Guide Variables de Paie & Cotisations',
            'subtitle': 'Configurer les paramètres de calcul salarial',
            'bullets': [
                '1. Accès : depuis le module Paie, cliquez sur le bouton "⚙ Variables & Cotisations" pour accéder à la page de configuration.',
                '2. Ajouter une variable : complétez le formulaire (Nom, Valeur, Unité, Description), puis validez. Les variables restent inactives par défaut.',
                '3. Ajouter une cotisation : renseignez Nom, Taux (%), Plafond mensuel (€) optionnel et Description, puis enregistrez.',
                '4. Activer/Désactiver : utilisez la colonne "Statut" pour basculer variables et cotisations entre Actif/Inactif sans les supprimer.',
                '5. Mise à jour : chaque modification met à jour le timestamp "Modifiée le" pour tracer les historiques de configuration.'
            ],
            'interactions': [
                'Les variables de paie (exemples : taux de congés, bonus fixes, indemnités) servent de paramètres de calcul réutilisables dans les fiches de paie.',
                'Les cotisations sociales (URSSAF, mutuelle, retraite) appliquent un taux (%) et éventuellement un plafond mensuel (base capped) au salaire brut.',
                'Une variable devient active après Activation et s\'affiche immédiatement dans les formulaires de paie si un administrateur la sélectionne.',
                'Une cotisation avec plafond limite le montant cotisé : exemple, plafond 3.000€/mois sur une base de calcul de 5.000€ = cotisation sur 3.000€ seulement.',
                'Les cotisations non-plafonnées (ex: URSSAF) appliquent le taux sur la totalité du salaire brut, modulo les autres déductions obligatoires.',
                'L\'imbriquer dans la paie : lors de la génération de fiche, sélectionnez les variables et cotisations actives applicables à cet employé pour ce mois.'
            ]
        },
    }

    employee_guides = {
        'planning': {
            'title': 'Guide Mon Planning',
            'subtitle': 'Consulter mes quarts et statuts',
            'bullets': [
                'Visualiser mes quarts : Planning affiche date, heure début/fin, statut.',
                'Statuts : Planifié, En cours, Complété, Annulé; suivez les mises à jour par le manager.',
                'Vérifier la durée : la colonne Total heures calcule automatiquement chaque quart.',
            ],
            'interactions': [
                'Les quarts planifiés peuvent être importés dans votre feuille de temps via “auto-fill”.',
                'Les statuts renseignent la disponibilité pour les feuilles de temps et la paie.'
            ]
        },
        'timesheets': {
            'title': 'Guide Mes Feuilles de temps',
            'subtitle': 'Saisir, soumettre et demander des ajustements',
            'bullets': [
                'Soumettre : passez au statut “Soumis” pour validation.',
                'Ajustements : ajoutez des heures supplémentaires, nuit, dimanche ou fériés; elles doivent être approuvées.',
                'Auto-fill : importez vos quarts planifiés pour préremplir la feuille.',
            ],
            'interactions': [
                'Seules les feuilles Soumises/Approuvées sont utilisées pour la paie.',
                'Les ajustements approuvés créent des entrées d’heures prises en compte dans la paie.'
            ]
        },
        'documents': {
            'title': 'Guide Mes Documents',
            'subtitle': 'Accéder et télécharger mes documents RH',
            'bullets': [
                'Accès : via “Mes Documents”, retrouvez vos pièces (contrat, fiches, attestations).',
                'Téléchargement : cliquez sur le document pour le récupérer.',
            ],
            'interactions': [
                'Les documents déposés par l’admin/HR apparaissent ici pour consultation.',
                'Les exports de paie peuvent être ajoutés par l’admin et visibles ici.'
            ]
        },
        'profile': {
            'title': 'Guide Mon Profil',
            'subtitle': 'Vérifier mes informations et identifiants',
            'bullets': [
                'Identité : vérifiez vos informations personnelles.',
                'Compte : votre login/mot de passe sont gérés par l’administrateur (demandez une mise à jour si besoin).',
            ],
            'interactions': [
                'Le profil est lié à vos accès Planning, Timesheets et Documents.',
                'Les informations de profil sont utilisées pour l’affichage des feuilles et de la paie.'
            ]
        },
    }

    guide_map = employee_guides if request.user.role == 'employee' else admin_guides
    guide = guide_map.get(slug)
    if not guide:
        messages.error(request, "Guide introuvable")
        return redirect('guides')

    context = {
        'page_title': guide['title'],
        'guide': guide,
    }
    return render(request, 'guides_detail.html', context)


@login_required(login_url='login')
def logout_view(request):
    """Déconnexion"""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_required
def employees_view(request):
    """Liste des employés - Admins seulement"""
    employees = Employee.objects.select_related('user', 'profession').all()
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        employees = employees.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Gestion de la vue salariée simulée
    view_employee = None
    view_employee_id = request.GET.get('view_employee_id')
    if view_employee_id:
        try:
            view_employee = Employee.objects.get(id=view_employee_id)
        except Employee.DoesNotExist:
            view_employee = None

    context = {
        'user': request.user,
        'employees': employees,
        'search': search,
        'page_title': '👨‍💼 Employés',
        'view_employee': view_employee,
    }
    return render(request, 'employees.html', context)


@login_required(login_url='login')
def planning_view(request):
    """Vue du planning"""
    from datetime import datetime, time
    
    shifts = Shift.objects.select_related('shift_type').prefetch_related('assignments').all()
    
    # Filtrer par date
    date_filter = request.GET.get('date', '')
    if date_filter:
        shifts = shifts.filter(date=date_filter)
    
    # Préparer les données des quarts avec les flags calculés
    now = datetime.now()
    current_time = now.time()
    current_date = now.date()
    
    shifts_data = []
    for shift in shifts:
        is_cancelled = shift.status == 'cancelled'
        is_in_progress = (
            not is_cancelled and
            shift.date == current_date and
            shift.start_time <= current_time <= shift.end_time
        )
        # Un quart est passé SEULEMENT si la date est avant aujourd'hui OU si c'est aujourd'hui mais l'heure est passée
        is_past = (not is_cancelled) and ((shift.date < current_date) or (shift.date == current_date and shift.end_time < current_time))
        
        # Mettre à jour automatiquement les assignments à "completed" s'ils n'étaient pas annulés/absents et que le shift n'est pas annulé
        if is_past and shift.date < current_date and shift.status != 'cancelled':  # Uniquement pour les quarts vraiment passés (hier ou avant)
            for assignment in shift.assignments.all():
                if assignment.status in ['assigned', 'confirmed', 'in_progress']:
                    assignment.status = 'completed'
                    assignment.save()
        
        shifts_data.append({
            'shift': shift,
            'is_in_progress': is_in_progress,
            'is_past': is_past,
            'is_cancelled': is_cancelled,
        })
    
    context = {
        'user': request.user,
        'shifts_data': shifts_data,
        'filter_date': date_filter,
        'page_title': '📅 Planning',
    }
    
    return render(request, 'planning.html', context)


@login_required(login_url='login')
def timesheets_view(request):
    """Vue des feuilles de temps"""
    timesheets = TimeSheet.objects.select_related('employee__user').all()
    
    # Filtrer par statut
    status_filter = request.GET.get('status', '')
    if status_filter:
        timesheets = timesheets.filter(status=status_filter)
    
    context = {
        'user': request.user,
        'timesheets': timesheets,
        'status_filter': status_filter,
        'page_title': '⏱️ Feuilles de Temps',
    }
    
    return render(request, 'timesheets.html', context)


@login_required(login_url='login')
@admin_required
def payroll_view(request):
    """Vue de la paie - Admins seulement"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    payrolls = Payroll.objects.all()
    
    # Filtrer par période
    period_filter = request.GET.get('period', '')
    if period_filter:
        payrolls = payrolls.filter(period=period_filter)
    
    # Calculer les totaux
    total_gross = sum(payroll.gross_salary or 0 for payroll in payrolls)
    total_net = sum(payroll.net_salary or 0 for payroll in payrolls)
    total_deductions = sum(payroll.total_deductions or 0 for payroll in payrolls)
    
    context = {
        'user': request.user,
        'payrolls': payrolls,
        'period_filter': period_filter,
        'page_title': '💰 Paie',
        'total_gross': total_gross,
        'total_net': total_net,
        'total_deductions': total_deductions,
    }
    
    return render(request, 'payroll.html', context)


@login_required(login_url='login')
@admin_required
def payroll_create(request):
    """Générer les feuilles de paie pour le mois en cours"""
    from datetime import date
    from decimal import Decimal
    
    if request.method == 'POST':
        year = int(request.POST.get('year', date.today().year))
        month = int(request.POST.get('month', date.today().month))
        
        # Récupérer tous les employés actifs
        employees = Employee.objects.filter(status='active')
        payrolls_created = 0
        payrolls_errors = []
        
        for employee in employees:
            # Récupérer la feuille de temps (uniquement soumises ou approuvées)
            timesheet = TimeSheet.objects.filter(
                employee=employee,
                year=year,
                month=month,
                status__in=['submitted', 'approved']
            ).first()
            
            if not timesheet:
                continue
            
            # Récupérer le contrat actif pour le taux horaire
            active_contract = None
            today = date.today()
            for contract in Contract.objects.filter(employee=employee, end_date__gte=today):
                if contract.hourly_rate:
                    active_contract = contract
                    break
            
            if not active_contract or not active_contract.hourly_rate:
                payrolls_errors.append(f'{employee.user.get_full_name()}: pas de contrat actif')
                continue  # Pas de contrat actif avec taux horaire
            
            # Créer ou récupérer la fiche de paie
            payroll, created = Payroll.objects.get_or_create(
                employee=employee,
                year=year,
                month=month,
                defaults={
                    'period': f'{year}-{month:02d}',
                    'status': 'draft'
                }
            )
            
            # Remplir les heures depuis la feuille de temps
            if not payroll.populate_hours_from_timesheet():
                payrolls_errors.append(f'{employee.user.get_full_name()}: impossible de récupérer les heures')
                continue
            
            # Récupérer les variables de paie actives pour les taux de majoration
            from payroll.models import PayrollVariable
            
            def get_rate_from_variables(variable_name, default_value):
                """Récupère le taux depuis les variables de paie ou utilise la valeur par défaut"""
                try:
                    var = PayrollVariable.objects.get(name__icontains=variable_name, is_active=True)
                    # Si l'unité est en %, diviser par 100 pour obtenir le multiplicateur
                    if var.unit == '%':
                        return var.value / Decimal('100')
                    else:
                        return var.value
                except PayrollVariable.DoesNotExist:
                    return Decimal(str(default_value))
            
            # Récupérer les taux depuis les variables de paie
            night_rate = get_rate_from_variables('Taux nuit', 1.25)
            sunday_rate = get_rate_from_variables('Taux dimanche', 1.50)
            holiday_rate = get_rate_from_variables('Taux jours fériés', 2.00)
            overtime_rate = get_rate_from_variables('Taux heures supplémentaires', 1.50)
            
            # Calculer le salaire brut à partir du taux horaire et des variables
            hourly_rate = Decimal(str(active_contract.hourly_rate))
            payroll.normal_salary = payroll.normal_hours * hourly_rate
            payroll.night_salary = payroll.night_hours * hourly_rate * night_rate
            payroll.sunday_salary = payroll.sunday_hours * hourly_rate * sunday_rate
            payroll.holiday_salary = payroll.holiday_hours * hourly_rate * holiday_rate
            payroll.overtime_salary = payroll.overtime_hours * hourly_rate * overtime_rate
            
            # Salaire brut
            payroll.gross_salary = (
                payroll.normal_salary
                + payroll.night_salary
                + payroll.sunday_salary
                + payroll.holiday_salary
                + payroll.overtime_salary
            )
            
            # Calculer les cotisations sociales à partir de la base de données
            payroll.calculate_with_payroll_rules()
            
            payroll.status = 'calculated'
            payroll.calculated_at = timezone.now()
            payroll.save()
            payrolls_created += 1
        
        if payrolls_created > 0:
            messages.success(request, f'✅ {payrolls_created} feuille(s) de paie créée(s) pour {month:02d}/{year} !')
        
        if payrolls_errors:
            for error in payrolls_errors:
                messages.warning(request, f'⚠️ {error}')
        
        if payrolls_created == 0 and not payrolls_errors:
            messages.warning(request, '⚠️ Aucune feuille de temps trouvée pour cette période')
        
        return redirect('payroll')
    
    # Afficher formulaire de création
    context = {
        'page_title': '➕ Créer Feuilles de Paie',
        'current_year': date.today().year,
        'current_month': date.today().month,
    }
    return render(request, 'payroll_create.html', context)


@login_required(login_url='login')
@admin_required
def payroll_detail(request, payroll_id):
    """Afficher les détails d'une fiche de paie"""
    payroll = get_object_or_404(Payroll, id=payroll_id)
    
    # Calculer les détails des cotisations
    from payroll.models import PayrollContribution, PayrollVariable
    
    contribution_details = []
    # Afficher UNIQUEMENT les cotisations salariales (non patronales)
    active_contributions = PayrollContribution.objects.filter(
        is_active=True,
        is_patronal=False
    )
    
    for contribution in active_contributions:
        rate = contribution.rate / Decimal('100')
        
        if contribution.ceiling:
            applicable_base = min(payroll.gross_salary, contribution.ceiling)
            amount = applicable_base * rate
        else:
            applicable_base = payroll.gross_salary
            amount = applicable_base * rate
        
        contribution_details.append({
            'name': contribution.name,
            'rate': contribution.rate,
            'ceiling': contribution.ceiling,
            'base': applicable_base,
            'amount': amount
        })
    
    total_contributions = sum(Decimal(str(c['amount'])) for c in contribution_details)
    
    context = {
        'payroll': payroll,
        'page_title': f'📋 Fiche de Paie - {payroll.employee.user.get_full_name()}',
        'contribution_details': contribution_details,
        'total_contributions': total_contributions,
    }
    
    return render(request, 'payroll_detail.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def payroll_calculation_api(request, payroll_id):
    """
    API JSON: Retourne les détails complets du calcul de paie
    Utile pour intégration/audit des cotisations
    """
    from payroll.models import PayrollContribution
    
    payroll = get_object_or_404(Payroll, id=payroll_id)
    
    # Vérifier les permissions
    if request.user.role != 'admin' and request.user.id != payroll.employee.user.id:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    contribution_details = []
    # Afficher UNIQUEMENT les cotisations salariales (non patronales)
    active_contributions = PayrollContribution.objects.filter(
        is_active=True,
        is_patronal=False
    )
    
    for contribution in active_contributions:
        rate = contribution.rate / Decimal('100')
        
        if contribution.ceiling:
            applicable_base = min(payroll.gross_salary, contribution.ceiling)
            amount = applicable_base * rate
        else:
            applicable_base = payroll.gross_salary
            amount = applicable_base * rate
        
        contribution_details.append({
            'name': contribution.name,
            'rate': float(contribution.rate),
            'ceiling': float(contribution.ceiling) if contribution.ceiling else None,
            'base': float(applicable_base),
            'amount': float(amount),
            'description': contribution.description
        })
    
    total_contributions = sum(Decimal(str(c['amount'])) for c in contribution_details)
    
    return JsonResponse({
        'payroll_id': payroll.id,
        'employee_name': payroll.employee.user.get_full_name(),
        'period': payroll.period,
        'hours': {
            'normal': float(payroll.normal_hours),
            'night': float(payroll.night_hours),
            'sunday': float(payroll.sunday_hours),
            'holiday': float(payroll.holiday_hours),
            'overtime': float(payroll.overtime_hours),
            'total': float(payroll.total_hours),
        },
        'salaries': {
            'normal': float(payroll.normal_salary),
            'night': float(payroll.night_salary),
            'sunday': float(payroll.sunday_salary),
            'holiday': float(payroll.holiday_salary),
            'overtime': float(payroll.overtime_salary),
            'gross': float(payroll.gross_salary),
        },
        'contributions': contribution_details,
        'total_contributions': float(total_contributions),
        'deductions': {
            'social_security': float(payroll.social_security),
            'taxes': float(payroll.taxes),
            'other': float(payroll.other_deductions),
            'total': float(payroll.total_deductions),
        },
        'net_salary': float(payroll.net_salary),
        'status': payroll.status,
        'calculated_at': payroll.calculated_at.isoformat() if payroll.calculated_at else None,
    })


@login_required(login_url='login')
@admin_required
def payroll_export(request, payroll_id):
    """Exporter une fiche de paie en PDF"""
    payroll = get_object_or_404(Payroll, id=payroll_id)
    
    # Pour l'instant, afficher un message
    messages.info(request, '📥 Export PDF en développement. Statut de la feuille: ' + payroll.get_status_display())
    return redirect('payroll')


@login_required(login_url='login')
@admin_required
def payroll_delete(request, payroll_id):
    """Supprimer une fiche de paie"""
    payroll = get_object_or_404(Payroll, id=payroll_id)
    employee_name = payroll.employee.user.get_full_name()
    period = f'{payroll.month:02d}/{payroll.year}'
    
    payroll.delete()
    messages.success(request, f'✅ Feuille de paie de {employee_name} ({period}) supprimée avec succès !')
    return redirect('payroll')


@login_required(login_url='login')
@admin_required
def contracts_view(request):
    """Vue des contrats - Admins seulement"""
    contracts = Contract.objects.select_related('employee__user', 'employee__profession').all()
    
    # Filtrer par statut
    status_filter = request.GET.get('status', '')
    if status_filter:
        contracts = contracts.filter(is_active=(status_filter == 'active'))
    
    context = {
        'user': request.user,
        'contracts': contracts,
        'status_filter': status_filter,
        'page_title': '📋 Contrats',
        'today': date.today(),
    }
    
    return render(request, 'contracts.html', context)


@login_required(login_url='login')
@admin_required
def vehicles_view(request):
    """Vue des véhicules - Admins seulement"""
    from vehicles.models import Vehicle
    
    vehicles = Vehicle.objects.all()
    
    # Filtrer par statut
    status_filter = request.GET.get('status', '')
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    
    context = {
        'user': request.user,
        'vehicles': vehicles,
        'status_filter': status_filter,
        'page_title': '🚗 Véhicules',
    }
    
    return render(request, 'vehicles.html', context)


@login_required(login_url='login')
@admin_required
def admin_panel(request):
    """Panel d'administration - Admins seulement"""
    if not (request.user.is_staff or request.user.role in ['admin', 'rh']):
        return redirect('dashboard')
    
    # Statistiques admin
    today = date.today()
    stats = {
        'total_employees': Employee.objects.count(),
        'active_contracts': Contract.objects.filter(is_active=True).count(),
        'pending_timesheets': TimeSheet.objects.filter(status='submitted').count(),
        'total_payroll': Payroll.objects.filter(
            status__in=['validated', 'paid']
        ).aggregate(total=Sum('net_salary'))['total'] or 0,
        'available_vehicles': Vehicle.objects.filter(status='available').count(),
        'recent_audits': AuditLog.objects.count(),
    }
    
    # Journaux d'audit récents
    audit_logs = AuditLog.objects.all().order_by('-timestamp')[:10]
    
    # Paramètres système
    settings = SystemSetting.objects.all()
    
    context = {
        'user': request.user,
        'stats': stats,
        'audit_logs': audit_logs,
        'settings': settings,
        'page_title': '🔧 Panneau d\'Administration',
    }
    
    return render(request, 'admin_panel.html', context)


@login_required(login_url='login')
@admin_required
def employee_create(request):
    """Créer un nouvel employé"""
    if request.method == 'POST':
        # Récupérer les données
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'employee')
        profession_id = request.POST.get('profession')
        
        # Vérification des champs obligatoires
        errors = []
        if not username:
            errors.append('Le nom d\'utilisateur est obligatoire')
        if not email:
            errors.append('L\'email est obligatoire')
        if not password:
            errors.append('Le mot de passe est obligatoire')
        if not first_name:
            errors.append('Le prénom est obligatoire')
        if not last_name:
            errors.append('Le nom est obligatoire')
        if not profession_id:
            errors.append('La profession est obligatoire')
        
        # Vérifier si username existe déjà
        if username and CustomUser.objects.filter(username=username).exists():
            errors.append(f'Le nom d\'utilisateur "{username}" existe déjà')
        
        # Vérifier si email existe déjà
        if email and CustomUser.objects.filter(email=email).exists():
            errors.append(f'L\'email "{email}" est déjà utilisé')
        
        if errors:
            professions = Profession.objects.all()
            return render(request, 'employee_form.html', {
                'employee': None,
                'professions': professions,
                'errors': errors,
                'form_data': request.POST,
                'page_title': '➕ Nouvel Employé',
            })
        
        try:
            # Créer l'utilisateur
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            # Créer l'employé avec tous les champs
            employee = Employee.objects.create(
                user=user,
                profession_id=profession_id,
                employee_id=request.POST.get('employee_id', '').strip(),
                date_entry=request.POST.get('date_entry'),
                birth_date=request.POST.get('birth_date'),
                birth_place=request.POST.get('birth_place', '').strip(),
                nationality=request.POST.get('nationality', 'Français(e)'),
                address=request.POST.get('address', '').strip(),
                postal_code=request.POST.get('postal_code', '').strip(),
                city=request.POST.get('city', '').strip(),
                country=request.POST.get('country', 'France'),
                phone=request.POST.get('phone', '').strip(),
                emergency_contact=request.POST.get('emergency_contact', '').strip(),
                emergency_phone=request.POST.get('emergency_phone', '').strip(),
                social_security_number=request.POST.get('social_security_number', '').strip(),
                rib=request.POST.get('rib', '').strip(),
                qualification=request.POST.get('qualification', '').strip(),
                status=request.POST.get('status', 'active')
            )
            
            messages.success(request, f'✅ Employé {user.get_full_name()} créé avec succès !')
            return redirect('employees')
            
        except Exception as e:
            messages.error(request, f'❌ Erreur lors de la création : {str(e)}')
            professions = Profession.objects.all()
            return render(request, 'employee_form.html', {
                'employee': None,
                'professions': professions,
                'form_data': request.POST,
                'page_title': '➕ Nouvel Employé',
            })
    
    professions = Profession.objects.all()
    return render(request, 'employee_form.html', {
        'employee': None,
        'professions': professions,
        'page_title': '➕ Nouvel Employé',
    })


@login_required(login_url='login')
@admin_required
def employee_edit(request, employee_id):
    """Modifier un employé"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        # Récupérer les données
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        
        # Vérifications
        errors = []
        
        if not username:
            errors.append('Le nom d\'utilisateur est obligatoire')
        if not email:
            errors.append('L\'email est obligatoire')
        if not first_name:
            errors.append('Le prénom est obligatoire')
        if not last_name:
            errors.append('Le nom est obligatoire')
        
        # Vérifier username uniqueness (sauf l'username actuel)
        if username and username != employee.user.username and CustomUser.objects.filter(username=username).exists():
            errors.append(f'Le nom d\'utilisateur "{username}" est déjà utilisé')
        
        # Vérifier email uniqueness (sauf l'email actuel)
        if email and email != employee.user.email and CustomUser.objects.filter(email=email).exists():
            errors.append(f'L\'email "{email}" est déjà utilisé')
        
        # Vérifier le mot de passe s'il est fourni
        if new_password and len(new_password) < 8:
            errors.append('Le mot de passe doit contenir au moins 8 caractères')
        
        if errors:
            professions = Profession.objects.all()
            return render(request, 'employee_form.html', {
                'employee': employee,
                'professions': professions,
                'errors': errors,
                'form_data': request.POST,
                'page_title': '✏️ Modifier l\'Employé',
            })
        
        try:
            # Mettre à jour l'utilisateur
            user = employee.user
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.role = request.POST.get('role', 'employee')
            
            # Mettre à jour le mot de passe s'il est fourni
            if new_password:
                user.set_password(new_password)
            
            user.save()
            
            # Mettre à jour l'employé
            profession_id = request.POST.get('profession')
            if profession_id:
                employee.profession_id = profession_id
            
            employee.date_entry = request.POST.get('date_entry')
            employee.birth_date = request.POST.get('birth_date')
            employee.birth_place = request.POST.get('birth_place', '').strip()
            employee.nationality = request.POST.get('nationality', 'Français(e)')
            employee.address = request.POST.get('address', '').strip()
            employee.postal_code = request.POST.get('postal_code', '').strip()
            employee.city = request.POST.get('city', '').strip()
            employee.country = request.POST.get('country', 'France')
            employee.phone = request.POST.get('phone', '').strip()
            employee.emergency_contact = request.POST.get('emergency_contact', '').strip()
            employee.emergency_phone = request.POST.get('emergency_phone', '').strip()
            employee.social_security_number = request.POST.get('social_security_number', '').strip()
            employee.rib = request.POST.get('rib', '').strip()
            employee.qualification = request.POST.get('qualification', '').strip()
            employee.status = request.POST.get('status', 'active')
            employee.save()
            
            messages.success(request, f'✅ Employé {user.get_full_name()} modifié avec succès !')
            return redirect('employees')
            
        except Exception as e:
            messages.error(request, f'❌ Erreur lors de la modification : {str(e)}')
            professions = Profession.objects.all()
            return render(request, 'employee_form.html', {
                'employee': employee,
                'professions': professions,
                'form_data': request.POST,
                'page_title': '✏️ Modifier l\'Employé',
            })
    
    professions = Profession.objects.all()
    return render(request, 'employee_form.html', {
        'employee': employee,
        'professions': professions,
        'page_title': '✏️ Modifier l\'Employé',
    })


@login_required(login_url='login')
@admin_required
def employee_delete(request, employee_id):
    """Supprimer un employé"""
    employee = get_object_or_404(Employee, id=employee_id)
    name = employee.user.get_full_name()
    employee.user.delete()  # Cascade delete
    messages.success(request, f'✅ Employé {name} supprimé avec succès !')
    return redirect('employees')


# CRUD Planning/Shifts
@login_required(login_url='login')
def shift_create(request):
    if request.method == 'POST':
        try:
            # Créer le shift
            shift = Shift.objects.create(
                shift_type_id=request.POST.get('shift_type'),
                date=request.POST.get('date'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
                status=request.POST.get('status', 'planned'),
                notes=request.POST.get('notes', ''),
                created_by=request.user
            )
            
            # Assigner l'employé au shift
            employee_id = request.POST.get('employee')
            assignment_status = request.POST.get('assignment_status', 'assigned')
            if employee_id:
                Assignment.objects.create(
                    shift=shift,
                    employee_id=employee_id,
                    status=assignment_status
                )
            
            messages.success(request, '✅ Quart créé et employé assigné avec succès !')
            return redirect('planning')
        except IntegrityError:
            messages.error(request, '❌ Erreur : Un quart existe déjà à cette date/heure avec ce type. Veuillez modifier l\'heure ou la date.')
            employees = Employee.objects.select_related('user', 'profession').filter(status='active')
            shift_types = ShiftType.objects.all()
            return render(request, 'shift_form.html', {
                'employees': employees,
                'shift_types': shift_types,
                'page_title': '➕ Nouveau Quart'
            })
    
    employees = Employee.objects.select_related('user', 'profession').filter(status='active')
    shift_types = ShiftType.objects.all()
    return render(request, 'shift_form.html', {
        'employees': employees,
        'shift_types': shift_types,
        'page_title': '➕ Nouveau Quart'
    })


@login_required(login_url='login')
def shift_edit(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    assignment = shift.assignments.first()  # Récupérer la première assignation
    
    if request.method == 'POST':
        # Mettre à jour le shift
        shift.shift_type_id = request.POST.get('shift_type')
        shift.date = request.POST.get('date')
        shift.start_time = request.POST.get('start_time')
        shift.end_time = request.POST.get('end_time')
        shift.status = request.POST.get('status', 'planned')
        shift.notes = request.POST.get('notes', '')
        shift.save()
        
        # Mettre à jour l'assignation
        employee_id = request.POST.get('employee')
        assignment_status = request.POST.get('assignment_status', 'assigned')
        if assignment and employee_id:
            assignment.employee_id = employee_id
            assignment.status = assignment_status
            assignment.save()
        elif employee_id and not assignment:
            # Créer une nouvelle assignation si elle n'existe pas
            Assignment.objects.create(
                shift=shift,
                employee_id=employee_id,
                status=assignment_status
            )
        
        messages.success(request, '✅ Quart modifié avec succès !')
        return redirect('planning')
    
    employees = Employee.objects.select_related('user', 'profession').filter(status='active')
    shift_types = ShiftType.objects.all()
    return render(request, 'shift_form.html', {
        'shift': shift,
        'assignment': assignment,
        'employees': employees,
        'shift_types': shift_types,
        'page_title': '✏️ Modifier Quart'
    })


@login_required(login_url='login')
def shift_delete(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    shift.delete()
    messages.success(request, '✅ Quart supprimé avec succès !')
    return redirect('planning')


# CRUD Timesheets
@login_required(login_url='login')
def timesheet_create(request):
    from datetime import date as date_module
    
    if request.method == 'POST':
        try:
            employee_id = request.POST.get('employee')
            year = int(request.POST.get('year', date_module.today().year))
            month = int(request.POST.get('month', date_module.today().month))
            status = request.POST.get('status', 'draft')
            notes = request.POST.get('notes', '')
            
            if not employee_id:
                messages.error(request, '❌ Veuillez sélectionner un employé')
                employees = Employee.objects.all()
                return render(request, 'timesheet_form.html', {'employees': employees, 'page_title': '➕ Nouvelle Feuille'})
            
            # Vérifier si une feuille existe déjà
            if TimeSheet.objects.filter(employee_id=employee_id, year=year, month=month).exists():
                messages.error(request, f'❌ Une feuille de temps existe déjà pour {month}/{year}')
                employees = Employee.objects.all()
                return render(request, 'timesheet_form.html', {'employees': employees, 'page_title': '➕ Nouvelle Feuille'})
            
            timesheet = TimeSheet.objects.create(
                employee_id=employee_id,
                year=year,
                month=month,
                status=status,
                notes=notes
            )
            messages.success(request, f'✅ Feuille de temps créée pour {month}/{year} !')
            return redirect('timesheets')
            
        except (ValueError, TypeError) as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
            employees = Employee.objects.all()
            return render(request, 'timesheet_form.html', {'employees': employees, 'page_title': '➕ Nouvelle Feuille'})
    
    employees = Employee.objects.all()
    context = {
        'employees': employees,
        'page_title': '➕ Nouvelle Feuille',
        'current_year': date_module.today().year,
        'current_month': date_module.today().month,
    }
    return render(request, 'timesheet_form.html', context)


@login_required(login_url='login')
def timesheet_edit(request, timesheet_id):
    timesheet = get_object_or_404(TimeSheet, id=timesheet_id)
    if request.method == 'POST':
        timesheet.status = request.POST.get('status')
        timesheet.notes = request.POST.get('notes', '')
        timesheet.save()
        messages.success(request, '✅ Feuille modifiée avec succès !')
        return redirect('timesheets')
    
    return render(request, 'timesheet_form.html', {'timesheet': timesheet, 'page_title': '✏️ Modifier Feuille'})


@login_required(login_url='login')
def timesheet_delete(request, timesheet_id):
    timesheet = get_object_or_404(TimeSheet, id=timesheet_id)
    timesheet.delete()
    messages.success(request, '✅ Feuille supprimée avec succès !')
    return redirect('timesheets')


@login_required(login_url='login')
@admin_required
def timesheet_auto_fill(request, timesheet_id):
    """Auto-remplir une feuille de temps à partir des quarts"""
    timesheet = get_object_or_404(TimeSheet, id=timesheet_id)
    
    entries_created = timesheet.auto_fill_from_assignments()
    
    if entries_created > 0:
        messages.success(request, f'✅ {entries_created} entrée(s) créée(s) à partir des quarts !')
    else:
        messages.warning(request, '⚠️ Aucun quart trouvé pour ce mois/employé')
    
    return redirect('timesheets')


# CRUD Contracts
@login_required(login_url='login')
def contract_create(request):
    if request.method == 'POST':
        contract = Contract.objects.create(
            employee_id=request.POST.get('employee'),
            contract_number=request.POST.get('contract_number'),
            contract_type=request.POST.get('contract_type'),
            status=request.POST.get('status', 'active'),
            contract_status=request.POST.get('contract_status', 'trial'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            trial_end_date=request.POST.get('trial_end_date') or None,
            working_hours_per_week=request.POST.get('working_hours_per_week', 35),
            hourly_rate=request.POST.get('hourly_rate') or None,
            monthly_salary=request.POST.get('monthly_salary') or None,
            occupational_health_service=request.POST.get('occupational_health_service', ''),
            collective_agreement=request.POST.get('collective_agreement', 'Convention collective du transport sanitaire'),
            collective_agreement_date=request.POST.get('collective_agreement_date') or None,
            notes=request.POST.get('notes', ''),
            created_by=request.user
        )
        messages.success(request, '✅ Contrat créé avec succès !')
        return redirect('contracts')
    
    employees = Employee.objects.all()
    return render(request, 'contract_form.html', {'employees': employees, 'page_title': '➕ Nouveau Contrat'})


@login_required(login_url='login')
def contract_edit(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == 'POST':
        try:
            # Préparer les valeurs numériques
            working_hours = request.POST.get('working_hours_per_week', '').strip()
            working_hours_value = Decimal(working_hours).quantize(Decimal('0.01')) if working_hours else Decimal('35.00')
            
            hourly_rate = request.POST.get('hourly_rate', '').strip()
            hourly_rate_value = Decimal(hourly_rate).quantize(Decimal('0.01')) if hourly_rate else None
            
            monthly_salary = request.POST.get('monthly_salary', '').strip()
            monthly_salary_value = Decimal(monthly_salary).quantize(Decimal('0.01')) if monthly_salary else None
            
            # Mise à jour via queryset pour bypasser la méthode save() personnalisée
            Contract.objects.filter(id=contract_id).update(
                contract_type=request.POST.get('contract_type'),
                status=request.POST.get('status', 'active'),
                contract_status=request.POST.get('contract_status', 'trial'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date') or None,
                trial_end_date=request.POST.get('trial_end_date') or None,
                working_hours_per_week=working_hours_value,
                hourly_rate=hourly_rate_value,
                monthly_salary=monthly_salary_value,
                occupational_health_service=request.POST.get('occupational_health_service', ''),
                collective_agreement=request.POST.get('collective_agreement', ''),
                collective_agreement_date=request.POST.get('collective_agreement_date') or None,
                notes=request.POST.get('notes', '')
            )
            
            messages.success(request, '✅ Contrat modifié avec succès !')
            return redirect('contracts')
        except Exception as e:
            messages.error(request, f'❌ Erreur lors de la modification: {str(e)}')
            return render(request, 'contract_form.html', {'contract': contract, 'page_title': '✏️ Modifier Contrat'})
    
    return render(request, 'contract_form.html', {'contract': contract, 'page_title': '✏️ Modifier Contrat'})


@login_required(login_url='login')
def contract_delete(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    contract.delete()
    messages.success(request, '✅ Contrat supprimé avec succès !')
    return redirect('contracts')


# CRUD Vehicles
@login_required(login_url='login')
def vehicle_create(request):
    if request.method == 'POST':
        vehicle = Vehicle.objects.create(
            vehicle_id=request.POST.get('vehicle_id'),
            registration_number=request.POST.get('registration_number'),
            vehicle_type=request.POST.get('vehicle_type'),
            brand=request.POST.get('brand'),
            model=request.POST.get('model'),
            year=request.POST.get('year'),
            color=request.POST.get('color', ''),
            seats_count=request.POST.get('seats_count', 3),
            stretcher_capacity=request.POST.get('stretcher_capacity', 1),
            initial_mileage=request.POST.get('initial_mileage', 0),
            current_mileage=request.POST.get('current_mileage', 0),
            fuel_type=request.POST.get('fuel_type', ''),
            consumption_per_100km=request.POST.get('consumption_per_100km') or None,
            purchase_date=request.POST.get('purchase_date'),
            entry_date=request.POST.get('entry_date'),
            exit_date=request.POST.get('exit_date') or None,
            status=request.POST.get('status', 'available'),
            last_maintenance_date=request.POST.get('last_maintenance_date') or None,
            next_maintenance_date=request.POST.get('next_maintenance_date') or None,
            last_inspection_date=request.POST.get('last_inspection_date') or None,
            next_inspection_date=request.POST.get('next_inspection_date') or None,
            insurance_policy_number=request.POST.get('insurance_policy_number', '')
        )
        messages.success(request, 'Véhicule ajouté !')
        return redirect('vehicles')
    
    return render(request, 'vehicle_form.html', {'page_title': '➕ Nouveau Véhicule'})


@login_required(login_url='login')
def vehicle_edit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        vehicle.vehicle_id = request.POST.get('vehicle_id')
        vehicle.registration_number = request.POST.get('registration_number')
        vehicle.vehicle_type = request.POST.get('vehicle_type')
        vehicle.brand = request.POST.get('brand')
        vehicle.model = request.POST.get('model')
        vehicle.year = request.POST.get('year')
        vehicle.color = request.POST.get('color', '')
        vehicle.seats_count = request.POST.get('seats_count', 3)
        vehicle.stretcher_capacity = request.POST.get('stretcher_capacity', 1)
        vehicle.initial_mileage = request.POST.get('initial_mileage', 0)
        vehicle.current_mileage = request.POST.get('current_mileage', 0)
        vehicle.fuel_type = request.POST.get('fuel_type', '')
        vehicle.consumption_per_100km = request.POST.get('consumption_per_100km') or None
        vehicle.purchase_date = request.POST.get('purchase_date')
        vehicle.entry_date = request.POST.get('entry_date')
        vehicle.exit_date = request.POST.get('exit_date') or None
        vehicle.status = request.POST.get('status', 'available')
        vehicle.last_maintenance_date = request.POST.get('last_maintenance_date') or None
        vehicle.next_maintenance_date = request.POST.get('next_maintenance_date') or None
        vehicle.last_inspection_date = request.POST.get('last_inspection_date') or None
        vehicle.next_inspection_date = request.POST.get('next_inspection_date') or None
        vehicle.insurance_policy_number = request.POST.get('insurance_policy_number', '')
        vehicle.save()
        messages.success(request, 'Véhicule modifié !')
        return redirect('vehicles')
    
    return render(request, 'vehicle_form.html', {'vehicle': vehicle, 'page_title': '✏️ Modifier Véhicule'})


@login_required(login_url='login')
def vehicle_delete(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    messages.success(request, 'Véhicule supprimé !')
    return redirect('vehicles')


# PORTAIL SALARIÉ
@login_required(login_url='login')
@employee_required
@login_required(login_url='login')
def employee_portal(request):
    """Portail personnel du salarié"""
    # Récupérer les données de l'employé connecté
    employee = Employee.objects.select_related('user', 'profession').filter(
        user=request.user
    ).first()
    
    if not employee:
        messages.error(request, '❌ Profil employé non trouvé.')
        return redirect('login')
    
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Contrats actuels
    contracts = Contract.objects.filter(
        employee=employee,
        status='active'
    ).order_by('-start_date')
    
    # Récupérer tous les shifts du salarié (mois en cours et passés)
    shifts = Shift.objects.filter(
        assignments__employee=employee,
        date__lte=today
    ).distinct().order_by('-date')[:30]  # Les 30 derniers shifts
    # Mettre à jour le statut dynamiquement si besoin
    for shift in shifts:
        if shift.status == 'planned' and shift.date < today:
            shift.status = 'completed'  # Optionnel : ou 'passé' si tu veux un autre statut
        elif shift.status == 'ongoing' and shift.date < today:
            shift.status = 'completed'
    
    # Feuille de temps du mois
    current_timesheet = TimeSheet.objects.filter(
        employee=employee,
        year=current_year,
        month=current_month
    ).first()
    
    context = {
        'user': request.user,
        'employee': employee,
        'contracts': contracts,
        'shifts': shifts,
        'current_timesheet': current_timesheet,
        'page_title': '👤 Mon Espace Salarié',
    }
    
    return render(request, 'employee_portal.html', context)


@login_required(login_url='login')
@admin_required
def absences_view(request):
    """Gestion des absences des salariés"""
    from timesheets.models import AbsenceRecord, TimeSheetEntry
    from datetime import datetime
    
    # Filtrer par employé si demandé
    employee_id = request.GET.get('employee')
    current_month = date.today().month
    current_year = date.today().year
    
    absences = AbsenceRecord.objects.all().order_by('-date_start')
    
    if employee_id:
        absences = absences.filter(employee_id=employee_id)
    
    # Créer une nouvelle absence
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
        absence_type = request.POST.get('absence_type')
        notes = request.POST.get('notes', '')
        
        try:
            employee = Employee.objects.get(id=employee_id)
            parsed_start = datetime.strptime(date_start, "%Y-%m-%d").date()
            parsed_end = datetime.strptime(date_end, "%Y-%m-%d").date()
            absence = AbsenceRecord(
                employee=employee,
                date_start=parsed_start,
                date_end=parsed_end,
                absence_type=absence_type,
                notes=notes
            )
            absence.save()
            
            # Annuler les quarts/assignations sur la période d'absence
            affected_assignments = Assignment.objects.filter(
                employee=employee,
                shift__date__gte=parsed_start,
                shift__date__lte=parsed_end,
                status__in=['assigned', 'confirmed', 'in_progress', 'completed']
            ).select_related('shift', 'shift__shift_type')
            cancelled_count = 0
            deduction_total = Decimal('0.00')
            maintained_total = Decimal('0.00')
            
            # Règles de rémunération selon le type d'absence (référence droit du travail)
            pay_blocked = absence_type in ['sick', 'unpaid', 'maternal', 'paternal', 'personal']
            pay_maintained = absence_type == 'vacation'
            
            for assign in affected_assignments:
                assign.status = 'cancelled'
                note_suffix = f"Absence du {parsed_start} au {parsed_end} ({absence.get_absence_type_display()})"
                assign.notes = f"{assign.notes}\n{note_suffix}" if assign.notes else note_suffix
                assign.save()
                cancelled_count += 1

                # Annuler également le quart (shift) si pas déjà annulé
                shift = assign.shift
                if shift.status != 'cancelled':
                    shift.status = 'cancelled'
                    shift.notes = f"{shift.notes}\n{note_suffix}" if shift.notes else note_suffix
                    shift.save()

                # Supprimer les entrées de feuille de temps liées à ce quart
                TimeSheetEntry.objects.filter(assignment=assign).delete()
                
                # Calcul des impacts paie
                hours = Decimal(str(assign.shift.duration_hours))
                contract = Contract.objects.filter(
                    employee=employee,
                    status='active',
                    start_date__lte=assign.shift.date
                ).order_by('-start_date').first()
                rate = None
                if contract:
                    if contract.hourly_rate:
                        rate = contract.hourly_rate
                    elif contract.monthly_salary:
                        rate = (contract.monthly_salary / Decimal('151.67')).quantize(Decimal('0.01'))
                if rate:
                    amount = (hours * rate).quantize(Decimal('0.01'))
                    period_str = f"{assign.shift.date.year:04d}-{assign.shift.date.month:02d}"
                    payroll, _ = Payroll.objects.get_or_create(
                        employee=employee,
                        year=assign.shift.date.year,
                        month=assign.shift.date.month,
                        defaults={'period': period_str}
                    )
                    if pay_blocked:
                        deduction_total += amount
                        payroll.other_deductions += amount
                        payroll.total_deductions = payroll.social_security + payroll.taxes + payroll.other_deductions
                        payroll.net_salary = payroll.gross_salary - payroll.total_deductions
                        payroll.save()
                        PayrollItem.objects.create(
                            payroll=payroll,
                            item_type='deduction',
                            description=f"Absence {absence.get_absence_type_display()} le {assign.shift.date}",
                            amount=amount
                        )
                    elif pay_maintained:
                        maintained_total += amount
                        payroll.gross_salary += amount
                        payroll.net_salary = payroll.gross_salary - payroll.total_deductions
                        payroll.save()
                        PayrollItem.objects.create(
                            payroll=payroll,
                            item_type='salary',
                            description=f"Maintien salaire congé payé le {assign.shift.date}",
                            amount=amount
                        )
            
            # Messages utilisateur
            if cancelled_count:
                messages.info(request, f'{cancelled_count} quart(s) annulé(s) pour absence.')
            if pay_blocked and deduction_total > 0:
                messages.info(request, f'Déductions ajoutées : {deduction_total} €')
            if pay_maintained:
                messages.info(request, f'Congé payé : rémunération maintenue (+{maintained_total} €) malgré annulation du quart.')
            
            messages.success(request, f'✅ Absence créée pour {employee.user.first_name} {employee.user.last_name}')
            return redirect('absences')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    # Statistiques
    today = date.today()
    absences_today = absences.filter(date_start__lte=today, date_end__gte=today)
    
    stats = {
        'total_absences': absences.count(),
        'absences_today': absences_today.count(),
        'employees_active': Employee.objects.filter(status='active').count(),
    }
    
    employees = Employee.objects.filter(status='active').order_by('user__last_name')
    absence_types = AbsenceRecord.ABSENCE_TYPE_CHOICES
    
    context = {
        'user': request.user,
        'absences': absences[:50],  # Dernières 50 absences
        'employees': employees,
        'absence_types': absence_types,
        'stats': stats,
        'page_title': '📋 Gestion des Absences',
    }
    
    return render(request, 'absences.html', context)


@login_required(login_url='login')
@admin_required
def absence_delete(request, absence_id):
    """Supprimer une absence"""
    from timesheets.models import AbsenceRecord
    
    absence = get_object_or_404(AbsenceRecord, id=absence_id)
    employee_name = f"{absence.employee.user.first_name} {absence.employee.user.last_name}"
    
    if request.method == 'POST':
        absence.delete()
        messages.success(request, f'✅ Absence supprimée pour {employee_name}')
        return redirect('absences')
    
    context = {
        'user': request.user,
        'absence': absence,
        'page_title': '🗑️ Supprimer Absence',
    }
    
    return render(request, 'absence_confirm_delete.html', context)


@login_required(login_url='login')
@admin_required
def documents_view(request):
    """Liste des employés pour accéder à leur GED"""
    from employees.models import EmployeeDocument
    from django.db.models import Count
    
    # Récupérer tous les employés avec le nombre de documents
    employees = Employee.objects.filter(status='active').annotate(
        document_count=Count('ged_documents')
    ).order_by('user__last_name')
    
    stats = {
        'total_employees': employees.count(),
        'total_documents': EmployeeDocument.objects.count(),
        'employees_with_docs': EmployeeDocument.objects.values('employee').distinct().count(),
    }
    
    context = {
        'user': request.user,
        'employees': employees,
        'stats': stats,
        'page_title': '📁 Gestion des Documents',
    }
    
    return render(request, 'documents.html', context)


@login_required(login_url='login')
@admin_required
def employee_documents_admin(request, employee_id):
    """Gestion des documents d'un employé spécifique"""
    from employees.models import EmployeeDocument
    
    employee = get_object_or_404(Employee, id=employee_id)
    documents = EmployeeDocument.objects.filter(employee=employee).order_by('-uploaded_at')
    
    # Upload de document
    if request.method == 'POST' and 'upload' in request.POST:
        document_type = request.POST.get('document_type')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')
        is_visible = request.POST.get('is_visible') == 'on'
        
        try:
            document = EmployeeDocument(
                employee=employee,
                document_type=document_type,
                title=title,
                description=description,
                file=file,
                uploaded_by=request.user,
                is_visible_to_employee=is_visible
            )
            document.save()
            messages.success(request, f'✅ Document "{title}" ajouté')
            return redirect('employee_documents_admin', employee_id=employee_id)
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    document_types = EmployeeDocument.DOCUMENT_TYPE_CHOICES
    
    context = {
        'user': request.user,
        'employee': employee,
        'documents': documents,
        'document_types': document_types,
        'page_title': f'📁 Documents de {employee.user.first_name} {employee.user.last_name}',
    }
    
    return render(request, 'employee_documents_admin.html', context)


@login_required(login_url='login')
@admin_required
def document_delete(request, document_id):
    """Supprimer un document"""
    from employees.models import EmployeeDocument
    
    document = get_object_or_404(EmployeeDocument, id=document_id)
    
    if request.method == 'POST':
        # Supprimer le fichier physique
        if document.file:
            document.file.delete()
        document.delete()
        messages.success(request, f'✅ Document "{document.title}" supprimé')
        return redirect('documents')
    
    context = {
        'user': request.user,
        'document': document,
        'page_title': '🗑️ Supprimer Document',
    }
    
    return render(request, 'document_confirm_delete.html', context)


@login_required(login_url='login')
def employee_documents_view(request):
    """Vue des documents pour un employé connecté"""
    from employees.models import EmployeeDocument
    
    try:
        employee = Employee.objects.get(user=request.user)
        documents = EmployeeDocument.objects.filter(
            employee=employee,
            is_visible_to_employee=True
        ).order_by('-uploaded_at')
        
        context = {
            'user': request.user,
            'employee': employee,
            'documents': documents,
            'page_title': '📁 Mes Documents',
        }
        
        return render(request, 'employee_documents.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Aucun profil employé trouvé')
        return redirect('dashboard')


@login_required(login_url='login')
@admin_required
@login_required(login_url='login')
@admin_required
def medical_visits_view(request):
    """Gestion des visites médicales"""
    from employees.models import MedicalVisit
    from datetime import date, timedelta
    
    # Filtres
    employee_id = request.GET.get('employee')
    status_filter = request.GET.get('status')
    
    visits = MedicalVisit.objects.all().select_related('employee__user').order_by('scheduled_date', '-created_at')
    
    if employee_id:
        visits = visits.filter(employee_id=employee_id)
    if status_filter:
        visits = visits.filter(status=status_filter)
    
    # Créer une visite
    if request.method == 'POST' and 'create' in request.POST:
        employee_id = request.POST.get('employee')
        visit_type = request.POST.get('visit_type')
        scheduled_date = request.POST.get('scheduled_date') or None
        status = request.POST.get('status', 'to_schedule')
        notes = request.POST.get('notes', '')
        try:
            employee = Employee.objects.get(id=employee_id)
            # Pré-remplir le médecin du travail depuis le dernier contrat actif
            latest_contract = (
                Contract.objects.filter(employee=employee)
                .order_by('-start_date')
                .first()
            )
            doctor_name = request.POST.get('doctor_name', '')
            if not doctor_name and latest_contract and latest_contract.occupational_health_service:
                doctor_name = latest_contract.occupational_health_service
            visit = MedicalVisit(
                employee=employee,
                visit_type=visit_type,
                scheduled_date=scheduled_date,
                doctor_name=doctor_name,
                notes=notes,
                status=status
            )
            visit.save()
            messages.success(request, f'✅ Visite médicale créée pour {employee.user.first_name} {employee.user.last_name}')
            return redirect('medical_visits')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    # Statistiques
    today = date.today()
    upcoming_30_days = today + timedelta(days=30)
    
    stats = {
        'total_visits': visits.count(),
        'to_schedule': visits.filter(status='to_schedule').count(),
        'upcoming_30_days': visits.filter(
            scheduled_date__gte=today,
            scheduled_date__lte=upcoming_30_days,
            status='scheduled'
        ).count(),
        'overdue': visits.filter(scheduled_date__lt=today, status='scheduled').count(),
    }
    
    employees = Employee.objects.filter(status='active').order_by('user__last_name')
    visit_types = MedicalVisit.VISIT_TYPE_CHOICES
    statuses = MedicalVisit.STATUS_CHOICES
    
    context = {
        'user': request.user,
        'visits': visits[:100],
        'employees': employees,
        'visit_types': visit_types,
        'statuses': statuses,
        'stats': stats,
        'page_title': '🏥 Gestion des Visites Médicales',
    }
    
    return render(request, 'medical_visits.html', context)


@login_required(login_url='login')
@admin_required
def medical_visit_edit(request, visit_id):
    """Modifier une visite médicale"""
    from employees.models import MedicalVisit
    
    visit = get_object_or_404(MedicalVisit, id=visit_id)
    
    if request.method == 'POST':
        visit.visit_type = request.POST.get('visit_type')
        visit.scheduled_date = request.POST.get('scheduled_date') or None
        visit.completed_date = request.POST.get('completed_date') or None
        visit.status = request.POST.get('status')
        visit.doctor_name = request.POST.get('doctor_name', '')
        visit.result = request.POST.get('result', '')
        visit.notes = request.POST.get('notes', '')
        visit.next_visit_date = request.POST.get('next_visit_date') or None
        visit.save()
        messages.success(request, '✅ Visite médicale mise à jour')
        return redirect('medical_visits')
    
    visit_types = MedicalVisit.VISIT_TYPE_CHOICES
    statuses = MedicalVisit.STATUS_CHOICES
    result_choices = [
        ('apte', 'Apte'),
        ('apte_reserve', 'Apte avec réserves'),
        ('inapte', 'Inapte'),
    ]
    
    context = {
        'user': request.user,
        'visit': visit,
        'visit_types': visit_types,
        'statuses': statuses,
        'result_choices': result_choices,
        'page_title': '✏️ Modifier Visite Médicale',
    }
    
    return render(request, 'medical_visit_edit.html', context)


@login_required(login_url='login')
@admin_required
def medical_visit_delete(request, visit_id):
    """Supprimer une visite médicale"""
    from employees.models import MedicalVisit
    
    visit = get_object_or_404(MedicalVisit, id=visit_id)
    
    if request.method == 'POST':
        employee_name = f"{visit.employee.user.first_name} {visit.employee.user.last_name}"
        visit.delete()
        messages.success(request, f'✅ Visite médicale supprimée pour {employee_name}')
        return redirect('medical_visits')
    
    context = {
        'user': request.user,
        'visit': visit,
        'page_title': '🗑️ Supprimer Visite Médicale',
    }
    
    return render(request, 'medical_visit_confirm_delete.html', context)

# ADMINISTRATION - GESTION DES DONNÉES DE BASE
@login_required(login_url='login')
@admin_required
def settings_professions(request):
    """Gestion des professions"""
    professions = Profession.objects.all()
    
    context = {
        'user': request.user,
        'professions': professions,
        'page_title': '👔 Gestion des Professions',
    }
    return render(request, 'admin/professions_list.html', context)


@login_required(login_url='login')
@admin_required
def profession_create(request):
    """Créer une profession"""
    if request.method == 'POST':
        code = request.POST.get('code')
        label = request.POST.get('label')
        description = request.POST.get('description', '')
        
        profession = Profession.objects.create(
            code=code,
            label=label,
            description=description
        )
        messages.success(request, f'Profession "{label}" créée !')
        return redirect('settings_professions')
    
    context = {
        'user': request.user,
        'page_title': '➕ Nouvelle Profession',
    }
    return render(request, 'admin/profession_form.html', context)


@login_required(login_url='login')
@admin_required
def profession_edit(request, profession_id):
    """Modifier une profession"""
    profession = get_object_or_404(Profession, id=profession_id)
    
    if request.method == 'POST':
        profession.label = request.POST.get('label')
        profession.description = request.POST.get('description', '')
        profession.is_active = request.POST.get('is_active') == 'on'
        profession.save()
        messages.success(request, 'Profession modifiée !')
        return redirect('settings_professions')
    
    context = {
        'user': request.user,
        'profession': profession,
        'page_title': '✏️ Modifier Profession',
    }
    return render(request, 'admin/profession_form.html', context)


@login_required(login_url='login')
@admin_required
def profession_delete(request, profession_id):
    """Supprimer une profession"""
    profession = get_object_or_404(Profession, id=profession_id)
    profession.delete()
    messages.success(request, 'Profession supprimée !')
    return redirect('settings_professions')


@login_required(login_url='login')
@admin_required
def settings_shifttypes(request):
    """Gestion des types de quart"""
    shifttypes = ShiftType.objects.all()
    
    context = {
        'user': request.user,
        'shifttypes': shifttypes,
        'page_title': '⏰ Gestion des Types de Quart',
    }
    return render(request, 'admin/shifttypes_list.html', context)


@login_required(login_url='login')
@admin_required
def shifttype_create(request):
    """Créer un type de quart"""
    if request.method == 'POST':
        name = request.POST.get('name')
        start_hour = request.POST.get('start_hour')
        end_hour = request.POST.get('end_hour')
        base_hours = request.POST.get('base_hours', '8')
        
        shifttype = ShiftType.objects.create(
            name=name,
            start_hour=start_hour,
            end_hour=end_hour,
            base_hours=float(base_hours)
        )
        messages.success(request, f'Type de quart "{name}" créé !')
        return redirect('settings_shifttypes')
    
    context = {
        'user': request.user,
        'page_title': '➕ Nouveau Type de Quart',
    }
    return render(request, 'admin/shifttype_form.html', context)


@login_required(login_url='login')
@admin_required
def shifttype_edit(request, shifttype_id):
    """Modifier un type de quart"""
    shifttype = get_object_or_404(ShiftType, id=shifttype_id)
    
    if request.method == 'POST':
        shifttype.name = request.POST.get('name')
        shifttype.start_hour = request.POST.get('start_hour')
        shifttype.end_hour = request.POST.get('end_hour')
        shifttype.base_hours = float(request.POST.get('base_hours', '8'))
        shifttype.is_active = request.POST.get('is_active') == 'on'
        shifttype.save()
        messages.success(request, 'Type de quart modifié !')
        return redirect('settings_shifttypes')
    
    context = {
        'user': request.user,
        'shifttype': shifttype,
        'page_title': '✏️ Modifier Type de Quart',
    }
    return render(request, 'admin/shifttype_form.html', context)


@login_required(login_url='login')
@admin_required
def shifttype_delete(request, shifttype_id):
    """Supprimer un type de quart"""
    shifttype = get_object_or_404(ShiftType, id=shifttype_id)
    shifttype.delete()
    messages.success(request, 'Type de quart supprimé !')
    return redirect('settings_shifttypes')


# CRUD TimeSheet Adjustments (Heures supplémentaires/réductions)
@login_required(login_url='login')
def timesheet_adjustment_add(request, timesheet_id):
    """Ajouter un ajustement d'heures (heures supplémentaires ou réductions)"""
    from timesheets.models import TimeSheetAdjustment
    
    timesheet = get_object_or_404(TimeSheet, id=timesheet_id)
    
    # Vérifier que l'employé ne peut modifier que sa feuille de temps
    # Les admins et managers peuvent modifier toutes les feuilles
    if not request.user.is_staff:
        try:
            if request.user.employee and request.user.employee != timesheet.employee:
                messages.error(request, "❌ Vous ne pouvez modifier que votre propre feuille de temps !")
                return redirect('timesheets')
        except:
            # Si l'utilisateur n'a pas d'Employee
            messages.error(request, "❌ Vous ne pouvez modifier que votre propre feuille de temps !")
            return redirect('timesheets')
    
    if request.method == 'POST':
        try:
            hours_adjustment = Decimal(request.POST.get('hours_adjustment', 0)).quantize(Decimal('0.01'))
            reason = request.POST.get('reason', '')
            hour_type = request.POST.get('hour_type', 'overtime')
            
            if not reason:
                messages.error(request, "❌ Veuillez indiquer une raison pour l'ajustement")
                return redirect('timesheet_edit', timesheet.id)
            
            if hours_adjustment == 0:
                messages.error(request, "❌ L'ajustement doit être différent de 0")
                return redirect('timesheet_edit', timesheet.id)
            
            TimeSheetAdjustment.objects.create(
                timesheet=timesheet,
                hours_adjustment=hours_adjustment,
                reason=reason,
                hour_type=hour_type,
                status='pending'
            )
            
            messages.success(request, f'✅ Ajustement de {hours_adjustment}h ajouté et en attente de validation')
            return redirect('timesheet_edit', timesheet.id)
        except Exception as e:
            messages.error(request, f"❌ Erreur: {str(e)}")
            return redirect('timesheet_edit', timesheet.id)
    
    return redirect('timesheet_edit', timesheet.id)


@login_required(login_url='login')
def timesheet_adjustment_approve(request, adjustment_id):
    """Approuver un ajustement d'heures"""
    from timesheets.models import TimeSheetAdjustment, TimeSheetEntry
    
    adjustment = get_object_or_404(TimeSheetAdjustment, id=adjustment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action', 'approve')
        
        if action == 'approve':
            adjustment.status = 'approved'
            adjustment.approved_by = request.user
            adjustment.approved_at = timezone.now()
            adjustment.notes = request.POST.get('notes', '')
            adjustment.save()
            
            # Créer une entrée dans la feuille de temps pour ajouter les heures
            TimeSheetEntry.objects.create(
                timesheet=adjustment.timesheet,
                date=adjustment.timesheet.get_last_day_of_month(),
                hour_type=adjustment.hour_type,
                hours_worked=abs(adjustment.hours_adjustment),
                hourly_rate=0,  # Les heures d'ajustement n'ont pas de taux horaire directe
                notes=f"Ajustement approuvé: {adjustment.reason}"
            )
            
            messages.success(request, f'✅ Ajustement de {adjustment.hours_adjustment}h approuvé et ajouté à la feuille de temps')
        elif action == 'reject':
            adjustment.status = 'rejected'
            adjustment.approved_by = request.user
            adjustment.approved_at = timezone.now()
            adjustment.notes = request.POST.get('notes', 'Rejeté')
            adjustment.save()
            messages.warning(request, f'⛔ Ajustement de {adjustment.hours_adjustment}h rejeté')
        
        return redirect('timesheets')
    
    # Affichage du formulaire d'approbation
    context = {
        'adjustment': adjustment,
        'page_title': '✏️ Valider Ajustement d\'Heures',
    }
    return render(request, 'adjustment_approval.html', context)


@login_required(login_url='login')
def timesheet_adjustment_delete(request, adjustment_id):
    """Supprimer un ajustement (avant approbation)"""
    from timesheets.models import TimeSheetAdjustment, TimeSheetEntry
    
    adjustment = get_object_or_404(TimeSheetAdjustment, id=adjustment_id)
    timesheet_id = adjustment.timesheet.id
    
    # Vérifier les permissions
    # Les admins peuvent supprimer tous les ajustements
    if not request.user.is_staff:
        try:
            if request.user.employee and request.user.employee != adjustment.timesheet.employee:
                messages.error(request, "❌ Vous ne pouvez supprimer que vos propres ajustements")
                return redirect('timesheets')
        except:
            # Si l'utilisateur n'a pas d'Employee
            messages.error(request, "❌ Vous ne pouvez supprimer que vos propres ajustements")
            return redirect('timesheets')
    
    if adjustment.status == 'rejected':
        messages.error(request, "❌ Les ajustements rejetés ne peuvent pas être supprimés")
        return redirect('timesheet_edit', timesheet_id)
    
    # Si l'ajustement est approuvé, supprimer aussi l'entrée correspondante dans la feuille de temps
    if adjustment.status == 'approved':
        # Supprimer l'entrée de feuille de temps créée lors de l'approbation
        # (l'entrée sans assignment avec la raison de l'ajustement)
        TimeSheetEntry.objects.filter(
            timesheet=adjustment.timesheet,
            assignment__isnull=True,
            notes__contains=adjustment.reason
        ).delete()
    
    adjustment.delete()
    messages.success(request, "✅ Ajustement supprimé")
    return redirect('timesheet_edit', timesheet_id)

# ===== RAPPORT FINANCIER ADMIN =====
@login_required(login_url='login')
@admin_required
def financial_report(request):
    """
    Rapport financier complet: montre TOUTES les cotisations (salariales ET patronales)
    pour une période donnée - VISIBLE UNIQUEMENT PAR LES ADMINS
    """
    from payroll.models import Payroll, PayrollContribution
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count
    from decimal import Decimal
    
    # Récupérer le mois/année demandé (par défaut, le mois courant)
    today = datetime.now()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # Construire la clé period au format "YYYY-MM"
    period_key = f"{year:04d}-{month:02d}"
    
    # Récupérer les fiches de paie du mois
    payrolls = Payroll.objects.filter(
        period=period_key
    ).select_related('employee__user')
    
    # Calculer les totaux
    total_brut = Decimal('0.00')
    total_net = Decimal('0.00')
    employee_contributions = {}  # {contribution_name: amount}
    employer_contributions = {}  # {contribution_name: amount}
    
    for payroll in payrolls:
        total_brut += payroll.gross_salary
        total_net += payroll.net_salary
        
        # Calculer les cotisations salariales
        salarial_contribs = PayrollContribution.objects.filter(
            is_active=True,
            is_patronal=False
        )
        
        for contribution in salarial_contribs:
            rate = contribution.rate / Decimal('100')
            if contribution.ceiling:
                applicable_base = min(payroll.gross_salary, contribution.ceiling)
                amount = applicable_base * rate
            else:
                applicable_base = payroll.gross_salary
                amount = applicable_base * rate
            
            key = contribution.name
            if key not in employee_contributions:
                employee_contributions[key] = Decimal('0.00')
            employee_contributions[key] += amount
        
        # Calculer les cotisations patronales
        patronal_contribs = PayrollContribution.objects.filter(
            is_active=True,
            is_patronal=True
        )
        
        for contribution in patronal_contribs:
            rate = contribution.rate / Decimal('100')
            if contribution.ceiling:
                applicable_base = min(payroll.gross_salary, contribution.ceiling)
                amount = applicable_base * rate
            else:
                applicable_base = payroll.gross_salary
                amount = applicable_base * rate
            
            key = contribution.name
            if key not in employer_contributions:
                employer_contributions[key] = Decimal('0.00')
            employer_contributions[key] += amount
    
    total_employee_contributions = sum(Decimal(str(v)) for v in employee_contributions.values())
    total_employer_contributions = sum(Decimal(str(v)) for v in employer_contributions.values())
    total_contributions = total_employee_contributions + total_employer_contributions
    
    # Calculer les pourcentages
    if total_brut > 0:
        pct_employee_contributions = (total_employee_contributions / total_brut) * 100
        pct_employer_contributions = (total_employer_contributions / total_brut) * 100
    else:
        pct_employee_contributions = Decimal('0.00')
        pct_employer_contributions = Decimal('0.00')
    
    context = {
        'user': request.user,
        'payrolls': payrolls,
        'month': month,
        'year': year,
        'months': range(1, 13),
        'years': range(today.year - 2, today.year + 1),
        'total_brut': total_brut,
        'total_net': total_net,
        'total_employee_contributions': total_employee_contributions,
        'total_employer_contributions': total_employer_contributions,
        'total_contributions': total_contributions,
        'pct_employee_contributions': pct_employee_contributions,
        'pct_employer_contributions': pct_employer_contributions,
        'employee_contributions': sorted(employee_contributions.items()),
        'employer_contributions': sorted(employer_contributions.items()),
        'nb_employees': payrolls.count(),
        'page_title': f'📊 Rapport Financier - {month:02d}/{year}'
    }
    
    return render(request, 'admin/financial_report.html', context)