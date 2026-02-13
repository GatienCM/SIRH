from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, date, timedelta
from decimal import Decimal

from .models import AuditLog, SystemSetting
from .serializers import AuditLogSerializer, SystemSettingSerializer
from accounts.permissions import IsAdmin, IsRH
from employees.models import Employee
from contracts.models import Contract
from vehicles.models import Vehicle
from planning.models import Shift, Assignment
from timesheets.models import TimeSheet, TimeSheetEntry
from payroll.models import Payroll
from portal.models import LeaveRequest, TimeOffBalance


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Consultation des logs d'audit"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        """Filtrer les logs selon les paramètres"""
        queryset = AuditLog.objects.all()
        
        # Filtrer par utilisateur
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filtrer par action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filtrer par période
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Récupérer les derniers logs (24h)"""
        yesterday = timezone.now() - timedelta(days=1)
        recent_logs = AuditLog.objects.filter(timestamp__gte=yesterday)[:100]
        serializer = AuditLogSerializer(recent_logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des logs d'audit"""
        # Logs par action
        actions_stats = AuditLog.objects.values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Logs par utilisateur
        users_stats = AuditLog.objects.values(
            'user__first_name', 'user__last_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Logs par jour (7 derniers jours)
        week_ago = timezone.now() - timedelta(days=7)
        daily_stats = AuditLog.objects.filter(
            timestamp__gte=week_ago
        ).extra(
            select={'day': 'date(timestamp)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        return Response({
            'actions': list(actions_stats),
            'users': list(users_stats),
            'daily': list(daily_stats),
            'total': AuditLog.objects.count()
        })


class SystemSettingViewSet(viewsets.ModelViewSet):
    """Gestion des paramètres système"""
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'])
    def by_key(self, request):
        """Récupérer un paramètre par sa clé"""
        key = request.query_params.get('key')
        if not key:
            return Response(
                {'error': 'Le paramètre key est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            setting = SystemSetting.objects.get(key=key)
            serializer = SystemSettingSerializer(setting)
            return Response(serializer.data)
        except SystemSetting.DoesNotExist:
            return Response(
                {'error': f'Paramètre {key} non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminDashboardViewSet(viewsets.ViewSet):
    """Dashboard administratif avec statistiques globales"""
    permission_classes = [IsAuthenticated, IsRH | IsAdmin]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé global du système"""
        today = date.today()
        current_month = today.month
        current_year = today.year

        cache_key = f"admin_summary:{current_year}-{current_month}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        # Statistiques employés
        total_employees = Employee.objects.count()
        active_contracts = Contract.objects.filter(
            status='active'
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=today)
        ).count()
        
        # Statistiques véhicules
        total_vehicles = Vehicle.objects.count()
        available_vehicles = Vehicle.objects.filter(
            status='available'
        ).count()
        
        # Statistiques planning
        shifts_today = Shift.objects.filter(date=today).count()
        assignments_today = Assignment.objects.filter(
            shift__date=today
        ).count()
        
        # Statistiques timesheets
        timesheets_pending = TimeSheet.objects.filter(
            status='submitted',
            year=current_year,
            month=current_month
        ).count()
        
        # Statistiques paie
        payrolls_to_validate = Payroll.objects.filter(
            status='calculated'
        ).count()
        
        total_salaries_month = Payroll.objects.filter(
            year=current_year,
            month=current_month,
            status__in=['validated', 'paid']
        ).aggregate(
            total=Sum('net_salary')
        )['total'] or Decimal('0.00')
        
        # Statistiques congés
        leave_requests_pending = LeaveRequest.objects.filter(
            status='pending'
        ).count()
        
        # Activité récente
        recent_activity = AuditLog.objects.all()[:10]
        
        summary_data = {
            'employees': {
                'total': total_employees,
                'active_contracts': active_contracts,
            },
            'vehicles': {
                'total': total_vehicles,
                'available': available_vehicles,
            },
            'planning': {
                'shifts_today': shifts_today,
                'assignments_today': assignments_today,
            },
            'timesheets': {
                'pending_approval': timesheets_pending,
            },
            'payroll': {
                'to_validate': payrolls_to_validate,
                'total_salaries_month': float(total_salaries_month),
            },
            'leave_requests': {
                'pending': leave_requests_pending,
            },
            'recent_activity': AuditLogSerializer(recent_activity, many=True).data,
        }
        
        return Response(summary_data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques détaillées"""
        period = request.query_params.get('period', '30')  # Jours
        try:
            days = int(period)
        except ValueError:
            days = 30
        
        today = date.today()
        cache_key = f"admin_statistics:{today.year}-{today.month}-{period}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        start_date = today - timedelta(days=days)
        
        # Évolution des employés
        employees_evolution = Employee.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Heures travaillées
        hours_worked = TimeSheetEntry.objects.filter(
            timesheet__year=today.year,
            timesheet__month=today.month
        ).aggregate(
            total_hours=Sum('hours_worked'),
            total_normal=Sum('hours_worked', filter=Q(entry_type='normal')),
            total_night=Sum('hours_worked', filter=Q(entry_type='night')),
            total_overtime=Sum('hours_worked', filter=Q(entry_type='overtime')),
        )
        
        # Répartition des congés
        leave_requests_by_type = LeaveRequest.objects.values('leave_type').annotate(
            count=Count('id'),
            total_days=Sum('days_requested')
        ).order_by('-count')
        
        # Salaires par période
        payrolls_by_month = Payroll.objects.filter(
            status__in=['validated', 'paid']
        ).values('period').annotate(
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            count=Count('id')
        ).order_by('-period')[:12]
        
        statistics_data = {
            'employees_evolution': list(employees_evolution),
            'hours_worked': hours_worked,
            'leave_requests': list(leave_requests_by_type),
            'payrolls': list(payrolls_by_month),
        }

        cache.set(cache_key, statistics_data, timeout=60)
        return Response(statistics_data)
    
    @action(detail=False, methods=['get'])
    def reports(self, request):
        """Rapports de conformité"""
        today = date.today()
        current_month = today.month
        current_year = today.year

        cache_key = f"admin_reports:{current_year}-{current_month}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        # Contrats expirant bientôt (30 jours)
        contracts_expiring = Contract.objects.filter(
            end_date__lte=today + timedelta(days=30),
            end_date__gte=today
        ).count()
        
        # Feuilles de temps non soumises
        timesheets_not_submitted = TimeSheet.objects.filter(
            year=current_year,
            month=current_month,
            status='draft'
        ).count()
        
        # Véhicules nécessitant maintenance
        vehicles_maintenance = Vehicle.objects.filter(
            status='maintenance'
        ).count()
        
        # Demandes de congés en attente depuis plus de 7 jours
        week_ago = timezone.now() - timedelta(days=7)
        old_leave_requests = LeaveRequest.objects.filter(
            status='pending',
            created_at__lt=week_ago
        ).count()
        
        reports_data = {
            'alerts': {
                'contracts_expiring': contracts_expiring,
                'timesheets_not_submitted': timesheets_not_submitted,
                'vehicles_maintenance': vehicles_maintenance,
                'old_leave_requests': old_leave_requests,
            },
            'compliance': {
                'total_active_employees': Employee.objects.filter(
                    contracts__status='active'
                ).filter(
                    Q(contracts__end_date__isnull=True) | Q(contracts__end_date__gte=today)
                ).distinct().count(),
                'employees_without_contract': Employee.objects.filter(
                    contracts__isnull=True
                ).count(),
                'total_hours_month': TimeSheetEntry.objects.filter(
                    timesheet__year=current_year,
                    timesheet__month=current_month
                ).aggregate(
                    total=Sum('hours_worked')
                )['total'] or 0,
            }
        }
        
        cache.set(cache_key, reports_data, timeout=60)
        return Response(reports_data)


def log_action(user, action, obj=None, changes=None, request=None):
    """Fonction utilitaire pour créer des logs d'audit"""
    from django.contrib.contenttypes.models import ContentType
    
    log_data = {
        'user': user,
        'action': action,
        'changes': changes or {},
    }
    
    if obj:
        log_data['content_type'] = ContentType.objects.get_for_model(obj)
        log_data['object_id'] = obj.pk
        log_data['object_repr'] = str(obj)
    
    if request:
        # Récupérer l'IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        log_data['ip_address'] = ip
        log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    return AuditLog.objects.create(**log_data)
