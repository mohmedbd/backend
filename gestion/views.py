from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer


class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer


class EnseignantViewSet(viewsets.ModelViewSet):
    queryset = Enseignant.objects.all()
    serializer_class = EnseignantSerializer


class AdministrateurViewSet(viewsets.ModelViewSet):
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer


class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer


class PlanificationViewSet(viewsets.ModelViewSet):
    queryset = Planification.objects.all()
    serializer_class = PlanificationSerializer


class SeanceQRViewSet(viewsets.ModelViewSet):
    queryset = SeanceQR.objects.all()
    serializer_class = SeanceQRSerializer


class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer


class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer