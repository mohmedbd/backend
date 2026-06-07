from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken , AccessToken
from gestion.models import Administrateur, Etudiant, Enseignant, Filiere
from rest_framework.decorators import  permission_classes 
from rest_framework.permissions import AllowAny                     


def get_tokens_for_user(user_id, role):
    refresh = RefreshToken()
    refresh['user_id'] = user_id
    refresh['role'] = role
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_tokens_for_user_double(admin_id, enseignant_id):
    refresh = RefreshToken()
    refresh['role']          = 'admin_enseignant'
    refresh['admin_id']      = admin_id
    refresh['enseignant_id'] = enseignant_id
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email    = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'status': 'error', 'message': 'Email et password obligatoires'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Chercher dans toutes les tables
    admin      = Administrateur.objects.filter(email_admin=email, password_admin=password).first()
    enseignant = Enseignant.objects.filter(email_enseignant=email, password_enseignant=password).first()
    etudiant   = Etudiant.objects.filter(email_etudiant=email, password_etudiant=password).first()

    # admin & enseignant
    if admin and enseignant:
        tokens = get_tokens_for_user_double(admin.id, enseignant.id)
        return Response({
            'status': 'success',
            'role': 'admin_enseignant',
            'tokens': tokens,
            'user': {
                'admin_id':      admin.id,
                'enseignant_id': enseignant.id,
                'email':         email,
                'nom':           admin.nom_admin,
                'prenom':        admin.prenom_admin,
            }
        })

    # admin
    if admin:
        tokens = get_tokens_for_user(admin.id, 'admin')
        return Response({
            'status': 'success',
            'role': 'admin',
            'tokens': tokens,
            'user': {
                'id':     admin.id,
                'email':  admin.email_admin,
                'nom':    admin.nom_admin,
                'prenom': admin.prenom_admin,
            }
        })

    # enseignant 
    if enseignant:
        tokens = get_tokens_for_user(enseignant.id, 'enseignant')
        return Response({
            'status': 'success',
            'role': 'enseignant',
            'tokens': tokens,
            'user': {
                'id':     enseignant.id,
                'email':  enseignant.email_enseignant,
                'nom':    enseignant.nom_enseignant,
                'prenom': enseignant.prenom_enseignant,
            }
        })

    # etudiant 
    if etudiant:
        tokens = get_tokens_for_user(etudiant.id, 'etudiant')
        return Response({
            'status': 'success',
            'role': 'etudiant',
            'tokens': tokens,
            'user': {
                'id':     etudiant.id,
                'email':  etudiant.email_etudiant,
                'nom':    etudiant.nom_etudiant,
                'prenom': etudiant.prenom_etudiant,
            }
        })

    return Response(
        {'status': 'error', 'message': 'Email ou password incorrect'},
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
def register(request):
    # Vérifier le token JWT et le rôle admin
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'status': 'error', 'message': 'Token manquant'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        token = auth_header.split(' ')[1]
        decoded = AccessToken(token)
        if decoded.get('role') != 'admin':
            return Response({'status': 'error', 'message': 'Accès réservé à l\'admin'}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({'status': 'error', 'message': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

    role = request.data.get('role')
    nom = request.data.get('nom')
    prenom = request.data.get('prenom')
    email = request.data.get('email')
    password = request.data.get('password')

    if not all([role, nom, prenom, email, password]):
        return Response({'status': 'error', 'message': 'Tous les champs sont obligatoires'}, status=status.HTTP_400_BAD_REQUEST)

    if role == 'etudiant':
        CIE = request.data.get('CIE')
        filier = request.data.get('filier_etudiant')
        if not CIE or not filier:
            return Response({'status': 'error', 'message': 'CIE et filier_etudiant obligatoires'}, status=400)

        try:
            filiere_obj = Filiere.objects.get(id=filier)
        except Filiere.DoesNotExist:
            return Response({'status': 'error', 'message': 'Filière introuvable'}, status=400)

        Etudiant.objects.create(
            nom_etudiant=nom,
            prenom_etudiant=prenom,
            email_etudiant=email,
            password_etudiant=password,
            filier_etudiant=filiere_obj,
            CIE=CIE
        )

    elif role == 'enseignant':
        if Enseignant.objects.filter(email_enseignant=email).exists():
            return Response({'status': 'error', 'message': 'Email déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
        Enseignant.objects.create(nom_enseignant=nom, prenom_enseignant=prenom, email_enseignant=email, password_enseignant=password)

    else:
        return Response({'status': 'error', 'message': 'Role invalide (etudiant ou enseignant)'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'success', 'message': f'{role} créé avec succès'}, status=status.HTTP_201_CREATED)

import jwt
from django.conf import settings
@api_view(['POST'])
@permission_classes([AllowAny])
def switch_role(request):
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

    if payload.get('role') != 'admin_enseignant':
        return Response({'error': 'Réservé aux comptes double-rôle'}, status=403)

    role_voulu = request.data.get('role_voulu')
    if role_voulu not in ['admin', 'enseignant']:
        return Response({'error': 'role_voulu doit être admin ou enseignant'}, status=400)

    # Générer un token "pur" avec le rôle choisi
    user_id = payload.get('enseignant_id') if role_voulu == 'enseignant' else payload.get('admin_id')

    new_token = RefreshToken()
    new_token['role']    = role_voulu
    new_token['user_id'] = user_id

    return Response({
        'role_actif': role_voulu,
        'access': str(new_token.access_token),
    })
