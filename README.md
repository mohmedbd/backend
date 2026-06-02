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

# Présence API — FSMeK

Système de gestion des présences par QR Code pour la Faculté des Sciences de Meknès.

---

## Table des matières

- [Informations générales](#informations-générales)
- [Authentification](#authentification)
- [Workflow séance & présences](#workflow-séance--présences)
- [Ressources CRUD](#ressources-crud)
  - [Filières](#filières)
  - [Salles](#salles)
  - [Enseignants](#enseignants)
  - [Étudiants](#étudiants)
  - [Administrateurs](#administrateurs)
  - [Planifications](#planifications)
  - [Séances](#séances)
  - [QR Codes](#qr-codes)
  - [Présences](#présences)

---

## Informations générales

| Propriété | Valeur |
|-----------|--------|
| Format | `application/json` |
| Authentification | `Authorization: Bearer <access_token>` |
| Expiration QR Code | 60 secondes (renouvelé automatiquement) |

---

## Authentification

### `POST /api/auth/login/`

Connexion d'un utilisateur (enseignant, étudiant ou admin).

**Body**
```json
{
  "email": "prof@fsmek.ma",
  "password": "motdepasse123"
}
```

**Réponse `200`**
```json
{
  "status": "success",
  "role": "enseignant",
  "tokens": {
    "refresh": "eyJ...",
    "access": "eyJ..."
  },
  "user": {
    "id": 1,
    "email": "prof@fsmek.ma",
    "nom": "Benali",
    "prenom": "Karim"
  }
}
```

---

### `POST /api/auth/register/`

> 🔒 Requiert un token d'accès admin.

Créer un nouveau compte utilisateur.

**Body**
```json
{
  "role": "etudiant",
  "nom": "Benali",
  "prenom": "Youssef",
  "email": "youssef.benali@gmail.com",
  "password": "test1234",
  "CIE": "C789012",
  "filier_etudiant": 1
}
```

> `filier_etudiant` est l'`id` de la filière (ex: `1` pour SDIA).

**Réponse `200`**
```json
{
  "status": "success",
  "message": "Compte créé avec succès"
}
```

---

## Workflow séance & présences

Ordre d'utilisation typique par un enseignant :

```
1. GET  /api/planifications/aujourd-hui/   → récupérer la planification du jour
2. POST /api/seances/generer/              → créer la séance + premier QR Code
3. GET  /api/qrcode/seance/{id}/          → rafraîchir le QR Code (toutes les ~60s)
4. POST /api/presences/scanner/            → les étudiants scannent le QR
5. GET  /api/seances/{id}/presences/      → consulter la liste des présents
6. GET  /api/seances/{id}/export/         → exporter en Excel
```

---

### `GET /api/planifications/aujourd-hui/`

Retourne l'emploi du temps du jour courant.

**Réponse `200`**
```json
{
  "jour": "vendredi",
  "date": "2026-05-22",
  "planifications": [
    {
      "id": 4,
      "salle": "2.2",
      "filiere": "SDIA",
      "heure_debut": "10:42:15",
      "heure_fin": "11:42:15",
      "jour": "vendredi"
    }
  ],
  "total": 1
}
```

---

### `POST /api/seances/generer/`

Crée une séance à partir d'une planification et génère le premier QR Code.

**Body**
```json
{
  "planification_id": 4
}
```

**Réponse `200`**
```json
{
  "seance_id": 1,
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "expire_dans": 60
}
```

---

### `GET /api/qrcode/seance/{id}/`

Récupère le QR Code actuel d'une séance (se renouvelle automatiquement).

**Réponse `200`**
```json
{
  "token": "nouveau-uuid-...",
  "seance_id": 1,
  "expire_dans": 45
}
```

---

### `POST /api/etudiants/verifier/`

Vérifie l'existence d'un étudiant dans la base de données avant de scanner.

**Body**
```json
{
  "CIE": "M33333",
  "nom": "haytham",
  "prenom": "ahodi",
  "email": "haytham@mail.com",
  "filiere": "SDIA",
  "password": "12345678"
}
```

**Réponse `200`**
```json
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
```

---

### `POST /api/presences/scanner/`

Enregistre la présence d'un étudiant via le token QR Code.

**Body**
```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "CIE": "P123456",
  "nom": "Alaoui",
  "prenom": "Sara"
}
```

**Réponse `200`**
```json
{
  "status": "success",
  "message": "Présence enregistrée pour Sara Alaoui",
  "heure": "10:47:32"
}
```

**Erreurs possibles**

| Code | Message |
|------|---------|
| `400` | `token et CIE obligatoires` |
| `400` | `QR Code expiré` |
| `400` | `Présence déjà enregistrée` |
| `404` | `QR Code invalide` |
| `404` | `CIE introuvable` |

---

### `GET /api/seances/{id}/presences/`

Retourne la liste des présences enregistrées pour une séance.

**Réponse `200`**
```json
{
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
```

---

### `GET /api/seances/{id}/export/`

> 🔒 Requiert un token enseignant.

Télécharge la feuille de présences au format Excel.

**Réponse** : fichier `presences_seance_{id}_{date}.xlsx`

---

## Ressources CRUD

### Filières

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/filieres/` | Liste toutes les filières |
| `POST` | `/api/filieres/` | Créer une filière |

**POST body**
```json
{ "nom_filiere": "SDIA" }
```

**Réponse `201`**
```json
{ "id": 1, "nom_filiere": "SDIA" }
```

---

### Salles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/salles/` | Liste toutes les salles |
| `POST` | `/api/salles/` | Créer une salle |

**POST body**
```json
{ "nom_salle": "2.2" }
```

**Réponse `201`**
```json
{ "id": 1, "nom_salle": "2.2" }
```

---

### Enseignants

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/enseignants/` | Liste tous les enseignants |
| `POST` | `/api/enseignants/` | Créer un enseignant |

**POST body**
```json
{
  "nom_enseignant": "Benali",
  "prenom_enseignant": "Karim",
  "email": "prof@fsmek.ma"
}
```

**Réponse `201`**
```json
{ "id": 1, "nom_enseignant": "Benali", "prenom_enseignant": "Karim", "email": "prof@fsmek.ma" }
```

---

### Étudiants

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/etudiants/` | Liste tous les étudiants |
| `POST` | `/api/etudiants/` | Créer un étudiant |

**POST body**
```json
{
  "nom_etudiant": "Alaoui",
  "prenom_etudiant": "Sara",
  "CIE": "P123456",
  "filiere": 1
}
```

**Réponse `201`**
```json
{ "id": 1, "nom_etudiant": "Alaoui", "prenom_etudiant": "Sara", "CIE": "P123456", "filiere": 1 }
```

---

### Administrateurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/administrateurs/` | Liste tous les admins |
| `POST` | `/api/administrateurs/` | Créer un admin |

**POST body**
```json
{
  "nom_admin": "Idrissi",
  "prenom_admin": "Omar",
  "email": "admin@fsmek.ma"
}
```

**Réponse `201`**
```json
{ "id": 1, "nom_admin": "Idrissi", "prenom_admin": "Omar", "email": "admin@fsmek.ma" }
```

---

### Planifications

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/planifications/` | Liste toutes les planifications |
| `POST` | `/api/planifications/` | Créer une planification |

**POST body**
```json
{
  "enseignant": 1,
  "salle": 1,
  "filiere": 1,
  "jour": "vendredi",
  "heure_debut": "10:00:00",
  "heure_fin": "12:00:00"
}
```

**Réponse `201`**
```json
{ "id": 4, "enseignant": 1, "salle": 1, "filiere": 1, "jour": "vendredi", "heure_debut": "10:00:00", "heure_fin": "12:00:00" }
```

---

### Séances

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/seances/` | Liste toutes les séances |
| `POST` | `/api/seances/` | Créer une séance |

**POST body**
```json
{ "planification": 4 }
```

**Réponse `201`**
```json
{ "id": 1, "planification": 4, "date": "2026-05-22" }
```

---

### QR Codes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/qrcodes/` | Liste tous les QR Codes |
| `POST` | `/api/qrcodes/` | Créer un QR Code |

**POST body**
```json
{ "seance": 1 }
```

**Réponse `201`**
```json
{ "id": 1, "seance": 1, "token": "550e8400-...", "cree_a": "2026-05-22T10:42:00Z", "expiration": 1 }
```

---

### Présences

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/presences/` | Liste toutes les présences |
| `POST` | `/api/presences/` | Créer une présence manuellement |

**POST body**
```json
{
  "etudiant": 1,
  "seance": 1,
  "date_scan": "2026-05-22",
  "heure_scan": "10:47:32"
}
```

**Réponse `201`**
```json
{ "id": 1, "etudiant": 1, "seance": 1, "date_scan": "2026-05-22", "heure_scan": "10:47:32" }
```
