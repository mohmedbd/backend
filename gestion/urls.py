from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import generer_seance_qr, get_qrcode_seance, planifications_du_jour
from .views import (
    FiliereViewSet, SemestreViewSet, ModuleViewSet, DepartementViewSet, SalleViewSet, AdminListViewSet,
    StudentListViewSet, ProfessorListViewSet, HeadOfDepartmentListViewSet,
    ProgramManagerListViewSet, PlanificationViewSet,
    SeanceQRViewSet, QRCodeViewSet, PresenceViewSet
)
from .views import (
    verifier_etudiant, liste_presences_seance, export_seance_excel,
    scanner_presence, update_profile_photo, my_profile,
    mes_planifications, mes_planifications_detail, emploi_du_temps_etudiant,
    importer_etudiants, importer_enseignants, etudiants_par_module,
    absences
)

router = DefaultRouter()
router.register(r'semestres', SemestreViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'departements', DepartementViewSet)
router.register(r'filieres', FiliereViewSet)
router.register(r'salles', SalleViewSet)
router.register(r'administrateurs', AdminListViewSet, basename='administrateur')
router.register(r'enseignants', ProfessorListViewSet, basename='enseignant')
router.register(r'etudiants', StudentListViewSet, basename='etudiant')
router.register(r'chefs-departement', HeadOfDepartmentListViewSet, basename='chef_departement')
router.register(r'responsables-filiere', ProgramManagerListViewSet, basename='responsable_filiere')
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
    path('mes-planifications/', mes_planifications, name='mes-planifications'),
    path('mes-planifications/<int:planification_id>/', mes_planifications_detail, name='mes-planifications-detail'),
    path('etudiants/emploi-du-temps/', emploi_du_temps_etudiant, name='emploi-du-temps-etudiant'),
    path('etudiants/importer/', importer_etudiants, name='importer-etudiants'),
    path('enseignants/importer/', importer_enseignants, name='importer-enseignants'),
    path('etudiants/par-module/', etudiants_par_module, name='etudiants-par-module'),
    path('absences/', absences, name='absences'),
    path('', include(router.urls)),
]
