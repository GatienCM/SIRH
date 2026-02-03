from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import (
    CustomUserSerializer,
    LoginSerializer,
    RegisterSerializer,
    ChangePasswordSerializer
)
from .permissions import IsOwnerOrAdmin

User = get_user_model()


class LoginView(generics.GenericAPIView):
    """Vue pour le login avec formulaire HTML"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Endpoint de connexion"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                'success': True,
                'message': 'Connexion réussie',
                'user': CustomUserSerializer(user).data,
                'session_id': request.session.session_key if request.session else None
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthViewSet(viewsets.ViewSet):
    """ViewSet pour l'authentification (logout, register, me, change_password)"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Endpoint de déconnexion"""
        request.session.flush()
        return Response({
            'success': True,
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Endpoint d'enregistrement"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Utilisateur créé avec succès',
                'user': CustomUserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Endpoint pour récupérer les infos de l'utilisateur connecté"""
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Endpoint pour changer le mot de passe"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'success': True,
                'message': 'Mot de passe changé avec succès'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les utilisateurs"""
    
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Les RH et admins voient tous les utilisateurs, les autres ne voient que leur profil"""
        user = self.request.user
        if user.role in ['rh', 'admin']:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_role(self, request):
        """Endpoint pour filtrer les utilisateurs par rôle"""
        role = request.query_params.get('role', None)
        if role:
            users = User.objects.filter(role=role)
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Veuillez spécifier un rôle'},
            status=status.HTTP_400_BAD_REQUEST
        )
