# Contexte Backend Django — QRCode

## Environnement

- OS : Windows, PowerShell
- Editeur : VS Code
- Dossier ouvert dans VS Code : PROJET (pas S6)
- Chemin complet : C:\Users\HP\Desktop\S6\Basse de donnees avancees\PROJET

## Stack technique

- Django 6.0.4
- Django REST Framework 3.17.1
- JWT (djangorestframework-simplejwt 5.5.1)
- CORS headers 4.9.0
- Pillow 12.2.0
- Python-decouple 3.8

## Commandes importantes

# Activer l'env (PowerShell Windows)
env\Scripts\Activate

# Lancer le serveur
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

## Superuser créé

- Username : marouan
- Email : marouanahoudi@gmail.com

## Organisation GitHub

- Nom : PresenceQRcode
- Repo backend  : https://github.com/PresenceQRcode/BackEnd.git
- Repo frontend : https://github.com/PresenceQRcode/FrontEnd.git

## Membres

- Marouan (toi) → backend-team → branche : feat/jwt-protection
- Zaid          → backend-team → branche : feat/register-endpoint
- Adil          → frontend-team
- Mohamed       → frontend-team

## Workflow Git

### Avant de coder (chaque jour)
git checkout main
git pull origin main
git checkout feat/ma-branche
git merge main
python manage.py runserver

### Après avoir codé
git status
git add .
git commit -m "feat: description"
git push origin feat/ma-branche

### Convention commits
feat:     nouvelle fonctionnalité
fix:      correction d'un bug
refactor: amélioration du code
docs:     modification du README

## État actuel

- [x] Environnement virtuel créé
- [x] Dépendances installées
- [x] Projet Django créé (QRcode)
- [x] App users créée
- [x] App gestion créée
- [x] Migrations appliquées
- [x] Superuser créé
- [x] Admin accessible sur http://127.0.0.1:8000/admin/
- [x] VS Code configuré
- [x] Modèles Django créés (gestion/models.py)
- [x] Migrations des nouveaux modèles
- [x] Enregistrement des modèles dans admin.py
- [x] Serializers créés (gestion/serializers.py)
- [x] API endpoints créés (gestion/views.py + gestion/urls.py)
- [x] Authentification JWT (users/views.py + users/urls.py)
- [x] Organisation GitHub créée (PresenceQRcode)
- [x] Repo backend créé et pushé
- [x] Repo frontend créé
- [x] Teams créées (backend-team, frontend-team)
- [x] README.md avec workflow documenté
- [ ] Zaid : clone + branche feat/register-endpoint
- [ ] Adil + Mohamed : invités dans l'organisation
- [ ] Register endpoint
- [ ] Protection des routes avec JWT
- [ ] Génération QR Code

## Structure des apps

- users/     → Authentification (JWT, login, register)
- gestion/   → Logique métier (modèles du MLD)

## Modèles créés (gestion/models.py)

- Filiere
- Salle
- Enseignant
- Administrateur
- Etudiant
- Planification
- SeanceQR
- QRCode
- Presence

## INSTALLED_APPS (settings.py)

- rest_framework
- corsheaders
- rest_framework_simplejwt
- users
- gestion

## URLs

- http://127.0.0.1:8000/admin/          → Admin Django
- http://127.0.0.1:8000/api/            → API Root
- http://127.0.0.1:8000/api/auth/login/ → Login JWT

## Endpoints API disponibles

- GET/POST   api/filieres/
- GET/POST   api/salles/
- GET/POST   api/enseignants/
- GET/POST   api/administrateurs/
- GET/POST   api/etudiants/
- GET/POST   api/planifications/
- GET/POST   api/seances/
- GET/POST   api/qrcodes/
- GET/POST   api/presences/
- POST       api/auth/login/

## Login JWT — Réponse attendue

{
    "status": "success",
    "role": "etudiant | admin | enseignant",
    "tokens": {
        "refresh": "...",
        "access": "..."
    },
    "user": {
        "id": 1,
        "email": "...",
        "nom": "...",
        "prenom": "..."
    }
}

## URL Flutter selon environnement

- Émulateur Android  → http://10.0.2.2:8000/api/
- Émulateur iOS      → http://127.0.0.1:8000/api/
- Téléphone physique → http://0.0.0.0:8000/api/

## Fichiers importants

- QRcode/settings.py      → Configuration principale
- QRcode/urls.py          → URLs principales
- gestion/models.py       → Modèles Django
- gestion/serializers.py  → Serializers DRF
- gestion/views.py        → ViewSets API
- gestion/urls.py         → URLs gestion
- gestion/admin.py        → Enregistrement admin
- users/views.py          → Login JWT
- users/urls.py           → URLs authentification
- .env.example            → Template variables d'environnement
- requirements.txt        → Dépendances Python
- README.md               → Documentation + workflow Git

## Prochaine étape

→ Choisir parmi :
   1. Register endpoint (Zaid) — créer etudiant/enseignant via API
   2. Protection des routes avec JWT (Marouan)
   3. Génération QR Code (logique métier principale)