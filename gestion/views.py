from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import AccessToken as AT

from .models import (
    Filiere, Salle, Enseignant, Administrateur,
    Etudiant, Planification, SeanceQR, QRCode, Presence
)
from .serializers import (
    FiliereSerializer, SalleSerializer, EnseignantSerializer,
    AdministrateurSerializer, EtudiantSerializer, PlanificationSerializer,
    SeanceQRSerializer, QRCodeSerializer, PresenceSerializer
)

import jwt
from django.conf import settings
def get_role_from_request(request):
    
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token_str = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=['HS256'])
        return payload.get('role'), payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None, None
    except jwt.InvalidTokenError:
        return None, None
class FiliereViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer

class SalleViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer

class EnseignantViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = Enseignant.objects.all()
    serializer_class = EnseignantSerializer

    def update(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().destroy(request, *args, **kwargs)

class AdministrateurViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer

class EtudiantViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer

    def update(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().destroy(request, *args, **kwargs)

class PlanificationViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = Planification.objects.all()
    serializer_class = PlanificationSerializer

    def update(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        role, _ = get_role_from_request(request)
        if role != 'admin':
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
        return super().destroy(request, *args, **kwargs)

class SeanceQRViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = SeanceQR.objects.all()
    serializer_class = SeanceQRSerializer

    def destroy(self, request, *args, **kwargs):
        role, enseignant_id = get_role_from_request(request)
        if role != 'enseignant':
            return Response({'error': 'Réservé aux enseignants'}, status=403)

        seance = self.get_object()
        # Vérifier que la séance appartient bien à cet enseignant
        if seance.planification.enseignant.id != enseignant_id:
            return Response({'error': 'Accès non autorisé à cette séance'}, status=403)

        return super().destroy(request, *args, **kwargs)

class QRCodeViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer

class PresenceViewSet(viewsets.ModelViewSet):
    authentication_classes = []                   
    permission_classes = [AllowAny]
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer

    def destroy(self, request, *args, **kwargs):
        role, enseignant_id = get_role_from_request(request)
        if role != 'enseignant':
            return Response({'error': 'Réservé aux enseignants'}, status=403)

        presence = self.get_object()
        # Vérifier que la présence appartient à une séance de cet enseignant
        if presence.seance.planification.enseignant.id != enseignant_id:
            return Response({'error': 'Accès non autorisé à cette présence'}, status=403)

        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generer_seance_qr(request):
    planification_id = request.data.get('planification_id')
    latitude_prof    = request.data.get('latitude_prof')
    longitude_prof   = request.data.get('longitude_prof')

    if not latitude_prof or not longitude_prof:
        return Response({'error': 'latitude_prof et longitude_prof obligatoires'}, status=400)

    if not planification_id:
        return Response({'error': 'planification_id est requis'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        planification = Planification.objects.get(id=planification_id)
    except Planification.DoesNotExist:
        return Response({'error': 'Planification introuvable'}, status=status.HTTP_404_NOT_FOUND)

    auth_header = request.headers.get('Authorization', '')
    try:
        token = auth_header.split(' ')[1]
        decoded = AT(token)
        role = decoded.get('role')
        user_id = decoded.get('user_id')
    except Exception:
        return Response({'error': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

    if role != 'enseignant':
        return Response({'error': 'Accès réservé aux enseignants'}, status=status.HTTP_403_FORBIDDEN)

    try:
        enseignant = Enseignant.objects.get(id=user_id)
    except Enseignant.DoesNotExist:
        return Response({'error': 'Enseignant introuvable'}, status=status.HTTP_404_NOT_FOUND)

    if planification.enseignant != enseignant:
        return Response({'error': 'Cette planification ne vous appartient pas'}, status=status.HTTP_403_FORBIDDEN)

    seance = SeanceQR.objects.create(
        planification=planification,
        latitude_prof=latitude_prof,
        longitude_prof=longitude_prof,
    )
    qrcode = QRCode.objects.create(seance=seance)

    expire_dans = int((qrcode.cree_a + timedelta(minutes=qrcode.expiration) - timezone.now()).total_seconds())

    return Response({
        'seance_id': seance.id,
        'token': str(qrcode.token),
        'expire_dans': expire_dans
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_qrcode_seance(request, seance_id):
    # Décoder le token pour vérifier le rôle
    auth_header = request.headers.get('Authorization', '')
    try:
        token = auth_header.split(' ')[1]
        decoded = AT(token)
        role = decoded.get('role')
        user_id = decoded.get('user_id')
    except Exception:
        return Response({'error': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

    if role != 'enseignant':
        return Response({'error': 'Accès réservé aux enseignants'}, status=status.HTTP_403_FORBIDDEN)

    try:
        enseignant = Enseignant.objects.get(id=user_id)
    except Enseignant.DoesNotExist:
        return Response({'error': 'Enseignant introuvable'}, status=status.HTTP_404_NOT_FOUND)

    try:
        seance = SeanceQR.objects.get(id=seance_id)
    except SeanceQR.DoesNotExist:
        return Response({'error': 'Séance introuvable'}, status=status.HTTP_404_NOT_FOUND)

    # Vérifier que la séance appartient bien à cet enseignant
    if seance.planification.enseignant != enseignant:
        return Response({'error': 'Cette séance ne vous appartient pas'}, status=status.HTTP_403_FORBIDDEN)

    qrcode = QRCode.objects.filter(seance=seance).order_by('-cree_a').first()

    if not qrcode or not qrcode.is_valid():
        qrcode = QRCode.objects.create(seance=seance)

    expire_dans = int((qrcode.cree_a + timedelta(minutes=qrcode.expiration) - timezone.now()).total_seconds())

    return Response({
        'token': str(qrcode.token),
        'seance_id': seance.id,
        'expire_dans': max(expire_dans, 0)
    })


# Planifications du jour
JOURS_MAP = {
    0: 'lundi',
    1: 'mardi',
    2: 'mercredi',
    3: 'jeudi',
    4: 'vendredi',
    5: 'samedi',
    6: 'dimanche',
}

@api_view(['GET'])
@permission_classes([AllowAny]) 
def planifications_du_jour(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': 'Token manquant'}, status=status.HTTP_401_UNAUTHORIZED)

    token_str = auth_header.split(' ')[1]
    try:
        token = AT(token_str)
        role  = token.get('role')
    except Exception:
        return Response({'error': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

    if role != 'enseignant':
        return Response({'error': 'Accès réservé aux enseignants'}, status=status.HTTP_403_FORBIDDEN)

    user_id = token.get('user_id')
    try:
        enseignant = Enseignant.objects.get(id=user_id)
    except Enseignant.DoesNotExist:
        return Response({'error': 'Enseignant introuvable'}, status=status.HTTP_404_NOT_FOUND)

    jour_actuel = JOURS_MAP[timezone.now().weekday()]

    planifications = Planification.objects.filter(
        enseignant=enseignant,
        jour=jour_actuel
    ).select_related('salle', 'filiere')

    data = []
    for p in planifications:
        data.append({
            'id':          p.id,
            'salle':       str(p.salle),
            'filiere':     str(p.filiere),
            'module':      p.module,
            'heure_debut': str(p.heure_debut),
            'heure_fin':   str(p.heure_fin),
            'jour':        p.jour,
        })

    return Response({
        'jour':           jour_actuel,
        'date':           str(timezone.now().date()),
        'planifications': data,
        'total':          len(data),
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def verifier_etudiant(request):
    data = request.data

    cie    = data.get('CIE') or data.get('massar') or data.get('code_massar')
    email  = data.get('email') or data.get('email_etudiant')
    nom    = data.get('nom')   or data.get('nom_etudiant')
    prenom = data.get('prenom') or data.get('prenom_etudiant')

    if not cie and not email:
        return Response(
            {'error': 'CIE (Massar) ou email obligatoire pour la vérification'},
            status=400
        )

    etudiant = None

    # recherche par CIE (Massar)
    if cie:
        try:
            etudiant = Etudiant.objects.get(CIE=cie)
        except Etudiant.DoesNotExist:
            pass

    # recherche par email si CIE non trouvé
    if not etudiant and email:
        try:
            etudiant = Etudiant.objects.get(email_etudiant=email)
        except Etudiant.DoesNotExist:
            pass

    if not etudiant:
        return Response({
            'found': False,
            'message': 'Étudiant introuvable dans le système',
            'recherche': {
                'CIE': cie,
                'email': email,
                'nom': nom,
                'prenom': prenom,
            }
        }, status=404)

    # Étudiant trouvé → retourner ses données
    return Response({
        'found': True,
        'message': f'Étudiant trouvé : {etudiant.prenom_etudiant} {etudiant.nom_etudiant}',
        'etudiant': {
            'id':       etudiant.id,
            'nom':      etudiant.nom_etudiant,
            'prenom':   etudiant.prenom_etudiant,
            'email':    etudiant.email_etudiant,
            'CIE':      etudiant.CIE,
            'filiere':  etudiant.filier_etudiant.nom_filiere if etudiant.filier_etudiant else None,
        }
    }, status=200)

@api_view(['GET'])
def liste_presences_seance(request, seance_id):
    
    import jwt
    from django.conf import settings

    # Vérifier le token JWT et extraire le rôle
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': 'Token manquant'}, status=401)

    token_str = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Token expiré'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'error': 'Token invalide'}, status=401)

    if payload.get('role') != 'enseignant':
        return Response({'error': 'Accès réservé aux enseignants'}, status=403)

    enseignant_id = payload.get('user_id')

    # Récupérer la séance
    try:
        seance = SeanceQR.objects.get(id=seance_id)
    except SeanceQR.DoesNotExist:
        return Response({'error': 'Séance introuvable'}, status=404)

    # Vérifier que la planification appartient bien à cet enseignant
    if seance.planification.enseignant.id != enseignant_id:
        return Response({'error': 'Accès non autorisé à cette séance'}, status=403)

    # Récupérer toutes les présences de cette séance
    presences = Presence.objects.filter(seance=seance).select_related('etudiant')

    data = {
        "seance_id": seance.id,
        "date": str(seance.date),
        "planification": {
            "filiere": seance.planification.filiere.nom_filiere,
            "module": seance.planification.module,
            "salle": seance.planification.salle.nom_salle,
            "heure_debut": str(seance.planification.heure_debut),
            "heure_fin": str(seance.planification.heure_fin),
        },
        "total_presents": presences.count(),
        "presences": [
            {
                "nom": p.etudiant.nom_etudiant,
                "prenom": p.etudiant.prenom_etudiant,
                "CIE": p.etudiant.CIE,
                "heure_scan": str(p.heure_scan),
                "date_scan": str(p.date_scan),
                "ip_address": p.ip_address,
            }
            for p in presences
        ]
    }

    return Response(data, status=200)


import jwt
import openpyxl
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_seance_excel(request, seance_id):

    # Décoder le token JWT
    try:
        raw_token     = request.headers.get('Authorization', '').split(' ')[1]
        payload       = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=['HS256'])
        enseignant_id = payload.get('user_id')
        role          = payload.get('role')
    except Exception:
        return Response({'error': 'Token invalide'}, status=401)

    if role != 'enseignant':
        return Response({'error': 'Accès réservé aux enseignants'}, status=403)

    # Récupérer la séance
    try:
        seance = SeanceQR.objects.select_related(
            'planification__enseignant',
            'planification__filiere',
            'planification__salle'
        ).get(id=seance_id)
    except SeanceQR.DoesNotExist:
        return Response({'error': 'Séance introuvable'}, status=404)

    # Vérifier que la séance appartient à cet enseignant
    if seance.planification.enseignant.id != enseignant_id:
        return Response({'error': 'Accès non autorisé à cette séance'}, status=403)

    # Récupérer tous les étudiants de la filière
    filiere        = seance.planification.filiere
    tous_etudiants = Etudiant.objects.filter(
        filier_etudiant=filiere
    ).order_by('nom_etudiant', 'prenom_etudiant')

    # Récupérer les CIE des étudiants présents
    presents_cie = set(
        Presence.objects.filter(seance=seance)
        .values_list('etudiant__CIE', flat=True)
    )

    # Construire le fichier Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Séance {seance_id}"

    # Styles
    from openpyxl.styles import Font, PatternFill, Alignment

    style_titre  = Font(bold=True, size=12)
    fill_present = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  
    fill_absent  = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  
    fill_header  = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")  
    bold         = Font(bold=True)

    # Infos séance
    ws.append(['Filière',   filiere.nom_filiere])
    ws.append(['Module',    seance.planification.module])
    ws.append(['Salle',     str(seance.planification.salle)])
    ws.append(['Date',      str(seance.date)])
    ws.append(['Semestre',  seance.planification.filiere.semester_filiere])
    ws.append([])  

    for row in ws.iter_rows(min_row=1, max_row=4):
        row[0].font = style_titre

    # En-têtes colonnes
    header_row = ["N°", "Nom", "Prénom", "CIE", "Filière", "Présence"]
    ws.append(header_row)

    header_excel_row = ws.max_row
    for cell in ws[header_excel_row]:
        cell.font      = bold
        cell.fill      = fill_header
        cell.alignment = Alignment(horizontal='center')

    # Données : tous les étudiants
    for i, etudiant in enumerate(tous_etudiants, start=1):
        est_present = etudiant.CIE in presents_cie
        statut      = 'Présent' if est_present else 'Absent'

        ws.append([
            i,
            etudiant.nom_etudiant,
            etudiant.prenom_etudiant,
            etudiant.CIE,
            str(etudiant.filier_etudiant),
            statut,
        ])

        # Colorier la cellule Présence
        statut_cell      = ws.cell(row=ws.max_row, column=6)
        statut_cell.fill = fill_present if est_present else fill_absent
        statut_cell.alignment = Alignment(horizontal='center')

    # Ajuster largeur colonnes
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 15

    # 7. Retourner la réponse HTTP
    filename = f"presences_seance_{seance_id}_{seance.date}.xlsx"
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

from django.utils import timezone

@api_view(['POST'])
@permission_classes([AllowAny])
def scanner_presence(request):
    token_uuid = request.data.get('token')
    cie        = request.data.get('CIE')

    if not all([token_uuid, cie]):
        return Response({'error': 'token et CIE obligatoires'}, status=400)
    
    # Récupérer @IP 
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    # Récupérer le QRCode
    try:
        qrcode = QRCode.objects.get(token=token_uuid)
    except QRCode.DoesNotExist:
        return Response({'error': 'QR Code invalide'}, status=404)

    # Vérifier validité
    if not qrcode.is_valid():
        return Response({'error': 'QR Code expiré'}, status=400)

    seance = qrcode.seance

    # @IP déjà scanné ou nn
    if Presence.objects.filter(seance=seance, ip_address=ip).exists():
        return Response({'error': 'Ce téléphone a déjà été utilisé pour cette séance'}, status=400)

    # Récupérer l'étudiant via CIE
    try:
        etudiant = Etudiant.objects.get(CIE=cie)
    except Etudiant.DoesNotExist:
        return Response({'error': 'CIE introuvable'}, status=404)

    # Anti-doublon
    if Presence.objects.filter(etudiant=etudiant, seance=seance).exists():
        return Response({'error': 'Présence déjà enregistrée'}, status=400)

    # Enregistrer la présence
    now = timezone.now()
    Presence.objects.create(
        etudiant=etudiant,
        seance=seance,
        date_scan=now.date(),
        heure_scan=now.time(),
        ip_address=ip,
    )

    return Response({
        'status': 'success',
        'message': f'Présence enregistrée pour {etudiant.prenom_etudiant} {etudiant.nom_etudiant}',
        'heure': str(now.time())[:8],
    })


import cloudinary.uploader

@api_view(['POST', 'DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def update_profile_photo(request):
    role, user_id = get_role_from_request(request)
    if not role or not user_id:
        return Response({'error': 'Token invalide'}, status=401)

    # objet selon le rôle
    try:
        if role == 'etudiant':
            user = Etudiant.objects.get(id=user_id)
        elif role == 'enseignant':
            user = Enseignant.objects.get(id=user_id)
        elif role in ['admin', 'admin_enseignant']:
            user = Administrateur.objects.get(id=user_id)
        else:
            return Response({'error': 'Rôle inconnu'}, status=400)
    except Exception:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    if request.method == 'DELETE':
        # Supprimer sur Cloudinary si public_id connu
        user.photo_url = None
        user.save()
        return Response({'message': 'Photo supprimée'}, status=200)

    # upload
    photo = request.FILES.get('photo')
    if not photo:
        return Response({'error': 'Aucune image fournie'}, status=400)

    # Validation type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if photo.content_type not in allowed_types:
        return Response({'error': 'Format non supporté (jpeg, png, webp)'}, status=status.HTTP_400_BAD_REQUEST)

    # Validation taille (max 2 MB)
    if photo.size > 2 * 1024 * 1024:
        return Response({'error': 'Image (max 2 MB)'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = cloudinary.uploader.upload(
            photo,
            folder=f'presenceqr/profiles/{role}s/',
            public_id=f'{role}_{user_id}',  # écrase l'ancienne photo automatiquement
            overwrite=True,
            transformation=[
                {'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'},
            ]
        )
        url = result['secure_url']
        user.photo_url = url
        user.save()
        return Response({'message': 'Photo mise à jour', 'photo_url': url}, status=200)
    except Exception as e:
        return Response({'error': f'Erreur Cloudinary : {str(e)}'}, status=500)

@api_view(['GET', 'PATCH'])
@authentication_classes([])
@permission_classes([AllowAny])
def my_profile(request):
    role, user_id = get_role_from_request(request)
    if not role or not user_id:
        return Response({'error': 'Token invalide'}, status=401)

    try:
        if role == 'etudiant':
            # only get
            if request.method == 'PATCH':
                return Response({'error': 'Modification non autorisée'}, status=403)
            user = Etudiant.objects.get(id=user_id)
            return Response({
                'id': user.id,
                'nom': user.nom_etudiant,
                'prenom': user.prenom_etudiant,
                'email': user.email_etudiant,
                'CIE': user.CIE,
                'filiere': user.filier_etudiant,
                'photo_url': user.photo_url,
                'role': 'etudiant',
            })

        elif role == 'enseignant':
            # only GET 
            if request.method == 'PATCH':
                return Response({'error': 'Modification non autorisée'}, status=403)
            user = Enseignant.objects.get(id=user_id)
            return Response({
                'id': user.id,
                'nom': user.nom_enseignant,
                'prenom': user.prenom_enseignant,
                'email': user.email_enseignant,
                'photo_url': user.photo_url,
                'role': 'enseignant',
            })

        elif role in ['admin', 'admin_enseignant']:
            user = Administrateur.objects.get(id=user_id)
            # PATCH + get
            if request.method == 'PATCH':
                for field in ['nom_administrateur', 'prenom_administrateur', 'email_administrateur']:
                    if field in request.data:
                        setattr(user, field, request.data[field])
                user.save()
            return Response({
                'id': user.id,
                'nom': user.nom_administrateur,
                'prenom': user.prenom_administrateur,
                'email': user.email_administrateur,
                'photo_url': user.photo_url,
                'role': role,
            })

    except Exception:
        return Response({'error': 'Utilisateur introuvable'}, status=404)


import math

def calculer_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # rayon Terre en mètres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def scanner_presence(request):
    token_uuid        = request.data.get('token')
    cie               = request.data.get('CIE')
    latitude_etudiant = request.data.get('latitude_etudiant')
    longitude_etudiant= request.data.get('longitude_etudiant')

    if not all([token_uuid, cie, latitude_etudiant, longitude_etudiant]):
        return Response({'error': 'token, CIE, latitude_etudiant et longitude_etudiant obligatoires'}, status=400)

    try:
        qrcode = QRCode.objects.get(token=token_uuid)
    except QRCode.DoesNotExist:
        return Response({'error': 'QR Code invalide'}, status=404)

    if not qrcode.is_valid():
        return Response({'error': 'QR Code expiré'}, status=400)

    seance = qrcode.seance
    if seance.latitude_prof and seance.longitude_prof:
        distance = calculer_distance(
            seance.latitude_prof, seance.longitude_prof,
            float(latitude_etudiant), float(longitude_etudiant)
        )
        if distance > 50:  # 50 metre
            return Response({
                'error': f'Vous êtes trop loin du QR Code ({int(distance)}m). Vous devez être dans la salle.'
            }, status=403)

    try:
        etudiant = Etudiant.objects.get(CIE=cie)
    except Etudiant.DoesNotExist:
        return Response({'error': 'CIE introuvable'}, status=404)

    if Presence.objects.filter(etudiant=etudiant, seance=seance).exists():
        return Response({'error': 'Présence déjà enregistrée'}, status=400)

    # Anti-fraud IP existant
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() \
        or request.META.get('REMOTE_ADDR')
    if Presence.objects.filter(seance=seance, ip_address=ip).exists():
        return Response({'error': 'Présence déjà enregistrée depuis cet appareil'}, status=400)

    now = timezone.now()
    Presence.objects.create(
        etudiant=etudiant,
        seance=seance,
        date_scan=now.date(),
        heure_scan=now.time(),
        ip_address=ip,
    )

    return Response({
        'status': 'success',
        'message': f'Présence enregistrée pour {etudiant.prenom_etudiant} {etudiant.nom_etudiant}',
        'heure': str(now.time())[:8],
    }, status=200)

@api_view(['POST'])
def mes_planifications(request):

    role, enseignant_id = get_role_from_request(request)
    if role not in ('enseignant', 'admin_enseignant'):
        return Response({'error': 'Réservé aux enseignants'}, status=403)

    data = request.data.copy()
    data['enseignant'] = enseignant_id  # forcé — ne peut pas usurper un autre prof

    serializer = PlanificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PATCH', 'DELETE'])
def mes_planifications_detail(request, planification_id):

    role, enseignant_id = get_role_from_request(request)
    if role not in ('enseignant', 'admin_enseignant'):
        return Response({'error': 'Réservé aux enseignants'}, status=403)

    try:
        planification = Planification.objects.get(id=planification_id)
    except Planification.DoesNotExist:
        return Response({'error': 'Planification introuvable'}, status=404)

    if planification.enseignant.id != enseignant_id:
        return Response({'error': 'Accès non autorisé à cette planification'}, status=403)

    if request.method == 'DELETE':
        planification.delete()
        return Response({'message': 'Planification supprimée'}, status=200)

    if request.method == 'PATCH':
        data = request.data.copy()
        data.pop('enseignant', None)  # l'enseignant ne peut pas changer le propriétaire

        serializer = PlanificationSerializer(planification, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return HttpResponse("Render works!")