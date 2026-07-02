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
| Access Token Lifetime | 1 jour |
| Refresh Token Lifetime | 7 jours |

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

### `POST /api/auth/token/refresh/`

Rafraîchit le token d'accès à partir du refresh token. **Utilisez cet endpoint quand vous recevez une erreur 401.**

**Body**
```json
{
  "refresh": "eyJ..."
}
```

**Réponse `200`**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

**Erreurs**
```json
{ "error": "Refresh token manquant" }     // 400
{ "error": "Token invalide ou expiré" }   // 401
```

> 💡 **Frontend:** Implémentez un intercepteur HTTP qui appelle cet endpoint automatiquement quand vous recevez 401.

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
1. GET  /api/planifications/aujourd-hui/        → récupérer la planification du jour
2. POST /api/seances/generer/                   → créer la séance + premier QR Code
3. GET  /api/qrcode/seance/{id}/                → rafraîchir le QR Code (toutes les ~60s)
4. POST /api/etudiants/verifier/                → vérifier l'étudiant avant de scanner
5. POST /api/presences/scanner/                 → les étudiants scannent le QR
6. GET  /api/seances/{id}/presences/            → consulter la liste des présents
7. GET  /api/seances/{id}/export/               → exporter en Excel
```

---

### `GET /api/planifications/aujourd-hui/`

Retourne l'emploi du temps du jour courant.

**Header requis**
```
Authorization: Bearer <token_enseignant>
```

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
      "module": "Algorithmique",
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

**Header requis**
```
Authorization: Bearer <token_enseignant>
```

**Body**
```json
{
  "planification_id": 4,
  "latitude_prof": 33.8935,
  "longitude_prof": -5.5473
}
```

**Réponse `201`**
```json
{
  "seance_id": 1,
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "expire_dans": 60
}
```

**Erreurs possibles**
```json
{ "error": "latitude_prof et longitude_prof obligatoires" }  // 400
{ "error": "Token manquant" }                                // 401 → utilisez /api/auth/token/refresh/
{ "error": "Accès réservé aux enseignants" }                 // 403
{ "error": "Planification introuvable" }                     // 404
{ "error": "Cette planification ne vous appartient pas" }    // 403
```

---

### `GET /api/qrcode/seance/{id}/`

Récupère le QR Code actuel d'une séance (se renouvelle automatiquement).

**Header requis**
```
Authorization: Bearer <token_enseignant>
```

**Réponse `200`**
```json
{
  "token": "nouveau-uuid-...",
  "seance_id": 1,
  "expire_dans": 45
}
```

---

### `POST /api/presences/scanner/`

Enregistre la présence d'un étudiant via le token QR Code. **Pas d'authentification requise (public).**

**Body**
```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "CIE": "M33333",
  "latitude_etudiant": 33.8935,
  "longitude_etudiant": -5.5474
}
```

**Réponse `200`**
```json
{
  "status": "success",
  "message": "Présence enregistrée pour Youssef Benali",
  "heure": "10:48:32"
}
```

**Erreurs possibles**

| Code | Message |
|------|---------|
| `400` | `token et CIE obligatoires` |
| `400` | `QR Code expiré` |
| `400` | `Présence déjà enregistrée` |
| `400` | `Présence déjà enregistrée depuis cet appareil` |
| `403` | `Vous êtes trop loin du QR Code (127m). Vous devez être dans la salle.` |
| `404` | `QR Code invalide` |
| `404` | `CIE introuvable` |

---

### `GET /api/seances/{id}/presences/`

Retourne la liste des présences enregistrées pour une séance.

**Header requis**
```
Authorization: Bearer <token_enseignant>
```

**Réponse `200`**
```json
{
  "seance_id": 3,
  "date": "2026-05-20",
  "planification": {
    "filiere": "SDIA",
    "module": "Algorithmique",
    "salle": "2.2",
    "heure_debut": "08:00:00",
    "heure_fin": "12:00:00"
  },
  "total_presents": 42,
  "presences": [
    {
      "nom": "Benali",
      "prenom": "Youssef",
      "CIE": "M33333",
      "heure_scan": "10:47:32",
      "date_scan": "2026-05-20",
      "ip_address": "192.168.1.100"
    }
  ]
}
```

---

### `GET /api/seances/{id}/export/`

> 🔒 Requiert un token enseignant.

Télécharge la feuille de présences au format Excel.

**Header requis**
```
Authorization: Bearer <token_enseignant>
```

**Réponse** : fichier `presences_seance_{id}_{date}.xlsx`

---

### `POST /api/etudiants/verifier/`

Vérifie l'existence d'un étudiant dans la base de données avant le scan.

**Body**
```json
{
  "CIE": "M33333"
}
```

**Réponse `200`**
```json
{
  "found": true,
  "message": "Étudiant trouvé : Youssef Benali",
  "etudiant": {
    "id": 1,
    "nom": "Benali",
    "prenom": "Youssef",
    "email": "youssef@gmail.com",
    "CIE": "M33333",
    "filiere": "SDIA"
  }
}
```

**Réponse `404` (étudiant non trouvé)**
```json
{
  "found": false,
  "message": "Étudiant introuvable dans le système",
  "recherche": {
    "CIE": "M33333",
    "email": null
  }
}
```

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
| `PUT` | `/api/enseignants/{id}/` | Modifier un enseignant (admin only) |
| `PATCH` | `/api/enseignants/{id}/` | Modifier partiellement (admin only) |
| `DELETE` | `/api/enseignants/{id}/` | Supprimer un enseignant (admin only) |

**POST body**
```json
{
  "nom_enseignant": "Benali",
  "prenom_enseignant": "Karim",
  "email_enseignant": "prof@fsmek.ma",
  "password_enseignant": "motdepasse123"
}
```

---

### Étudiants

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/etudiants/` | Liste tous les étudiants |
| `POST` | `/api/etudiants/` | Créer un étudiant |
| `PUT` | `/api/etudiants/{id}/` | Modifier un étudiant (admin only) |
| `PATCH` | `/api/etudiants/{id}/` | Modifier partiellement (admin only) |
| `DELETE` | `/api/etudiants/{id}/` | Supprimer un étudiant (admin only) |

**POST body**
```json
{
  "nom_etudiant": "Alaoui",
  "prenom_etudiant": "Sara",
  "email_etudiant": "sara@gmail.com",
  "password_etudiant": "motdepasse123",
  "CIE": "P123456",
  "filier_etudiant": 1
}
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
  "email_admin": "admin@fsmek.ma",
  "password_admin": "motdepasse123"
}
```

---

### Planifications

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/planifications/` | Liste toutes les planifications |
| `POST` | `/api/planifications/` | Créer une planification |
| `PUT` | `/api/planifications/{id}/` | Modifier une planification (admin only) |
| `PATCH` | `/api/planifications/{id}/` | Modifier partiellement (admin only) |
| `DELETE` | `/api/planifications/{id}/` | Supprimer une planification (admin only) |

**POST body**
```json
{
  "enseignant": 1,
  "salle": 1,
  "filiere": 1,
  "module": "Algorithmique",
  "jour": "vendredi",
  "heure_debut": "10:00:00",
  "heure_fin": "12:00:00"
}
```

---

### Mes Planifications (Enseignant)

Les enseignants peuvent créer et gérer leurs propres planifications.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/mes-planifications/` | Créer une planification personnelle |
| `PATCH` | `/api/mes-planifications/{id}/` | Modifier une de ses planifications |
| `DELETE` | `/api/mes-planifications/{id}/` | Supprimer une de ses planifications |

**POST body**
```json
{
  "salle": 2,
  "filiere": 3,
  "module": "Algorithmique",
  "jour": "samedi",
  "heure_debut": "14:00:00",
  "heure_fin": "16:00:00"
}
```

---

### Séances

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/seances/` | Liste toutes les séances |
| `DELETE` | `/api/seances/{id}/` | Supprimer une séance (enseignant only) |

---

### QR Codes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/qrcodes/` | Liste tous les QR Codes |

---

### Présences

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/presences/` | Liste toutes les présences |
| `DELETE` | `/api/presences/{id}/` | Supprimer une présence (enseignant only) |

---

## Profil utilisateur

### `GET /api/profile/`

Récupère le profil de l'utilisateur connecté.

**Header requis**
```
Authorization: Bearer <token>
```

**Réponse étudiant (200)**
```json
{
  "id": 1,
  "nom": "Benali",
  "prenom": "Youssef",
  "email": "youssef@gmail.com",
  "CIE": "M33333",
  "filiere": "SDIA",
  "photo_url": "https://res.cloudinary.com/.../etudiant_1.jpg",
  "role": "etudiant"
}
```

**Réponse enseignant (200)**
```json
{
  "id": 2,
  "nom": "Alami",
  "prenom": "Karim",
  "email": "karim@gmail.com",
  "photo_url": null,
  "role": "enseignant"
}
```

**Réponse admin (200)**
```json
{
  "id": 1,
  "nom": "Dupont",
  "prenom": "Admin",
  "email": "admin@gmail.com",
  "photo_url": null,
  "role": "admin"
}
```

---

### `PATCH /api/profile/` (Admin uniquement)

Modifie le profil de l'admin connecté.

**Header requis**
```
Authorization: Bearer <token_admin>
```

**Body** *(tous les champs optionnels)*
```json
{
  "nom_administrateur": "Nouveau Nom",
  "prenom_administrateur": "Nouveau Prénom",
  "email_administrateur": "nouveau@gmail.com"
}
```

**Réponse (200)**
```json
{
  "id": 1,
  "nom": "Nouveau Nom",
  "prenom": "Nouveau Prénom",
  "email": "nouveau@gmail.com",
  "photo_url": null,
  "role": "admin"
}
```

---

## Photo de profil

### `POST /api/profile/photo/`

Upload ou met à jour la photo de profil.

**Header requis**
```
Authorization: Bearer <token>
```

**Body** : `form-data` (pas JSON)

| Key | Type | Value |
|-----|------|-------|
| `photo` | File | image.jpg / .png / .webp |

**Réponse (200)**
```json
{
  "message": "Photo mise à jour",
  "photo_url": "https://res.cloudinary.com/.../etudiant_1.jpg"
}
```

**Erreurs**
```json
{ "error": "Token invalide" }                         // 401
{ "error": "Aucune image fournie" }                   // 400
{ "error": "Format non supporté (jpeg, png, webp)" }  // 400
{ "error": "Image trop lourde (max 2 MB)" }           // 400
{ "error": "Erreur Cloudinary : ..." }                // 500
```

---

### `DELETE /api/profile/photo/`

Supprime la photo de profil.

**Header requis**
```
Authorization: Bearer <token>
```

**Réponse (200)**
```json
{
  "message": "Photo supprimée"
}
```

---

## Emploi du temps étudiant

### `GET /api/etudiants/emploi-du-temps/`

Récupère l'emploi du temps (planifications) de l'étudiant connecté, basé sur sa filière.

**Accès :** Étudiant uniquement

**Header requis**
```
Authorization: Bearer <token_etudiant>
```

**Réponse (200)**
```json
{
  "filiere": "SDIA",
  "total": 4,
  "planifications": [
    {
      "id": 13,
      "jour": "lundi",
      "heure_debut": "10:30:00",
      "heure_fin": "12:30:00",
      "module": "Stage",
      "salle": "1.2",
      "enseignant": "Youssef Alami"
    },
    {
      "id": 14,
      "jour": "mercredi",
      "heure_debut": "08:30:00",
      "heure_fin": "12:30:00",
      "module": "Java",
      "salle": "1.1",
      "enseignant": "Mohammed Badaoui"
    }
  ]
}
```

---

## Troubleshooting

### ❌ Erreur 401 "Token invalide" ou "Token expiré"

**Solution :**
1. Votre access token a expiré (durée de vie: 1 jour)
2. Appelez `POST /api/auth/token/refresh/` avec votre refresh token
3. Utilisez le nouvel access token pour les prochaines requêtes

**Frontend:**
```javascript
// Implémentez un intercepteur HTTP
if (response.status === 401) {
  const newToken = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh: localStorage.getItem('refreshToken') })
  }).then(r => r.json());
  
  localStorage.setItem('accessToken', newToken.access);
  // Réessayez la requête avec le nouveau token
}
```

### ❌ Erreur 404 au lieu de 401

Si vous recevez une 404 à la place d'une 401, c'est que l'endpoint `/api/auth/token/refresh/` n'existe pas. **Assurez-vous que votre backend est à jour** avec le code qui inclut cet endpoint.

---

## Notes de sécurité

- 🔐 Ne stockez **jamais** les tokens en localStorage seul. Utilisez des cookies `httpOnly` si possible.
- 🔄 Implémentez toujours un système de refresh automatique côté frontend.
- 🚫 Les tokens refresh expirent après 7 jours. Au-delà, l'utilisateur doit se reconnecter.
- 📝 L'access token a une durée de vie de 1 jour.
