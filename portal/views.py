from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, date

from .models import LeaveRequest, TimeOffBalance, Document, Notification
from .serializers import (
    LeaveRequestSerializer, TimeOffBalanceSerializer,
    DocumentSerializer, NotificationSerializer
)
from accounts.permissions import IsRH, IsAdmin, IsManager
from planning.models import Assignment
from planning.serializers import AssignmentSerializer
from timesheets.models import TimeSheet
from timesheets.serializers import TimeSheetSerializer
from payroll.models import Payroll
from payroll.serializers import PayrollSerializer


class DashboardViewSet(viewsets.ViewSet):
    """Dashboard personnel de l'employé"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé du tableau de bord de l'employé"""
        user = request.user
        
        if not hasattr(user, 'employee'):
            return Response(
                {'error': 'Utilisateur non associé à un employé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        employee = user.employee
        today = date.today()
        current_year = today.year
        current_month = today.month
        
        # Prochaines affectations
        upcoming_assignments = Assignment.objects.filter(
            employee=employee,
            shift__date__gte=today
        ).order_by('shift__date')[:5]
        
        # Feuille de temps du mois en cours
        try:
            current_timesheet = TimeSheet.objects.get(
                employee=employee,
                year=current_year,
                month=current_month
            )
            timesheet_data = TimeSheetSerializer(current_timesheet).data
        except TimeSheet.DoesNotExist:
            timesheet_data = None
        
        # Dernière fiche de paie
        latest_payroll = Payroll.objects.filter(
            employee=employee
        ).order_by('-period').first()
        
        # Solde de congés
        try:
            time_off_balance = TimeOffBalance.objects.get(
                employee=employee,
                year=current_year
            )
            balance_data = TimeOffBalanceSerializer(time_off_balance).data
        except TimeOffBalance.DoesNotExist:
            balance_data = None
        
        # Demandes de congés en attente
        pending_leave_requests = LeaveRequest.objects.filter(
            employee=employee,
            status='pending'
        ).count()
        
        # Notifications non lues
        unread_notifications = Notification.objects.filter(
            employee=employee,
            is_read=False
        ).count()
        
        summary_data = {
            'employee': {
                'id': employee.id,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'profession': employee.profession.name if employee.profession else None,
            },
            'upcoming_assignments': AssignmentSerializer(upcoming_assignments, many=True).data,
            'current_timesheet': timesheet_data,
            'latest_payroll': PayrollSerializer(latest_payroll).data if latest_payroll else None,
            'time_off_balance': balance_data,
            'pending_leave_requests': pending_leave_requests,
            'unread_notifications': unread_notifications,
        }

        # Actions à faire
        todo = []
        if not current_timesheet:
            todo.append('Créer la feuille de temps du mois en cours')
        elif current_timesheet.status == 'draft':
            todo.append('Soumettre la feuille de temps du mois en cours')
        if pending_leave_requests > 0:
            todo.append('Suivre vos demandes de congés en attente')
        summary_data['todo'] = todo
        
        return Response(summary_data)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """Gestion des demandes de congés"""
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les demandes selon l'utilisateur"""
        user = self.request.user
        
        # RH et Admin voient toutes les demandes
        if user.role in ['admin', 'rh']:
            return LeaveRequest.objects.all()
        
        # Manager voit les demandes de son équipe
        if user.role == 'manager' and hasattr(user, 'employee'):
            # TODO: Implémenter la logique d'équipe
            return LeaveRequest.objects.filter(employee=user.employee)
        
        # Employé voit seulement ses demandes
        if hasattr(user, 'employee'):
            return LeaveRequest.objects.filter(employee=user.employee)
        
        return LeaveRequest.objects.none()
    
    def perform_create(self, serializer):
        """Créer une demande de congé pour l'employé connecté"""
        if hasattr(self.request.user, 'employee'):
            serializer.save(employee=self.request.user.employee)
        else:
            raise serializers.ValidationError("Utilisateur non associé à un employé")

    def _adjust_balance(self, leave_request, direction):
        """Ajuster le solde de congés (direction=1 pour déduire, -1 pour restaurer)"""
        balance, _ = TimeOffBalance.objects.get_or_create(
            employee=leave_request.employee,
            year=leave_request.start_date.year
        )
        days = leave_request.days_requested
        if leave_request.leave_type == 'vacation':
            balance.vacation_days_taken += days * direction
        elif leave_request.leave_type == 'sick':
            balance.sick_days_taken += days * direction
        else:
            balance.other_days_taken += days * direction
        balance.save()
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Récupérer les demandes de l'employé connecté"""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'Utilisateur non associé à un employé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        requests = LeaveRequest.objects.filter(employee=request.user.employee)
        serializer = LeaveRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Récupérer les demandes en attente"""
        pending = self.get_queryset().filter(status='pending')
        serializer = LeaveRequestSerializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsManager])
    def approve(self, request, pk=None):
        """Approuver une demande de congé"""
        leave_request = self.get_object()
        if request.user.role == 'manager' and hasattr(request.user, 'employee'):
            if leave_request.employee != request.user.employee:
                return Response(
                    {'error': 'Accès non autorisé pour ce manager'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if leave_request.status != 'pending':
            return Response(
                {'error': 'Seule une demande en attente peut être approuvée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = 'approved'
        leave_request.approved_at = timezone.now()
        if hasattr(request.user, 'employee'):
            leave_request.approved_by = request.user.employee
        leave_request.save()

        # Mettre à jour le solde de congés
        self._adjust_balance(leave_request, direction=1)
        
        # Créer une notification
        Notification.objects.create(
            employee=leave_request.employee,
            notification_type='success',
            title='Demande de congé approuvée',
            message=f'Votre demande de congé du {leave_request.start_date} au {leave_request.end_date} a été approuvée.'
        )
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsManager])
    def reject(self, request, pk=None):
        """Refuser une demande de congé"""
        leave_request = self.get_object()
        if request.user.role == 'manager' and hasattr(request.user, 'employee'):
            if leave_request.employee != request.user.employee:
                return Response(
                    {'error': 'Accès non autorisé pour ce manager'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if leave_request.status != 'pending':
            return Response(
                {'error': 'Seule une demande en attente peut être refusée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        leave_request.status = 'rejected'
        leave_request.rejection_reason = rejection_reason
        if hasattr(request.user, 'employee'):
            leave_request.approved_by = request.user.employee
        leave_request.approved_at = timezone.now()
        leave_request.save()
        
        # Créer une notification
        Notification.objects.create(
            employee=leave_request.employee,
            notification_type='error',
            title='Demande de congé refusée',
            message=f'Votre demande de congé du {leave_request.start_date} au {leave_request.end_date} a été refusée. Motif: {rejection_reason}'
        )
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler sa propre demande de congé"""
        leave_request = self.get_object()
        
        # Vérifier que c'est bien la demande de l'employé
        if hasattr(request.user, 'employee') and leave_request.employee != request.user.employee:
            return Response(
                {'error': 'Vous ne pouvez annuler que vos propres demandes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if leave_request.status not in ['pending', 'approved']:
            return Response(
                {'error': 'Seule une demande en attente ou approuvée peut être annulée'},
                status=status.HTTP_400_BAD_REQUEST
            )

        was_approved = leave_request.status == 'approved'
        
        leave_request.status = 'cancelled'
        leave_request.save()

        # Restaurer le solde si la demande était approuvée
        if was_approved:
            self._adjust_balance(leave_request, direction=-1)
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)


class TimeOffBalanceViewSet(viewsets.ModelViewSet):
    """Gestion des soldes de congés"""
    queryset = TimeOffBalance.objects.all()
    serializer_class = TimeOffBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRH(), IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filtrer les soldes selon l'utilisateur"""
        user = self.request.user
        
        if user.role in ['admin', 'rh']:
            return TimeOffBalance.objects.all()
        
        if hasattr(user, 'employee'):
            return TimeOffBalance.objects.filter(employee=user.employee)
        
        return TimeOffBalance.objects.none()
    
    @action(detail=False, methods=['get'])
    def my_balance(self, request):
        """Récupérer le solde de l'employé connecté"""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'Utilisateur non associé à un employé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        year = request.query_params.get('year', timezone.now().year)
        
        try:
            balance = TimeOffBalance.objects.get(
                employee=request.user.employee,
                year=year
            )
            serializer = TimeOffBalanceSerializer(balance)
            return Response(serializer.data)
        except TimeOffBalance.DoesNotExist:
            return Response(
                {'error': f'Aucun solde trouvé pour l\'année {year}'},
                status=status.HTTP_404_NOT_FOUND
            )


class DocumentViewSet(viewsets.ModelViewSet):
    """Gestion des documents personnels"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les documents selon l'utilisateur"""
        user = self.request.user
        
        if user.role in ['admin', 'rh']:
            return Document.objects.all()
        
        if hasattr(user, 'employee'):
            return Document.objects.filter(employee=user.employee)
        
        return Document.objects.none()
    
    def perform_create(self, serializer):
        """Créer un document"""
        user = self.request.user
        if user.role in ['admin', 'rh']:
            employee_id = self.request.data.get('employee_id')
            if employee_id:
                serializer.save(
                    employee_id=employee_id,
                    uploaded_by=user.employee if hasattr(user, 'employee') else None
                )
            else:
                serializer.save(uploaded_by=user.employee if hasattr(user, 'employee') else None)
            return

        if hasattr(user, 'employee'):
            serializer.save(
                employee=user.employee,
                uploaded_by=user.employee
            )
        else:
            raise serializers.ValidationError("Utilisateur non associé à un employé")
    
    @action(detail=False, methods=['get'])
    def my_documents(self, request):
        """Récupérer les documents de l'employé connecté"""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'Utilisateur non associé à un employé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        documents = Document.objects.filter(employee=request.user.employee)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    """Gestion des notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les notifications selon l'utilisateur"""
        user = self.request.user
        
        if hasattr(user, 'employee'):
            return Notification.objects.filter(employee=user.employee)
        
        return Notification.objects.none()
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Récupérer les notifications non lues"""
        unread = self.get_queryset().filter(is_read=False)
        serializer = NotificationSerializer(unread, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marquer toutes les notifications comme lues"""
        notifications = self.get_queryset().filter(is_read=False)
        now = timezone.now()
        
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
        
        Notification.objects.bulk_update(notifications, ['is_read', 'read_at'])
        
        return Response({'message': f'{notifications.count()} notifications marquées comme lues'})
