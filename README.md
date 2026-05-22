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

## URL pour Flutter

Émulateur Android  → http://10.0.2.2:8000/api/
Émulateur iOS      → http://127.0.0.1:8000/api/
Téléphone physique → http://0.0.0.0:8000/api/
