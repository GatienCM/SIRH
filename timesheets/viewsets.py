from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from .models import TimeSheet, TimeSheetEntry, AbsenceRecord
from .serializers import TimeSheetSerializer, TimeSheetEntrySerializer, AbsenceRecordSerializer
from accounts.permissions import IsRH, IsAdmin
from employees.models import Employee


class TimeSheetViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les feuilles de temps"""
    
    queryset = TimeSheet.objects.all()
    serializer_class = TimeSheetSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'year', 'month', 'status']
    ordering_fields = ['year', 'month', 'created_at']
    ordering = ['-year', '-month']
    
    def get_queryset(self):
        """Les employés ne voient que leurs propres feuilles, les RH/Admins voient toutes"""
        user = self.request.user
        queryset = TimeSheet.objects.select_related('employee__user')
        
        if user.role == 'employee':
            try:
                employee = Employee.objects.get(user=user)
                queryset = queryset.filter(employee=employee)
            except:
                queryset = TimeSheet.objects.none()
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current_month(self, request):
        """Récupérer la feuille de temps du mois courant"""
        today = timezone.now().date()
        user = request.user
        
        try:
            employee = Employee.objects.get(user=user)
            timesheet = TimeSheet.objects.get(
                employee=employee,
                year=today.year,
                month=today.month
            )
            serializer = self.get_serializer(timesheet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TimeSheet.DoesNotExist:
            return Response(
                {'error': 'Aucune feuille de temps pour ce mois'},
                status=status.HTTP_404_NOT_FOUND
            )
        except:
            return Response(
                {'error': 'Employé non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """Soumettre une feuille de temps"""
        timesheet = self.get_object()
        if request.user.role == 'employee':
            try:
                employee = Employee.objects.get(user=request.user)
                if timesheet.employee_id != employee.id:
                    return Response(
                        {'error': 'Accès non autorisé'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Employee.DoesNotExist:
                return Response(
                    {'error': 'Employé non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
        if timesheet.status != 'draft':
            return Response(
                {'error': 'Seules les brouillons peuvent être soumis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        timesheet.status = 'submitted'
        timesheet.submitted_at = timezone.now()
        timesheet.save()
        serializer = self.get_serializer(timesheet)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsAdmin])
    def approve(self, request, pk=None):
        """Approuver une feuille de temps"""
        timesheet = self.get_object()
        if timesheet.status != 'submitted':
            return Response(
                {'error': 'Seules les feuilles soumises peuvent être approuvées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        timesheet.status = 'approved'
        timesheet.approved_at = timezone.now()
        timesheet.approved_by = request.user
        timesheet.save()
        serializer = self.get_serializer(timesheet)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsAdmin])
    def reject(self, request, pk=None):
        """Rejeter une feuille de temps"""
        timesheet = self.get_object()
        if timesheet.status != 'submitted':
            return Response(
                {'error': 'Seules les feuilles soumises peuvent être rejetées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        timesheet.status = 'draft'
        timesheet.submitted_at = None
        timesheet.save()
        serializer = self.get_serializer(timesheet)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsAdmin])
    def mark_paid(self, request, pk=None):
        """Marquer une feuille de temps comme payée"""
        timesheet = self.get_object()
        if timesheet.status != 'approved':
            return Response(
                {'error': 'Seules les feuilles approuvées peuvent être marquées comme payées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        timesheet.status = 'paid'
        timesheet.save()
        serializer = self.get_serializer(timesheet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TimeSheetEntryViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les entrées de feuille de temps"""
    
    queryset = TimeSheetEntry.objects.all()
    serializer_class = TimeSheetEntrySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['timesheet', 'date', 'hour_type']
    ordering_fields = ['date', 'hour_type']
    ordering = ['-date']
    
    def get_queryset(self):
        """Filtrer par feuille de temps de l'utilisateur"""
        user = self.request.user
        queryset = TimeSheetEntry.objects.select_related('timesheet', 'assignment', 'timesheet__employee__user')
        
        if user.role == 'employee':
            try:
                employee = Employee.objects.get(user=user)
                queryset = queryset.filter(timesheet__employee=employee)
            except:
                queryset = TimeSheetEntry.objects.none()
        
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_create_from_assignments(self, request):
        """Créer automatiquement les entrées à partir des assignments"""
        timesheet_id = request.data.get('timesheet_id')
        
        if not timesheet_id:
            return Response(
                {'error': 'timesheet_id est obligatoire'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            timesheet = TimeSheet.objects.get(id=timesheet_id)
        except TimeSheet.DoesNotExist:
            return Response(
                {'error': 'Feuille de temps non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Contrôle d'accès : employé uniquement sur sa propre feuille
        if request.user.role == 'employee':
            try:
                employee = Employee.objects.get(user=request.user)
                if timesheet.employee_id != employee.id:
                    return Response(
                        {'error': 'Accès non autorisé'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Employee.DoesNotExist:
                return Response(
                    {'error': 'Employé non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Récupérer tous les assignments du mois
        from planning.models import Assignment
        first_day = date(timesheet.year, timesheet.month, 1)
        if timesheet.month == 12:
            last_day = date(timesheet.year + 1, 1, 1) - timezone.timedelta(days=1)
        else:
            last_day = date(timesheet.year, timesheet.month + 1, 1) - timezone.timedelta(days=1)
        
        assignments = Assignment.objects.filter(
            employee=timesheet.employee,
            shift__date__gte=first_day,
            shift__date__lte=last_day,
            status__in=['assigned', 'confirmed', 'in_progress', 'completed']
        )
        
        created_count = 0
        for assignment in assignments:
            # Déterminer le type d'heures basé sur le shift type
            shift_type = assignment.shift.shift_type.name
            if shift_type == 'night':
                hour_type = 'night'
            elif shift_type == 'sunday':
                hour_type = 'sunday'
            elif shift_type == 'holiday':
                hour_type = 'holiday'
            else:
                hour_type = 'normal'
            
            # Créer l'entrée
            entry, created = TimeSheetEntry.objects.get_or_create(
                timesheet=timesheet,
                assignment=assignment,
                date=assignment.shift.date,
                defaults={
                    'hour_type': hour_type,
                    'hours_worked': assignment.shift.duration_hours,
                    'hourly_rate': 0  # À définir selon le contrat
                }
            )
            if created:
                created_count += 1
        
        return Response(
            {'message': f'{created_count} entrées créées'},
            status=status.HTTP_200_OK
        )


class AbsenceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les absences"""
    
    queryset = AbsenceRecord.objects.all()
    serializer_class = AbsenceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'absence_type', 'date_start']
    ordering_fields = ['date_start', 'date_end']
    ordering = ['-date_start']
    
    def get_queryset(self):
        """Filtrer par employé"""
        user = self.request.user
        queryset = AbsenceRecord.objects.all()
        
        if user.role == 'employee':
            try:
                employee = Employee.objects.get(user=user)
                queryset = queryset.filter(employee=employee)
            except:
                queryset = AbsenceRecord.objects.none()
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current_month(self, request):
        """Récupérer les absences du mois courant"""
        today = timezone.now().date()
        absences = self.queryset.filter(
            date_start__year=today.year,
            date_start__month=today.month
        )
        serializer = self.get_serializer(absences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
