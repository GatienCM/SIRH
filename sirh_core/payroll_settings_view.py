from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sirh_core.decorators import admin_required

@login_required(login_url='login')
@admin_required
def payroll_settings_view(request):
    """Page de gestion des variables de paie et cotisations"""
    # Pour l'instant, page statique, à compléter avec la logique métier plus tard
    return render(request, 'payroll_settings.html', {'page_title': 'Variables de paie & Cotisations'})
