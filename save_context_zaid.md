# Contexte Backend Django — QRCode (Zaid)

## Environnement

- OS : Windows, PowerShell
- Editeur : VS Code
- Chemin complet : C:\Users\DELL\OneDrive\Desktop\s6\stagePfe\QR_PFE\BackEnd

## Stack technique

- Django 6.0.4
- Django REST Framework 3.17.1
- JWT (djangorestframework-simplejwt 5.5.1)
- CORS headers 4.9.0
- Pillow 12.2.0
- Python-decouple 3.8
- dj-database-url 3.1.2
- psycopg2-binary 2.9.12
- gunicorn 21.2.0

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

## Git config (Zaid)

- user.name  : Zaid
- user.email : aitouissaadenza@gmail.com

## Organisation GitHub

- Nom : PresenceQRcode
- Repo backend  : https://github.com/PresenceQRcode/BackEnd.git
- Repo frontend : https://github.com/PresenceQRcode/FrontEnd.git

## Membres

- Marouan → backend-team → branche : feat/jwt-protection
- Zaid    → backend-team → branche : feat/jwt-protection ✅ TERMINÉ
- Adil    → frontend-team
- Mohamed → frontend-team

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
- [x] Modèles Django créés (gestion/models.py)
- [x] Serializers créés (gestion/serializers.py)
- [x] API endpoints créés (gestion/views.py + gestion/urls.py)
- [x] Authentification JWT (users/views.py + users/urls.py)
- [x] Base de données migrée vers PostgreSQL (NeonDB)
- [x] Settings adaptés pour la production (DEBUG, SECRET_KEY via .env)
- [x] Vue /home ajoutée (health check Render)
- [x] Protection des routes avec JWT ✅
- [x] Login public avec AllowAny ✅
- [x] Tests Postman réussis ✅
- [x] Push sur feat/jwt-protection ✅
- [ ] Merger feat/jwt-protection dans main
- [ ] Register endpoint
- [ ] Génération QR Code

## Ce qui a été fait — feat/jwt-protection

### gestion/views.py
- Ajout de `JWTAuthentication` et `IsAuthenticated` sur tous les ViewSets
- Route `home` marquée `AllowAny` (publique)

### users/views.py
- Route `login` marquée `@permission_classes([AllowAny])` (publique)
- Route `register` déjà présente (à connecter dans urls.py)

### QRcode/settings.py
- Bloc REST_FRAMEWORK avec JWT par défaut :
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

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

- http://127.0.0.1:8000/admin/           → Admin Django
- http://127.0.0.1:8000/api/             → API Root
- http://127.0.0.1:8000/api/auth/login/  → Login JWT (public)
- http://127.0.0.1:8000/home             → Health check (public)

## Endpoints API (tous protégés JWT sauf login et home)

- GET/POST   api/filieres/
- GET/POST   api/salles/
- GET/POST   api/enseignants/
- GET/POST   api/administrateurs/
- GET/POST   api/etudiants/
- GET/POST   api/planifications/
- GET/POST   api/seances/
- GET/POST   api/qrcodes/
- GET/POST   api/presences/
- POST       api/auth/login/    ← public
- POST       api/auth/register/ ← à connecter dans urls.py

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

## Base de données — Production

- Provider : NeonDB (PostgreSQL)
- URL : dans la variable d'environnement DATABASE_URL
- Ne jamais committer la DATABASE_URL dans le code

## Variables d'environnement (.env)

- SECRET_KEY   → clé secrète Django
- DEBUG        → True (local) / False (production)
- DATABASE_URL → URL NeonDB PostgreSQL

## Fichiers importants

- QRcode/settings.py      → Configuration principale
- QRcode/urls.py          → URLs principales
- gestion/models.py       → Modèles Django
- gestion/serializers.py  → Serializers DRF
- gestion/views.py        → ViewSets API + vue home (JWT protégé)
- gestion/urls.py         → URLs gestion
- gestion/admin.py        → Enregistrement admin
- users/views.py          → Login (public) + Register (admin only)
- users/urls.py           → URLs authentification
- .env                    → Variables d'environnement (ne pas committer)
- requirements.txt        → Dépendances Python

## Prochaine étape

→ Register endpoint :
   1. Vérifier que register est bien dans users/urls.py
   2. Tester avec Postman (token admin requis)
   3. Merger feat/jwt-protection dans main
   4. Push main
