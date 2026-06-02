from django.db import models
import uuid


#1 Filière
class Filiere(models.Model):
    nom_filiere        = models.CharField(max_length=30)
    semester_filiere   = models.CharField(max_length=30)
    departement_filiere = models.CharField(max_length=30)

    def __str__(self):
        return self.nom_filiere


#2 Salle
class Salle(models.Model):
    type_salle = models.CharField(max_length=30)
    nom_salle  = models.CharField(max_length=30)
    location   = models.CharField(max_length=30)

    def __str__(self):
        return self.nom_salle


#3 Enseignant
class Enseignant(models.Model):
    nom_enseignant    = models.CharField(max_length=30)
    prenom_enseignant = models.CharField(max_length=30)
    email_enseignant  = models.EmailField(unique=True)
    password_enseignant = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.prenom_enseignant} {self.nom_enseignant}"


#4 Admin (gestionnaire)
class Administrateur(models.Model):
    nom_admin      = models.CharField(max_length=30)
    prenom_admin   = models.CharField(max_length=30)
    email_admin    = models.EmailField(unique=True)
    password_admin = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.prenom_admin} {self.nom_admin}"


#5 Étudiant
class Etudiant(models.Model):
    nom_etudiant      = models.CharField(max_length=30)
    prenom_etudiant   = models.CharField(max_length=30)
    email_etudiant    = models.EmailField(unique=True)
    password_etudiant = models.CharField(max_length=128)
    filier_etudiant   = models.ForeignKey(   
        Filiere,
        on_delete=models.SET_NULL,
        null=True
    )
    CIE               = models.CharField(max_length=30, unique=True)

#6 Planification
class Planification(models.Model):
    enseignant  = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    salle       = models.ForeignKey(Salle, on_delete=models.CASCADE)
    filiere     = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    jour        = models.CharField(max_length=30)
    heure_debut = models.TimeField()
    heure_fin   = models.TimeField()
    semestre    = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.jour} - {self.enseignant}"


#7 Séance QR
class SeanceQR(models.Model):
    planification = models.ForeignKey(Planification, on_delete=models.CASCADE)
    date          = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Séance {self.date}"


#8 QR Code
class QRCode(models.Model):
    seance     = models.ForeignKey(SeanceQR, on_delete=models.CASCADE)
    token      = models.UUIDField(default=uuid.uuid4, unique=True)
    cree_a = models.DateTimeField(auto_now_add=True)
    expiration = models.IntegerField(default=1)  # minutes

    def is_valid(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() < self.cree_a + timedelta(minutes=self.expiration)

    def __str__(self):
        return f"QR - Séance {self.seance}"

#9 Présence
class Presence(models.Model):
    etudiant   = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    seance     = models.ForeignKey(SeanceQR, on_delete=models.CASCADE)
    date_scan  = models.DateField()
    heure_scan = models.TimeField()

    def __str__(self):
        return f"{self.etudiant} - {self.date_scan}"