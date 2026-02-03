from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Vehicle
from .serializers import VehicleSerializer
from accounts.permissions import IsRH, IsAdmin, IsManager


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet pour les véhicules"""
    
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['vehicle_type', 'status']
    search_fields = ['vehicle_id', 'registration_number', 'brand', 'model']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def available(self, request):
        """Endpoint pour voir les véhicules disponibles"""
        vehicles = Vehicle.objects.filter(status='available')
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def maintenance_needed(self, request):
        """Endpoint pour voir les véhicules nécessitant une maintenance"""
        vehicles = [v for v in Vehicle.objects.all() if v.is_maintenance_needed]
        serializer = self.get_serializer(vehicles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def status(self, request, pk=None):
        """Endpoint pour récupérer le statut d'un véhicule"""
        vehicle = self.get_object()
        return Response({
            'id': vehicle.id,
            'vehicle_id': vehicle.vehicle_id,
            'status': vehicle.status,
            'is_available': vehicle.is_available,
            'current_mileage': vehicle.current_mileage,
            'is_maintenance_needed': vehicle.is_maintenance_needed,
            'is_inspection_needed': vehicle.is_inspection_needed,
            'is_insurance_valid': vehicle.is_insurance_valid
        }, status=status.HTTP_200_OK)
