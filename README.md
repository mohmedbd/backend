 # QRCode Backend

API Django REST pour le système de présence par QR Code.

## Stack technique
- Django 6.0.4
- Django REST Framework 3.17.1
- JWT (djangorestframework-simplejwt 5.5.1)

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

## Avant de commencer à coder (chaque jour)

git checkout main
git pull origin main
git checkout feat/ma-branche
git merge main
python manage.py runserver

## Après avoir codé

git status
git add .
git commit -m "feat: description"
git push origin feat/ma-branche

## Branches

- main                    → code stable
- feat/jwt-protection     → Marouan
- feat/register-endpoint  → Zaid

## Endpoints disponibles

- POST   /api/auth/login/
- GET    /api/filieres/
- GET    /api/salles/
- GET    /api/enseignants/
- GET    /api/etudiants/
- GET    /api/planifications/
- GET    /api/seances/
- GET    /api/qrcodes/
- GET    /api/presences/

## URL pour Flutter

Émulateur Android  → http://10.0.2.2:8000/api/
Émulateur iOS      → http://127.0.0.1:8000/api/
Téléphone physique → http://0.0.0.0:8000/api/
