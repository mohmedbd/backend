from django.contrib import admin
from .models import (
    Departement,
    Filiere,
    Salle,
    Planification,
    SeanceQR,
    QRCode,
    Presence,
)
from users.models import (
    AdminProfile, ProfessorProfile, HeadOfDepartmentProfile,
    ProgramManagerProfile, StudentProfile,
)


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['nom_departement', 'description']
    search_fields = ['nom_departement']


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ['nom_filiere', 'semester_filiere', 'departement']
    search_fields = ['nom_filiere']


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ['nom_salle', 'type_salle', 'location']
    search_fields = ['nom_salle']


@admin.register(Planification)
class PlanificationAdmin(admin.ModelAdmin):
    list_display = ['module', 'professor', 'salle', 'filiere', 'jour', 'heure_debut', 'heure_fin']
    list_filter = ['jour', 'filiere']
    search_fields = ['module', 'professor__email', 'professor__last_name']


@admin.register(SeanceQR)
class SeanceQRAdmin(admin.ModelAdmin):
    list_display = ['id', 'planification', 'date', 'latitude_prof', 'longitude_prof']


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['token', 'seance', 'cree_a', 'expiration']
    readonly_fields = ['token', 'cree_a']


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'seance', 'date_scan', 'heure_scan', 'ip_address']
    list_filter = ['date_scan']
    search_fields = ['student__email', 'student__last_name']


