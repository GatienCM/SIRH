from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from datetime import datetime

from .models import SalaryScale, Payroll, PayrollItem
from .serializers import SalaryScaleSerializer, PayrollSerializer, PayrollItemSerializer
from accounts.permissions import IsRH, IsAdmin
from timesheets.models import TimeSheet
from employees.models import Employee


class SalaryScaleViewSet(viewsets.ModelViewSet):
    """Gestion des grilles salariales"""
    queryset = SalaryScale.objects.all()
    serializer_class = SalaryScaleSerializer
    permission_classes = [IsAuthenticated, IsRH]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return super().get_permissions()


class PayrollViewSet(viewsets.ModelViewSet):
    """Gestion des fiches de paie"""
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated, IsRH]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtrer les fiches de paie selon l'utilisateur"""
        user = self.request.user
        if hasattr(user, 'employee') and user.role == 'employee':
            return Payroll.objects.select_related('employee__user').filter(employee=user.employee)
        return Payroll.objects.select_related('employee__user')
    
    @action(detail=False, methods=['post'], permission_classes=[IsRH])
    def create_payroll(self, request):
        """Créer une fiche de paie pour un employé et une période"""
        employee_id = request.data.get('employee_id')
        period = request.data.get('period')  # Format: YYYY-MM
        
        if not employee_id or not period:
            return Response(
                {'error': 'employee_id et period sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            year, month = period.split('-')
            year = int(year)
            month = int(month)
            
            if month < 1 or month > 12:
                return Response(
                    {'error': 'Le mois doit être entre 1 et 12'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, IndexError):
            return Response(
                {'error': 'Format de période invalide (YYYY-MM)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employé non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Créer ou récupérer la fiche de paie
        payroll, created = Payroll.objects.get_or_create(
            employee=employee,
            period=period,
            year=year,
            month=month
        )
        
        serializer = PayrollSerializer(payroll)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH])
    def calculate(self, request, pk=None):
        """Calculer le salaire brut et net d'une fiche de paie"""
        payroll = self.get_object()
        
        # Récupérer ou créer la TimeSheet
        try:
            timesheet = TimeSheet.objects.get(
                employee=payroll.employee,
                year=payroll.year,
                month=payroll.month
            )
        except TimeSheet.DoesNotExist:
            return Response(
                {'error': 'Pas de feuille de temps pour cette période'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Récupérer la grille salariale
        salary_scale_id = request.data.get('salary_scale_id')
        if not salary_scale_id:
            return Response(
                {'error': 'salary_scale_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            salary_scale = SalaryScale.objects.get(id=salary_scale_id)
        except SalaryScale.DoesNotExist:
            return Response(
                {'error': 'Grille salariale non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Copier les heures depuis la feuille de temps
        payroll.total_hours = timesheet.total_hours
        payroll.normal_hours = timesheet.total_normal_hours
        payroll.night_hours = timesheet.total_night_hours
        payroll.sunday_hours = timesheet.total_sunday_hours
        payroll.holiday_hours = timesheet.total_holiday_hours
        payroll.overtime_hours = timesheet.total_overtime_hours
        
        # Calculer le salaire brut
        payroll.calculate_salary(salary_scale)
        
        # Calculer les déductions selon les règles légales
        payroll.calculate_with_payroll_rules()
        
        payroll.status = 'calculated'
        payroll.calculated_at = timezone.now()
        payroll.save()
        
        serializer = PayrollSerializer(payroll)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH])
    def validate(self, request, pk=None):
        """Valider une fiche de paie"""
        payroll = self.get_object()
        
        if payroll.status == 'calculated':
            payroll.status = 'validated'
            payroll.validated_at = timezone.now()
            payroll.validated_by = request.user.employee if hasattr(request.user, 'employee') else None
            payroll.save()
            serializer = PayrollSerializer(payroll)
            return Response(serializer.data)
        
        if payroll.status == 'validated' and request.user.role == 'admin':
            payroll.status = 'processed'
            payroll.save()
            serializer = PayrollSerializer(payroll)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Statut non valide pour cette action'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH])
    def mark_paid(self, request, pk=None):
        """Marquer une fiche de paie comme payée"""
        payroll = self.get_object()
        
        if payroll.status != 'validated':
            return Response(
                {'error': 'Seule une fiche validée peut être marquée comme payée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payroll.status = 'paid'
        payroll.paid_at = timezone.now()
        payroll.save()
        
        serializer = PayrollSerializer(payroll)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_period(self, request):
        """Récupérer les fiches de paie par période"""
        period = request.query_params.get('period')
        
        if not period:
            return Response(
                {'error': 'Le paramètre period (YYYY-MM) est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payrolls = self.get_queryset().filter(period=period)
        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Récupérer les fiches de paie d'un employé"""
        employee_id = request.query_params.get('employee_id')
        
        if not employee_id:
            return Response(
                {'error': 'Le paramètre employee_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payrolls = self.get_queryset().filter(employee_id=employee_id)
        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Exporter une fiche de paie (format JSON pour future intégration CSV/PDF)"""
        payroll = self.get_object()
        
        export_data = {
            'employee_name': f"{payroll.employee.user.first_name} {payroll.employee.user.last_name}",
            'period': payroll.period,
            'status': payroll.get_status_display(),
            'hours': {
                'total': float(payroll.total_hours),
                'normal': float(payroll.normal_hours),
                'night': float(payroll.night_hours),
                'sunday': float(payroll.sunday_hours),
                'holiday': float(payroll.holiday_hours),
                'overtime': float(payroll.overtime_hours),
            },
            'salary': {
                'gross': float(payroll.gross_salary),
                'normal': float(payroll.normal_salary),
                'night': float(payroll.night_salary),
                'sunday': float(payroll.sunday_salary),
                'holiday': float(payroll.holiday_salary),
                'overtime': float(payroll.overtime_salary),
            },
            'deductions': {
                'social_security': float(payroll.social_security),
                'taxes': float(payroll.taxes),
                'other': float(payroll.other_deductions),
                'total': float(payroll.total_deductions),
            },
            'net_salary': float(payroll.net_salary),
            'notes': payroll.notes,
        }
        
        return Response(export_data)


class PayrollItemViewSet(viewsets.ModelViewSet):
    """Gestion des éléments de paie"""
    queryset = PayrollItem.objects.all()
    serializer_class = PayrollItemSerializer
    permission_classes = [IsAuthenticated, IsRH]
    
    def get_queryset(self):
        payroll_id = self.request.query_params.get('payroll_id')
        if payroll_id:
            return PayrollItem.objects.filter(payroll_id=payroll_id)
        return PayrollItem.objects.all()
