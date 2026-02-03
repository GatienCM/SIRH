from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Contract
from .serializers import ContractSerializer
from accounts.permissions import IsRH, IsAdmin


class ContractViewSet(viewsets.ModelViewSet):
    """ViewSet pour les contrats"""
    
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['employee', 'contract_type', 'status']
    search_fields = ['contract_number', 'employee__employee_id']
    
    def get_queryset(self):
        """Les salariés ne voient que leurs contrats, les RH voient tous"""
        user = self.request.user
        if user.role in ['rh', 'admin']:
            return Contract.objects.all()
        # Les salariés ne peuvent voir que leurs contrats
        try:
            from employees.models import Employee
            employee = Employee.objects.get(user=user)
            return Contract.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            return Contract.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_contracts(self, request):
        """Endpoint pour voir les contrats de l'utilisateur connecté"""
        try:
            from employees.models import Employee
            employee = Employee.objects.get(user=request.user)
            contracts = employee.contracts.all()
            serializer = self.get_serializer(contracts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Vous n\'êtes pas associé à un profil salarié'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def status(self, request, pk=None):
        """Endpoint pour récupérer le statut d'un contrat"""
        contract = self.get_object()
        return Response({
            'id': contract.id,
            'contract_number': contract.contract_number,
            'status': contract.status,
            'is_active': contract.is_active,
            'is_trial_period': contract.is_trial_period,
            'days_remaining': contract.days_remaining
        }, status=status.HTTP_200_OK)
