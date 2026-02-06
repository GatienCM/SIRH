from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import ShiftType, Shift, Assignment
from .serializers import ShiftTypeSerializer, ShiftSerializer, AssignmentSerializer
from accounts.permissions import IsRH, IsAdmin


class ShiftTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les types de shifts"""
    
    queryset = ShiftType.objects.filter(is_active=True)
    serializer_class = ShiftTypeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['name', 'is_active']
    search_fields = ['name', 'description']


class ShiftViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les shifts"""
    
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'cancel']:
            return [IsRH(), IsAdmin()]
        return [IsAuthenticated()]
    filterset_fields = ['date', 'status', 'shift_type']
    search_fields = ['notes']
    ordering_fields = ['date', 'start_time', 'created_at']
    ordering = ['-date', '-start_time']
    
    def perform_create(self, serializer):
        """Créer un shift avec l'utilisateur actuel"""
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """Les RH/Admins voient tous les shifts, les autres ne voient que les shifts futurs"""
        user = self.request.user
        queryset = Shift.objects.select_related('shift_type').prefetch_related('assignments')
        
        if user.role not in ['admin', 'rh']:
            # Les employés ne voient que les shifts futurs
            today = timezone.now().date()
            queryset = queryset.filter(date__gte=today)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def upcoming(self, request):
        """Récupérer les shifts à venir (7 prochains jours)"""
        today = timezone.now().date()
        week_end = today + timedelta(days=7)
        shifts = self.queryset.filter(
            date__gte=today,
            date__lt=week_end,
            status__in=['planned', 'ongoing']
        )
        serializer = self.get_serializer(shifts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_date(self, request):
        """Récupérer les shifts pour une date spécifique"""
        date_str = request.query_params.get('date', None)
        if not date_str:
            return Response(
                {'error': 'Le paramètre "date" est requis (format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            shifts = self.queryset.filter(date=date)
            serializer = self.get_serializer(shifts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {'error': 'Format de date invalide (utilisez YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsAdmin])
    def cancel(self, request, pk=None):
        """Annuler un shift"""
        shift = self.get_object()
        if shift.status == 'completed':
            return Response(
                {'error': 'Impossible d\'annuler un shift complété'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shift.status = 'cancelled'
        shift.save()
        serializer = self.get_serializer(shift)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les assignments"""
    
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'confirm', 'mark_absent', 'mark_completed']:
            return [IsRH(), IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        vehicle = serializer.validated_data.get('vehicle')
        if vehicle and vehicle.status != 'available':
            raise serializers.ValidationError({'vehicle': 'Véhicule indisponible (maintenance ou hors service).'} )
        serializer.save()
    filterset_fields = ['shift__date', 'employee', 'status', 'vehicle']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    ordering_fields = ['shift__date', 'status', 'created_at']
    ordering = ['-shift__date', 'status']
    
    def get_queryset(self):
        """Les employés ne voient que leurs assignments, les RH/Admins voient tous"""
        user = self.request.user
        queryset = Assignment.objects.select_related('shift', 'employee__user', 'vehicle')
        
        if user.role == 'employee':
            # Afficher seulement les assignments de l'employé
            try:
                from employees.models import Employee
                employee = Employee.objects.get(user=user)
                queryset = queryset.filter(employee=employee)
            except:
                queryset = Assignment.objects.none()
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_schedule(self, request):
        """Récupérer le planning personnel de l'utilisateur connecté"""
        user = request.user
        try:
            from employees.models import Employee
            employee = Employee.objects.get(user=user)
            assignments = Assignment.objects.filter(employee=employee).order_by('-shift__date')
            serializer = self.get_serializer(assignments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(
                {'error': 'Employé non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_shift(self, request):
        """Récupérer tous les assignments pour un shift spécifique"""
        shift_id = request.query_params.get('shift_id', None)
        if not shift_id:
            return Response(
                {'error': 'Le paramètre "shift_id" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignments = self.queryset.filter(shift_id=shift_id)
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsAdmin])
    def confirm(self, request, pk=None):
        """Confirmer un assignment"""
        assignment = self.get_object()
        if assignment.status == 'confirmed':
            return Response(
                {'error': 'L\'assignment est déjà confirmé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment.status = 'confirmed'
        assignment.confirmed_at = timezone.now()
        assignment.save()
        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsAdmin])
    def mark_absent(self, request, pk=None):
        """Marquer un employé comme absent"""
        assignment = self.get_object()
        if assignment.status in ['completed', 'absent']:
            return Response(
                {'error': 'Impossible de modifier cet assignment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment.status = 'absent'
        assignment.save()
        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsRH | IsAdmin])
    def mark_completed(self, request, pk=None):
        """Marquer un assignment comme complété"""
        assignment = self.get_object()
        assignment.status = 'completed'
        assignment.save()
        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)
