from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


def home(request):
    """Page d'accueil du SIRH"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """Informations sur l'API"""
    return Response({
        'nom': 'SIRH - Système d\'Information RH',
        'version': '1.0.0',
        'description': 'Plateforme de gestion RH pour transport sanitaire',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'employees': '/api/employees/',
            'contracts': '/api/contracts/',
            'vehicles': '/api/vehicles/',
            'planning': '/api/planning/',
            'timesheets': '/api/timesheets/',
            'payroll': '/api/payroll/',
            'portal': '/api/portal/',
        },
        'statut': 'En production',
    })
