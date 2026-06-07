from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import generer_seance_qr, get_qrcode_seance, planifications_du_jour
from .views import (
    FiliereViewSet, SalleViewSet, EnseignantViewSet,
    AdministrateurViewSet, EtudiantViewSet, PlanificationViewSet,
    SeanceQRViewSet, QRCodeViewSet, PresenceViewSet
)
from .views import (
    verifier_etudiant, liste_presences_seance, export_seance_excel,
    scanner_presence, update_profile_photo, my_profile
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
    path('planifications/aujourd-hui/', planifications_du_jour, name='planifications-jour'),
    path('etudiants/verifier/', verifier_etudiant, name='verifier-etudiant'),
    path('seances/<int:seance_id>/presences/', liste_presences_seance, name='liste-presences-seance'),
    path('seances/<int:seance_id>/export/', export_seance_excel, name='export-seance'),
    path('presences/scanner/', scanner_presence, name='scanner-presence'),
    path('profile/', my_profile, name='my-profile'),
    path('profile/photo/', update_profile_photo, name='update-profile-photo'),
    path('', include(router.urls)),
]
