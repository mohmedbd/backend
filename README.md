## Installation (première fois)

git clone https://github.com/PresenceQRcode/BackEnd.git
cd BackEnd
python -m venv env
env\Scripts\Activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

## Endpoints disponibles

- GET   /home
- POST   /api/auth/login/
- GET/POST    /api/filieres/          ---Liste / créer filières
- GET/POST    /api/salles/            ---Liste / créer salles
- GET/POST    /api/enseignants/       ---Liste / créer enseignants
- GET/POST    /api/etudiants/         ---Liste / créer étudiants
- GET/POST    /api/administrateurs/   ---Liste / créer admins
- GET/POST    /api/planifications/    ---Liste / créer planifications
- GET/POST    /api/seances/           ---Liste / créer séances
- GET    /api/qrcodes/
- GET    /api/presences/
- POST   /api/auth/register/  -----> khas token d'acces admin bax ikhdm
- POST   /api/seances/generer/      --->Créer séance + premier QR Code 
- GET    /api/qrcode/seance/{id}/   --->QR Code actuel de seance d id =xx
- GET/POST    /api/qrcodes/         ---Liste / créer QR Codes
- GET/POST    /api/presences/       ---Liste / créer présences
- GET /api/planifications/aujourd-hui/  ---emploi du temps d'aujourd-hui
- POST api/etudiants/verifier/          --- verfier la presence d'un etudiant dans la base de donnees
- GET    /api/seances/{id}/presences/   --- pour recupirer la liste des presence actuel 

## body & response pour chaque api 

===============================================
POST /api/auth/login/
Body :
{
"email": "prof@fsmek.ma",
 "password": "motdepasse123"
}
Réponse :
{
"status": "success",
 "role": "enseignant",
 "tokens": {"refresh": "eyJ...",
 "access": "eyJ..."},
 "user": {"id": 1,
	 "email": "prof@fsmek.ma",
	 "nom": "Benali",
	 "prenom": "Karim"
}}

===============================================
POST /api/auth/register/
Body :
{ 
"email": "etudiant@fsmek.ma",
"password": "motdepasse123",
 "nom": "Alaoui",
 "prenom": "Sara",
 "role": "etudiant",
 "CIE": "P123456"
}
Réponse:
{"status": "success",
 "message": "Compte créé avec succès"
}


===============================================
GET /api/planifications/aujourd-hui/
Body : aucun
Réponse :
{
"jour": "vendredi",
 "date": "2026-05-22",
 "planifications": [{
	"id": 4,
	 "salle": "2.2",
	 "filiere": "SDIA",
	 "heure_debut": "10:42:15",
	 "heure_fin": "11:42:15",
	 "jour": "vendredi"
	}],
 "total": 1
}

===============================================
POST /api/seances/generer/
Body :
{"planification_id": 4}
Réponse :
{
"seance_id": 1,
 "token": "550e8400-e29b-41d4-a716-446655440000",
 "expire_dans": 60
}

===============================================
GET /api/qrcode/seance/{id}/             ex: /api/qrcode/seance/1/
Body : aucun
Réponse :
{
"token": "nouveau-uuid-...",
 "seance_id": 1,
 "expire_dans": 45
}

===============================================
POST /api/presences/scanner/
Body :
{
"token": "550e8400-e29b-41d4-a716-446655440000",
 "CIE": "P123456",
 "nom": "Alaoui",
 "prenom": "Sara"
}
Réponse :
{
"status": "success", 
"message": "Présence enregistrée pour Sara Alaoui", 
"heure": "10:47:32"
}

Erreurs possibles :
400 {"error": "token et CIE obligatoires"}
400 {"error": "QR Code expiré"}
400 {"error": "Présence déjà enregistrée"}
404 {"error": "QR Code invalide"}
404 {"error": "CIE introuvable"}

===================================================================
GET /api/etudiants/ 
Body : aucun
Réponse :
[{
"id": 1, 
"nom_etudiant": "Alaoui", 
"prenom_etudiant": "Sara", 
"CIE": "P123456", 
"filiere": 1
}]

==========================================================
POST /api/etudiants/
Body : {"nom_etudiant": "Alaoui", "prenom_etudiant": "Sara", "CIE": "P123456", "filiere": 1}
Réponse 201 : {"id": 1, "nom_etudiant": "Alaoui", "prenom_etudiant": "Sara", "CIE": "P123456", "filiere": 1}

============================================================
GET /api/filieres/
Réponse : [{"id": 1, "nom_filiere": "SDIA"}]

=========================================================
POST /api/filieres/
Body : {"nom_filiere": "SDIA"}
Réponse 201 : {"id": 1, "nom_filiere": "SDIA"}

================================================================
GET /api/salles/
Réponse : [{"id": 1, "nom_salle": "2.2"}]

=================================================================
POST /api/salles/
Body : {"nom_salle": "2.2"}
Réponse 201 : {"id": 1, "nom_salle": "2.2"}

=================================================================
GET /api/enseignants/
Réponse : [{"id": 1, "nom_enseignant": "Benali", "prenom_enseignant": "Karim", "email": "prof@fsmek.ma"}]

==================================================================
POST /api/enseignants/
Body : {"nom_enseignant": "Benali", "prenom_enseignant": "Karim", "email": "prof@fsmek.ma"}
Réponse 201 : {"id": 1, "nom_enseignant": "Benali", "prenom_enseignant": "Karim", "email": "prof@fsmek.ma"}

======================================================================
GET /api/administrateurs/
Réponse : [{"id": 1, "nom_admin": "Idrissi", "prenom_admin": "Omar", "email": "admin@fsmek.ma"}]

=========================================================================
POST /api/administrateurs/
Body : {"nom_admin": "Idrissi", "prenom_admin": "Omar", "email": "admin@fsmek.ma"}
Réponse 201 : {"id": 1, "nom_admin": "Idrissi", "prenom_admin": "Omar", "email": "admin@fsmek.ma"}

========================================================================
GET /api/planifications/
Réponse : [{"id": 4, "enseignant": 1, "salle": 1, "filiere": 1, "jour": "vendredi", "heure_debut": "10:00:00", "heure_fin": "12:00:00"}]

===========================================================================
POST /api/planifications/
Body : {"enseignant": 1, "salle": 1, "filiere": 1, "jour": "vendredi", "heure_debut": "10:00:00", "heure_fin": "12:00:00"}
Réponse 201 : {"id": 4, "enseignant": 1, "salle": 1, "filiere": 1, "jour": "vendredi", "heure_debut": "10:00:00", "heure_fin": "12:00:00"}

==================================================================
GET /api/seances/
Réponse : [{"id": 1, "planification": 4, "date": "2026-05-22"}]

==================================================================
POST /api/seances/
Body : {"planification": 4}
Réponse 201 : {"id": 1, "planification": 4, "date": "2026-05-22"}

====================================================================
GET /api/qrcodes/
Réponse : [{"id": 1, "seance": 1, "token": "550e8400-e29b-41d4-a716-446655440000", "cree_a": "2026-05-22T10:42:00Z", "expiration": 1}]

===============================================================
POST /api/qrcodes/
Body : {"seance": 1}
Réponse 201 : {"id": 1, "seance": 1, "token": "550e8400-e29b-41d4-a716-446655440000", "cree_a": "2026-05-22T10:42:00Z", "expiration": 1}

==================================================================
GET /api/presences/
Réponse : [{"id": 1, "etudiant": 1, "seance": 1, "date_scan": "2026-05-22", "heure_scan": "10:47:32"}]

=====================================================================
POST /api/presences/
Body : {"etudiant": 1, "seance": 1, "date_scan": "2026-05-22", "heure_scan": "10:47:32"}
Réponse 201 : {"id": 1, "etudiant": 1, "seance": 1, "date_scan": "2026-05-22", "heure_scan": "10:47:32"}

=====================================================================
POST api/etudiants/verifier/
Body :
{
    "CIE": "M33333",
    "nom": "haytham",
    "prenom": "ahodi",
    "email": "haytham@mail.com",
    "filiere": "SDIA",
    "password": "12345678"
}
Réponse :
{
    "found": true,
    "message": "Étudiant trouvé : ahodi haytham",
    "etudiant": {
        "id": 15,
        "nom": "haytham",
        "prenom": "ahodi",
        "email": "haytham@mail.com",
        "CIE": "M33333",
        "filiere": "SDIA"
    }
}
==================================================================
GET /api/seances/{id}/presences/     ici id == 3 
Réponse : {
    "seance_id": 3,
    "date": "2026-05-20",
    "planification": {
        "filiere": "SDIA",
        "salle": "2.2",
        "heure_debut": "08:00:00",
        "heure_fin": "12:00:00"
    },
    "total_presents": 0,
    "presences": []
}
=====================================================================