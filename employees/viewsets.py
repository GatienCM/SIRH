from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profession, Employee
from .serializers import ProfessionSerializer, EmployeeSerializer
from accounts.permissions import IsRH, IsAdmin


class ProfessionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les professions"""
    
    queryset = Profession.objects.filter(is_active=True)
    serializer_class = ProfessionSerializer
    permission_classes = [IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les salariés"""
    
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRH(), IsAdmin()]
        return [IsAuthenticated()]
    filterset_fields = ['status', 'profession', 'date_entry']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'phone']
    
    def get_queryset(self):
        """Les salariés ne voient que leur profil, les RH voient tous"""
        user = self.request.user
        if user.role in ['rh', 'admin']:
            return Employee.objects.select_related('user', 'profession')
        # Les salariés ne peuvent voir que leur propre profil
        try:
            return Employee.objects.select_related('user', 'profession').filter(user=user)
        except Employee.DoesNotExist:
            return Employee.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Endpoint pour récupérer le profil du salarié connecté"""
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = self.get_serializer(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Profil salarié non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def contracts(self, request, pk=None):
        """Endpoint pour voir les contrats d'un salarié"""
        employee = self.get_object()
        contracts = employee.contracts.all()
        from contracts.serializers import ContractSerializer
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
