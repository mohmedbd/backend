from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
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