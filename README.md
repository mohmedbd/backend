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

- POST   /api/auth/login/
- GET    /api/filieres/
- GET    /api/salles/
- GET    /api/enseignants/
- GET    /api/etudiants/
- GET    /api/planifications/
- GET    /api/seances/
- GET    /api/qrcodes/
- GET    /api/presences/
- POST   /api/auth/register/  -----> khas token d'acces admin bax ikhdm

## URL pour Flutter

Émulateur Android  → http://10.0.2.2:8000/api/
Émulateur iOS      → http://127.0.0.1:8000/api/
Téléphone physique → http://0.0.0.0:8000/api/
