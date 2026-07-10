from django.db import models
import uuid
from django.conf import settings


class Departement(models.Model):
    nom_departement = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom_departement


class Filiere(models.Model):
    nom_filiere         = models.CharField(max_length=30)
    semester_filiere    = models.CharField(max_length=30)
    departement         = models.ForeignKey(
        Departement, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='filieres'
    )

    def __str__(self):
        return self.nom_filiere


class Module(models.Model):
    nom_module = models.CharField(max_length=100, unique=True)
    filiere = models.ForeignKey(
        Filiere, on_delete=models.CASCADE,
        null=True, blank=True, related_name='modules'
    )

    def __str__(self):
        return self.nom_module


class Salle(models.Model):
    type_salle = models.CharField(max_length=30)
    nom_salle  = models.CharField(max_length=30)
    location   = models.CharField(max_length=30)

    def __str__(self):
        return self.nom_salle


class Planification(models.Model):
    professor   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='planifications',
    )
    salle       = models.ForeignKey(Salle, on_delete=models.CASCADE)
    filiere     = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    module      = models.CharField(max_length=100)
    jour        = models.CharField(max_length=30)
    heure_debut = models.TimeField()
    heure_fin   = models.TimeField()

    def __str__(self):
        return f"{self.jour} - {self.professor}"

    @property
    def professor_profile(self):
        return getattr(self.professor, 'professor_profile', None)


class SeanceQR(models.Model):
    planification = models.ForeignKey(Planification, on_delete=models.CASCADE)
    date          = models.DateField(auto_now_add=True)
    latitude_prof    = models.FloatField(null=True, blank=True)
    longitude_prof   = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Séance {self.date}"


class QRCode(models.Model):
    seance     = models.ForeignKey(SeanceQR, on_delete=models.CASCADE)
    token      = models.UUIDField(default=uuid.uuid4, unique=True)
    cree_a = models.DateTimeField(auto_now_add=True)
    expiration = models.IntegerField(default=1)

    def is_valid(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() < self.cree_a + timedelta(minutes=self.expiration)

    def __str__(self):
        return f"QR - Séance {self.seance}"


class Presence(models.Model):
    student    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presences',
    )
    seance     = models.ForeignKey(SeanceQR, on_delete=models.CASCADE)
    date_scan  = models.DateField()
    heure_scan = models.TimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.date_scan}"
