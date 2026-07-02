from django.contrib import admin
from .models import (
    Filiere,
    Salle,
    Enseignant,
    Administrateur,
    Etudiant,
    Planification,
    SeanceQR,
    QRCode,
    Presence,
)

admin.site.register(Filiere)
admin.site.register(Salle)
admin.site.register(Enseignant)
admin.site.register(Administrateur)
admin.site.register(Etudiant)
admin.site.register(Planification)
admin.site.register(SeanceQR)
admin.site.register(QRCode)
admin.site.register(Presence)