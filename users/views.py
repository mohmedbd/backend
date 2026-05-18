from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken , AccessToken
from gestion.models import Administrateur, Etudiant, Enseignant


def get_tokens_for_user(user_id, role):
    refresh = RefreshToken()
    refresh['user_id'] = user_id
    refresh['role'] = role
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'status': 'error', 'message': 'Email et password obligatoires'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Administrateur
    admin = Administrateur.objects.filter(email_admin=email, password_admin=password).first()
    if admin:
        tokens = get_tokens_for_user(admin.id, 'admin')
        return Response({
            'status': 'success',
            'role': 'admin',
            'tokens': tokens,
            'user': {
                'id': admin.id,
                'email': admin.email_admin,
                'nom': admin.nom_admin,
                'prenom': admin.prenom_admin,
            }
        })

    # Etudiant
    etudiant = Etudiant.objects.filter(email_etudiant=email, password_etudiant=password).first()
    if etudiant:
        tokens = get_tokens_for_user(etudiant.id, 'etudiant')
        return Response({
            'status': 'success',
            'role': 'etudiant',
            'tokens': tokens,
            'user': {
                'id': etudiant.id,
                'email': etudiant.email_etudiant,
                'nom': etudiant.nom_etudiant,
                'prenom': etudiant.prenom_etudiant,
            }
        })

    # Enseignant
    enseignant = Enseignant.objects.filter(email_enseignant=email, password_enseignant=password).first()
    if enseignant:
        tokens = get_tokens_for_user(enseignant.id, 'enseignant')
        return Response({
            'status': 'success',
            'role': 'enseignant',
            'tokens': tokens,
            'user': {
                'id': enseignant.id,
                'email': enseignant.email_enseignant,
                'nom': enseignant.nom_enseignant,
                'prenom': enseignant.prenom_enseignant,
            }
        })

    # Aucun utilisateur trouve
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
            return Response({'status': 'error', 'message': 'CIE et filier_etudiant obligatoires'}, status=status.HTTP_400_BAD_REQUEST)
        if Etudiant.objects.filter(email_etudiant=email).exists():
            return Response({'status': 'error', 'message': 'Email déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
        Etudiant.objects.create(nom_etudiant=nom, prenom_etudiant=prenom, email_etudiant=email, password_etudiant=password, filier_etudiant=filier, CIE=CIE)

    elif role == 'enseignant':
        if Enseignant.objects.filter(email_enseignant=email).exists():
            return Response({'status': 'error', 'message': 'Email déjà utilisé'}, status=status.HTTP_400_BAD_REQUEST)
        Enseignant.objects.create(nom_enseignant=nom, prenom_enseignant=prenom, email_enseignant=email, password_enseignant=password)

    else:
        return Response({'status': 'error', 'message': 'Role invalide (etudiant ou enseignant)'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'success', 'message': f'{role} créé avec succès'}, status=status.HTTP_201_CREATED)