from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import generer_seance_qr, get_qrcode_seance
from .views import (
    FiliereViewSet, SalleViewSet, EnseignantViewSet,
    AdministrateurViewSet, EtudiantViewSet, PlanificationViewSet,
    SeanceQRViewSet, QRCodeViewSet, PresenceViewSet
)

router = DefaultRouter()
router.register(r'filieres', FiliereViewSet)
router.register(r'salles', SalleViewSet)
router.register(r'enseignants', EnseignantViewSet)
router.register(r'administrateurs', AdministrateurViewSet)
router.register(r'etudiants', EtudiantViewSet)
router.register(r'planifications', PlanificationViewSet)
router.register(r'seances', SeanceQRViewSet)
router.register(r'qrcodes', QRCodeViewSet)
router.register(r'presences', PresenceViewSet)

urlpatterns = [
    path('seances/generer/', generer_seance_qr, name='generer-seance-qr'),
    path('qrcode/seance/<int:seance_id>/', get_qrcode_seance, name='get-qrcode-seance'),
    path('', include(router.urls)),
]
