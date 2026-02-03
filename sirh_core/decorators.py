"""Décorateurs pour contrôle d'accès basé sur les rôles"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Décorateur : seuls les admins peuvent accéder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in ['admin', 'rh']:
            messages.error(request, '❌ Accès refusé. Cette section est réservée aux administrateurs.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def employee_required(view_func):
    """Décorateur : seuls les employés peuvent accéder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'employee':
            messages.error(request, '❌ Accès refusé. Cette section est réservée aux salariés.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_or_owner(view_func):
    """Décorateur : admin OU salarié consulte ses propres données"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # Les admins peuvent voir tout, les employés que leurs données
        if request.user.role == 'employee':
            # Vérifier qu'on accède à ses propres données
            employee_id = kwargs.get('employee_id')
            if employee_id:
                # L'employé peut voir ses données
                from employees.models import Employee
                try:
                    emp = Employee.objects.get(id=employee_id)
                    if emp.user != request.user:
                        messages.error(request, '❌ Vous ne pouvez consulter que vos propres données.')
                        return redirect('dashboard')
                except Employee.DoesNotExist:
                    pass
        return view_func(request, *args, **kwargs)
    return wrapper
