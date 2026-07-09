from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import jwt
from django.conf import settings
from datetime import datetime, timedelta, timezone

from .models import (
    User, RoleConfig, UserRoleAssignment, Role,
    AdminProfile, ProfessorProfile, HeadOfDepartmentProfile,
    ProgramManagerProfile, StudentProfile, validate_role_combination,
)
from gestion.models import Filiere


def get_tokens_for_user(user):
    refresh = RefreshToken()
    refresh['user_id'] = user.id
    refresh['roles'] = user.get_active_roles()
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def get_user_profile_data(user):
    data = {
        'id': user.id,
        'email': user.email,
        'nom': user.last_name,
        'prenom': user.first_name,
        'phone': user.phone,
        'roles': user.get_active_roles(),
        'photo_url': getattr(user, 'photo_url', None),
    }

    if user.has_role(Role.STUDENT):
        profile = getattr(user, 'student_profile', None)
        if profile:
            data.update({
                'CIE': profile.CIE,
                'filiere': str(profile.program) if profile.program else None,
                'filiere_id': profile.program.id if profile.program else None,
            })

    if user.has_role(Role.PROFESSOR):
        profile = getattr(user, 'professor_profile', None)
        if profile:
            data.update({
                'specialization': profile.specialization,
            })

    if user.has_role(Role.HEAD_OF_DEPARTMENT):
        profile = getattr(user, 'hod_profile', None)
        if profile:
            data['department'] = profile.department.nom_departement if profile.department else ''

    if user.has_role(Role.PROGRAM_MANAGER):
        profile = getattr(user, 'program_manager_profile', None)
        if profile:
            data['program'] = profile.program_name

    return data


def create_role_assignments(user, role_codenames):
    for codename in role_codenames:
        role_config, _ = RoleConfig.objects.get_or_create(
            codename=codename,
            defaults={'display_name': dict(Role.choices).get(codename, codename)}
        )
        UserRoleAssignment.objects.create(user=user, role=role_config)


def create_profile_for_role(user, role, extra_data=None):
    extra_data = extra_data or {}
    if role == Role.ADMIN:
        AdminProfile.objects.get_or_create(user=user)
    elif role == Role.PROFESSOR:
        ProfessorProfile.objects.get_or_create(
            user=user,
            defaults={'specialization': extra_data.get('specialization', '')}
        )
    elif role == Role.HEAD_OF_DEPARTMENT:
        HeadOfDepartmentProfile.objects.get_or_create(
            user=user,
            defaults={
                'department_id': extra_data.get('department_id'),
            }
        )
    elif role == Role.PROGRAM_MANAGER:
        ProgramManagerProfile.objects.get_or_create(
            user=user,
            defaults={
                'program_name': extra_data.get('program_name', ''),
                'program_id': extra_data.get('program_id'),
            }
        )
    elif role == Role.STUDENT:
        StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'CIE': extra_data.get('CIE', ''),
                'program_id': extra_data.get('program_id'),
            }
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'status': 'error', 'message': 'Email et mot de passe obligatoires'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, email=email, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)
        return Response({
            'status': 'success',
            'tokens': tokens,
            'user': get_user_profile_data(user),
        })

    return Response(
        {'status': 'error', 'message': 'Email ou mot de passe incorrect'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response(
            {'status': 'error', 'message': 'Token manquant'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        token = auth_header.split(' ')[1]
        decoded = AccessToken(token)
        admin_roles = decoded.get('roles', [])
        if not isinstance(admin_roles, list):
            admin_roles = [admin_roles]
        if Role.ADMIN not in admin_roles:
            return Response(
                {'status': 'error', 'message': 'Accès réservé à l\'administrateur'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Exception:
        return Response(
            {'status': 'error', 'message': 'Token invalide'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    role = request.data.get('role')
    email = request.data.get('email')
    password = request.data.get('password')
    nom = request.data.get('nom', '')
    prenom = request.data.get('prenom', '')

    if not all([role, email, password]):
        return Response(
            {'status': 'error', 'message': 'role, email et password obligatoires'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if role not in dict(Role.choices):
        return Response(
            {'status': 'error', 'message': f'Rôle invalide. Choisissez parmi: {", ".join(dict(Role.choices).keys())}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'status': 'error', 'message': 'Email déjà utilisé'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_role_combination([role])
    except ValidationError as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=prenom,
        last_name=nom,
    )

    create_role_assignments(user, [role])

    extra = {}
    if role == Role.STUDENT:
        cie = request.data.get('CIE') or request.data.get('code_massar')
        program_id = request.data.get('program_id') or request.data.get('filiere_id')
        if not cie:
            user.delete()
            return Response(
                {'status': 'error', 'message': 'CIE (Code Massar) obligatoire pour un étudiant'},
                status=400
            )
        extra['CIE'] = cie
        extra['program_id'] = program_id
    elif role == Role.PROFESSOR:
        extra['specialization'] = request.data.get('specialization', '')
    elif role == Role.HEAD_OF_DEPARTMENT:
        extra['department_id'] = request.data.get('department_id')
    elif role == Role.PROGRAM_MANAGER:
        extra['program_name'] = request.data.get('program_name', '')

    create_profile_for_role(user, role, extra)

    tokens = get_tokens_for_user(user)
    return Response({
        'status': 'success',
        'message': f'{dict(Role.choices)[role]} créé avec succès',
        'tokens': tokens,
        'user': get_user_profile_data(user),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    refresh_token = request.data.get('refresh')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token manquant'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    except Exception:
        return Response(
            {'error': 'Token invalide ou expiré'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
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

    roles = payload.get('roles', [])
    if not isinstance(roles, list):
        roles = [roles]

    role_voulu = request.data.get('role_voulu')
    if role_voulu not in roles:
        return Response(
            {'error': f'Vous n\'avez pas le rôle "{role_voulu}". Rôles disponibles: {roles}'},
            status=403
        )

    user_id = payload.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    new_payload = {
        'token_type': 'access',
        'user_id': user_id,
        'roles': roles,
        'active_role': role_voulu,
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
    }
    access_token = jwt.encode(new_payload, settings.SECRET_KEY, algorithm='HS256')

    return Response({
        'active_role': role_voulu,
        'access': access_token,
        'user': get_user_profile_data(user),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def assign_role(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'error': 'Token manquant'}, status=401)

    try:
        token = auth_header.split(' ')[1]
        decoded = AccessToken(token)
        admin_roles = decoded.get('roles', [])
        if not isinstance(admin_roles, list):
            admin_roles = [admin_roles]
        if Role.ADMIN not in admin_roles:
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
    except Exception:
        return Response({'error': 'Token invalide'}, status=401)

    user_id = request.data.get('user_id')
    new_role = request.data.get('role')
    extra_data = request.data.get('extra_data', {})

    if not user_id or not new_role:
        return Response({'error': 'user_id et role obligatoires'}, status=400)

    if new_role not in dict(Role.choices):
        return Response({'error': f'Rôle invalide'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    existing_roles = user.get_active_roles()
    new_roles = list(set(existing_roles + [new_role]))

    try:
        validate_role_combination(new_roles)
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)

    create_role_assignments(user, [new_role])
    create_profile_for_role(user, new_role, extra_data)

    tokens = get_tokens_for_user(user)
    return Response({
        'status': 'success',
        'message': f'Rôle "{new_role}" assigné à {user.email}',
        'tokens': tokens,
        'user': get_user_profile_data(user),
    })


@api_view(['DELETE'])
@permission_classes([AllowAny])
def remove_role(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'error': 'Token manquant'}, status=401)

    try:
        token = auth_header.split(' ')[1]
        decoded = AccessToken(token)
        admin_roles = decoded.get('roles', [])
        if not isinstance(admin_roles, list):
            admin_roles = [admin_roles]
        if Role.ADMIN not in admin_roles:
            return Response({'error': 'Réservé aux administrateurs'}, status=403)
    except Exception:
        return Response({'error': 'Token invalide'}, status=401)

    user_id = request.data.get('user_id')
    role_to_remove = request.data.get('role')

    if not user_id or not role_to_remove:
        return Response({'error': 'user_id et role obligatoires'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    UserRoleAssignment.objects.filter(
        user=user,
        role__codename=role_to_remove,
        is_active=True
    ).update(is_active=False)

    return Response({
        'status': 'success',
        'message': f'Rôle "{role_to_remove}" retiré de {user.email}',
        'user': get_user_profile_data(user),
    })
