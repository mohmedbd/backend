from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import (
    Filiere, Salle, Enseignant, Administrateur,
    Etudiant, Planification, SeanceQR, QRCode, Presence
)
from .serializers import (
    FiliereSerializer, SalleSerializer, EnseignantSerializer,
    AdministrateurSerializer, EtudiantSerializer, PlanificationSerializer,
    SeanceQRSerializer, QRCodeSerializer, PresenceSerializer
)

class FiliereViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer

class SalleViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer

class EnseignantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Enseignant.objects.all()
    serializer_class = EnseignantSerializer

class AdministrateurViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer

class EtudiantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer

class PlanificationViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Planification.objects.all()
    serializer_class = PlanificationSerializer

class SeanceQRViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = SeanceQR.objects.all()
    serializer_class = SeanceQRSerializer

class QRCodeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer

class PresenceViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return HttpResponse("Render works!")