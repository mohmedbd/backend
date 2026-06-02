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

class FiliereViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer

class SalleViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer

class EnseignantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Enseignant.objects.all()
    serializer_class = EnseignantSerializer

class AdministrateurViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer

class EtudiantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer

class PlanificationViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Planification.objects.all()
    serializer_class = PlanificationSerializer

class SeanceQRViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = SeanceQR.objects.all()
    serializer_class = SeanceQRSerializer

class QRCodeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer

class PresenceViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generer_seance_qr(request):
    planification_id = request.data.get('planification_id')

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

    seance = SeanceQR.objects.create(planification=planification)
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
    ws.append(['Salle',     str(seance.planification.salle)])
    ws.append(['Date',      str(seance.date)])
    ws.append(['Semestre',  seance.planification.semestre])
    ws.append([])  

    for row in ws.iter_rows(min_row=1, max_row=4):
        row[0].font = style_titre

    # En-têtes colonnes
    header_row = ['N°', 'Nom', 'Prénom', 'CIE', 'Présence']
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
            statut,
        ])

        # Colorier la cellule Présence
        statut_cell      = ws.cell(row=ws.max_row, column=5)
        statut_cell.fill = fill_present if est_present else fill_absent
        statut_cell.alignment = Alignment(horizontal='center')

    # Ajuster largeur colonnes
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 12

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
    nom        = request.data.get('nom')
    prenom     = request.data.get('prenom')

    if not all([token_uuid, cie]):
        return Response({'error': 'token et CIE obligatoires'}, status=400)

    # Récupérer le QRCode
    try:
        qrcode = QRCode.objects.get(token=token_uuid)
    except QRCode.DoesNotExist:
        return Response({'error': 'QR Code invalide'}, status=404)

    # Vérifier validité
    if not qrcode.is_valid():
        return Response({'error': 'QR Code expiré'}, status=400)

    # Récupérer l'étudiant via CIE
    try:
        etudiant = Etudiant.objects.get(CIE=cie)
    except Etudiant.DoesNotExist:
        return Response({'error': 'CIE introuvable'}, status=404)

    # Anti-doublon
    seance = qrcode.seance
    if Presence.objects.filter(etudiant=etudiant, seance=seance).exists():
        return Response({'error': 'Présence déjà enregistrée'}, status=400)

    # Enregistrer la présence
    now = timezone.now()
    Presence.objects.create(
        etudiant=etudiant,
        seance=seance,
        date_scan=now.date(),
        heure_scan=now.time(),
    )

    return Response({
        'status': 'success',
        'message': f'Présence enregistrée pour {etudiant.prenom_etudiant} {etudiant.nom_etudiant}',
        'heure': str(now.time())[:8],
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return HttpResponse("Render works!")
