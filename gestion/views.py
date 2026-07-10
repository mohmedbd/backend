from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import AccessToken as AT

from .models import Departement, Filiere, Salle, Planification, SeanceQR, QRCode, Presence
from .serializers import (
    DepartementSerializer, FiliereSerializer, SalleSerializer,
    PlanificationSerializer, SeanceQRSerializer,
    QRCodeSerializer, PresenceSerializer,
    StudentUserSerializer, ProfessorUserSerializer,
    HeadOfDepartmentUserSerializer, ProgramManagerUserSerializer,
)
from users.models import (
    User, RoleConfig, UserRoleAssignment, Role,
    AdminProfile, ProfessorProfile, StudentProfile,
    HeadOfDepartmentProfile, ProgramManagerProfile,
)

import jwt
from django.conf import settings


def get_role_from_request(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, None
    token_str = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=['HS256'])
        roles = payload.get('roles', [])
        if isinstance(roles, str):
            roles = [roles]
        user_id = payload.get('user_id')
        return roles, user_id
    except jwt.ExpiredSignatureError:
        return None, None
    except jwt.InvalidTokenError:
        return None, None


def has_role(roles, required_role):
    if not roles:
        return False
    return required_role in roles


class FiliereViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer

    def get_queryset(self):
        roles, user_id = get_role_from_request(self.request)
        if not roles or not user_id:
            return Filiere.objects.none()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Filiere.objects.none()

        active_roles = user.get_active_roles()
        if Role.ADMIN in active_roles:
            return Filiere.objects.all()
        if Role.HEAD_OF_DEPARTMENT in active_roles:
            hod = getattr(user, 'hod_profile', None)
            if hod and hod.department_id:
                return Filiere.objects.filter(departement_id=hod.department_id)
            return Filiere.objects.none()
        if Role.PROGRAM_MANAGER in active_roles:
            pm = getattr(user, 'program_manager_profile', None)
            if pm and pm.program_id:
                return Filiere.objects.filter(id=pm.program_id)
            return Filiere.objects.none()
        return Filiere.objects.none()

    def _can_write(self, user, filiere=None):
        active_roles = user.get_active_roles()
        if Role.ADMIN in active_roles:
            return True
        if Role.HEAD_OF_DEPARTMENT in active_roles:
            hod = getattr(user, 'hod_profile', None)
            if not hod or not hod.department_id:
                return False
            if filiere is not None:
                return filiere.departement_id == hod.department_id
            return True
        if Role.PROGRAM_MANAGER in active_roles:
            pm = getattr(user, 'program_manager_profile', None)
            if not pm or not pm.program_id:
                return False
            if filiere is not None:
                return filiere.id == pm.program_id
            return True
        return False

    def list(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        if not self._can_write(user):
            return Response({'error': 'Acces non autorise'}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        instance = self.get_object()
        if not self._can_write(user, instance):
            return Response({'error': 'Acces non autorise a cette filiere'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        instance = self.get_object()
        if not self._can_write(user, instance):
            return Response({'error': 'Acces non autorise a cette filiere'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        instance = self.get_object()
        if not self._can_write(user, instance):
            return Response({'error': 'Acces non autorise a cette filiere'}, status=403)
        return super().destroy(request, *args, **kwargs)


class DepartementViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer

    def get_queryset(self):
        roles, user_id = get_role_from_request(self.request)
        if not roles or not user_id:
            return Departement.objects.none()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Departement.objects.none()

        active_roles = user.get_active_roles()
        if Role.ADMIN in active_roles:
            return Departement.objects.all()
        if Role.HEAD_OF_DEPARTMENT in active_roles:
            hod = getattr(user, 'hod_profile', None)
            if hod and hod.department_id:
                return Departement.objects.filter(id=hod.department_id)
            return Departement.objects.none()
        return Departement.objects.none()

    def _can_write(self, user, dept=None):
        active_roles = user.get_active_roles()
        if Role.ADMIN in active_roles:
            return True
        if Role.HEAD_OF_DEPARTMENT in active_roles:
            hod = getattr(user, 'hod_profile', None)
            if not hod or not hod.department_id:
                return False
            if dept is not None:
                return dept.id == hod.department_id
            return True
        return False

    def list(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        if not self._can_write(user):
            return Response({'error': 'Acces non autorise'}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        instance = self.get_object()
        if not self._can_write(user, instance):
            return Response({'error': 'Acces non autorise a ce departement'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        instance = self.get_object()
        if not self._can_write(user, instance):
            return Response({'error': 'Acces non autorise a ce departement'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=404)
        instance = self.get_object()
        if not self._can_write(user, instance):
            return Response({'error': 'Acces non autorise a ce departement'}, status=403)
        return super().destroy(request, *args, **kwargs)


class SalleViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer


class AdminListViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(
            role_assignments__role__codename='admin',
            role_assignments__is_active=True
        )

    def get_serializer_class(self):
        return ProfessorUserSerializer

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response([], status=200)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._create_user(request, Role.ADMIN)

    def update(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def _create_user(self, request, role):
        email = request.data.get('email')
        password = request.data.get('password')
        nom = request.data.get('last_name', '')
        prenom = request.data.get('first_name', '')

        if not email or not password:
            return Response({'error': 'email et password obligatoires'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email déjà utilisé'}, status=400)

        user = User.objects.create_user(
            email=email, password=password,
            first_name=prenom, last_name=nom,
        )

        from users.views import create_role_assignments, create_profile_for_role
        all_roles = [role]
        extras = [{'role': role, 'data': {}}]

        if request.data.get('also_professor'):
            all_roles.append(Role.PROFESSOR)
            extras.append({'role': Role.PROFESSOR, 'data': {
                'specialization': request.data.get('specialization', ''),
            }})

        if request.data.get('also_head_of_department'):
            all_roles.append(Role.HEAD_OF_DEPARTMENT)
            extras.append({'role': Role.HEAD_OF_DEPARTMENT, 'data': {
                'department_id': request.data.get('department_id'),
            }})

        if request.data.get('also_program_manager'):
            all_roles.append(Role.PROGRAM_MANAGER)
            extras.append({'role': Role.PROGRAM_MANAGER, 'data': {
                'program_id': request.data.get('program_id'),
            }})

        create_role_assignments(user, all_roles)
        for extra in extras:
            create_profile_for_role(user, extra['role'], extra['data'])

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)

    def _update_user(self, request, *args, **kwargs):
        kwargs.pop('partial', False)
        instance = self.get_object()
        email = request.data.get('email', instance.email)
        nom = request.data.get('last_name', instance.last_name)
        prenom = request.data.get('first_name', instance.first_name)
        password = request.data.get('password')

        instance.email = email
        instance.last_name = nom
        instance.first_name = prenom
        if password:
            instance.set_password(password)
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class StudentListViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = User.objects.filter(
            role_assignments__role__codename='student',
            role_assignments__is_active=True
        )
        roles, user_id = get_role_from_request(self.request)
        if not roles or not user_id:
            return qs.none()
        if has_role(roles, 'admin'):
            return qs
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return qs.none()
            hod = getattr(user, 'hod_profile', None)
            if hod and hod.department_id:
                return qs.filter(
                    student_profile__program__departement_id=hod.department_id
                )
            return qs.none()
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return qs.none()
            pm = getattr(user, 'program_manager_profile', None)
            if pm and pm.program_id:
                return qs.filter(student_profile__program_id=pm.program_id)
            return qs.none()
        return qs.none()

    def get_serializer_class(self):
        return StudentUserSerializer

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not roles:
            return Response([], status=200)
        if has_role(roles, 'head_of_department') or has_role(roles, 'admin') or has_role(roles, 'program_manager'):
            return super().list(request, *args, **kwargs)
        return Response([], status=200)

    def _can_access_student(self, request, student_user=None):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return False
        if has_role(roles, 'admin'):
            return True
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return False
            hod = getattr(user, 'hod_profile', None)
            if not hod or not hod.department_id:
                return False
            if student_user:
                sp = getattr(student_user, 'student_profile', None)
                if sp and sp.program:
                    return sp.program.departement_id == hod.department_id
                return False
            return True
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return False
            pm = getattr(user, 'program_manager_profile', None)
            if not pm or not pm.program_id:
                return False
            if student_user:
                sp = getattr(student_user, 'student_profile', None)
                if sp:
                    return sp.program_id == pm.program_id
                return False
            return True
        return False

    def create(self, request, *args, **kwargs):
        if not self._can_access_student(request):
            return Response({'error': 'Acces non autorise'}, status=403)
        filiere_id = request.data.get('program_id') or request.data.get('filiere_id')
        roles, user_id = get_role_from_request(request)
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'Utilisateur introuvable'}, status=404)
            pm = getattr(user, 'program_manager_profile', None)
            if not pm or not pm.program_id:
                return Response({'error': 'Acces non autorise'}, status=403)
            if int(filiere_id) != pm.program_id if filiere_id else True:
                return Response({'error': 'Filiere hors de votre ressort'}, status=403)
        return self._create_user(request, Role.STUDENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_access_student(request, instance):
            return Response({'error': 'Acces non autorise a cet etudiant'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_access_student(request, instance):
            return Response({'error': 'Acces non autorise a cet etudiant'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_access_student(request, instance):
            return Response({'error': 'Acces non autorise a cet etudiant'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def _create_user(self, request, role):
        email = request.data.get('email')
        password = request.data.get('password')
        nom = request.data.get('last_name', '')
        prenom = request.data.get('first_name', '')
        cie = request.data.get('CIE', request.data.get('code_massar', ''))
        program_id = request.data.get('program_id') or request.data.get('filiere_id')

        if not email or not password:
            return Response({'error': 'email et password obligatoires'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email déjà utilisé'}, status=400)

        user = User.objects.create_user(
            email=email, password=password,
            first_name=prenom, last_name=nom,
        )

        from users.views import create_role_assignments, create_profile_for_role
        create_role_assignments(user, [role])
        create_profile_for_role(user, role, {
            'CIE': cie,
            'program_id': program_id,
        })

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)

    def _update_user(self, request, *args, **kwargs):
        kwargs.pop('partial', False)
        instance = self.get_object()
        email = request.data.get('email', instance.email)
        nom = request.data.get('last_name', instance.last_name)
        prenom = request.data.get('first_name', instance.first_name)
        password = request.data.get('password')

        instance.email = email
        instance.last_name = nom
        instance.first_name = prenom
        if password:
            instance.set_password(password)
        instance.save()

        program_id = request.data.get('program_id') or request.data.get('filiere_id')
        if program_id is not None:
            profile = getattr(instance, 'student_profile', None)
            if profile:
                profile.program_id = program_id
                profile.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProfessorListViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = User.objects.filter(
            role_assignments__role__codename='professor',
            role_assignments__is_active=True
        )
        roles, user_id = get_role_from_request(self.request)
        if not roles or not user_id:
            return qs.none()
        if has_role(roles, 'admin'):
            return qs
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return qs.none()
            hod = getattr(user, 'hod_profile', None)
            if hod and hod.department_id:
                return qs.filter(
                    professor_profile__departements=hod.department_id
                )
            return qs.none()
        if has_role(roles, 'program_manager'):
            return qs
        return qs.none()

    def get_serializer_class(self):
        return ProfessorUserSerializer

    def _get_user_and_dept(self, request):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return None, None
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None, None
        hod_dept_id = None
        if has_role(roles, 'head_of_department'):
            hod = getattr(user, 'hod_profile', None)
            if hod:
                hod_dept_id = hod.department_id
        return user, hod_dept_id

    def _can_manage_professor(self, user, hod_dept_id, professor_user=None):
        if Role.ADMIN in user.get_active_roles():
            return True
        if hod_dept_id:
            if professor_user:
                prof_profile = getattr(professor_user, 'professor_profile', None)
                if not prof_profile:
                    return False
                return prof_profile.departements.filter(id=hod_dept_id).exists()
            return True
        return False

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not roles:
            return Response([], status=200)
        if has_role(roles, 'head_of_department') or has_role(roles, 'admin') or has_role(roles, 'program_manager'):
            return super().list(request, *args, **kwargs)
        return Response([], status=200)

    def create(self, request, *args, **kwargs):
        user, hod_dept_id = self._get_user_and_dept(request)
        if not user or not self._can_manage_professor(user, hod_dept_id):
            return Response({'error': 'Acces non autorise'}, status=403)
        return self._create_user(request, Role.PROFESSOR, hod_dept_id)

    def update(self, request, *args, **kwargs):
        user, hod_dept_id = self._get_user_and_dept(request)
        if not user:
            return Response({'error': 'Authentification requise'}, status=401)
        instance = self.get_object()
        if not self._can_manage_professor(user, hod_dept_id, instance):
            return Response({'error': 'Acces non autorise a cet enseignant'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user, hod_dept_id = self._get_user_and_dept(request)
        if not user:
            return Response({'error': 'Authentification requise'}, status=401)
        instance = self.get_object()
        if not self._can_manage_professor(user, hod_dept_id, instance):
            return Response({'error': 'Acces non autorise a cet enseignant'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user, hod_dept_id = self._get_user_and_dept(request)
        if not user:
            return Response({'error': 'Authentification requise'}, status=401)
        instance = self.get_object()
        if not self._can_manage_professor(user, hod_dept_id, instance):
            return Response({'error': 'Acces non autorise a cet enseignant'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def _create_user(self, request, role, hod_dept_id=None):
        email = request.data.get('email')
        password = request.data.get('password')
        nom = request.data.get('last_name', '')
        prenom = request.data.get('first_name', '')

        if not email or not password:
            return Response({'error': 'email et password obligatoires'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email déjà utilisé'}, status=400)

        user = User.objects.create_user(
            email=email, password=password,
            first_name=prenom, last_name=nom,
        )

        from users.views import create_role_assignments, create_profile_for_role
        extra_data = {
            'specialization': request.data.get('specialization', ''),
        }
        department_ids = request.data.get('department_ids')
        if department_ids:
            extra_data['department_ids'] = department_ids
        elif hod_dept_id:
            extra_data['department_ids'] = [hod_dept_id]

        create_role_assignments(user, [role])
        create_profile_for_role(user, role, extra_data)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)

    def _update_user(self, request, *args, **kwargs):
        kwargs.pop('partial', False)
        instance = self.get_object()
        email = request.data.get('email', instance.email)
        nom = request.data.get('last_name', instance.last_name)
        prenom = request.data.get('first_name', instance.first_name)
        password = request.data.get('password')

        instance.email = email
        instance.last_name = nom
        instance.first_name = prenom
        if password:
            instance.set_password(password)
        instance.save()

        department_ids = request.data.get('department_ids')
        if department_ids is not None:
            profile = getattr(instance, 'professor_profile', None)
            if profile:
                profile.departements.set(department_ids)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class HeadOfDepartmentListViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(
            role_assignments__role__codename='head_of_department',
            role_assignments__is_active=True
        )

    def get_serializer_class(self):
        return HeadOfDepartmentUserSerializer

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response([], status=200)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._create_user(request, Role.HEAD_OF_DEPARTMENT)

    def update(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def _create_user(self, request, role):
        email = request.data.get('email')
        password = request.data.get('password')
        nom = request.data.get('last_name', '')
        prenom = request.data.get('first_name', '')

        if not email or not password:
            return Response({'error': 'email et password obligatoires'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email déjà utilisé'}, status=400)

        user = User.objects.create_user(
            email=email, password=password,
            first_name=prenom, last_name=nom,
        )

        from users.views import create_role_assignments, create_profile_for_role
        all_roles = [role]
        extras = [{'role': role, 'data': {
            'department_id': request.data.get('department_id'),
        }}]

        if request.data.get('also_professor'):
            all_roles.append(Role.PROFESSOR)
            extras.append({'role': Role.PROFESSOR, 'data': {
                'specialization': request.data.get('specialization', ''),
            }})

        if request.data.get('also_program_manager'):
            all_roles.append(Role.PROGRAM_MANAGER)
            extras.append({'role': Role.PROGRAM_MANAGER, 'data': {
                'program_id': request.data.get('program_id'),
            }})

        create_role_assignments(user, all_roles)
        for extra in extras:
            create_profile_for_role(user, extra['role'], extra['data'])

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)

    def _update_user(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        email = request.data.get('email', instance.email)
        nom = request.data.get('last_name', instance.last_name)
        prenom = request.data.get('first_name', instance.first_name)
        password = request.data.get('password')

        instance.email = email
        instance.last_name = nom
        instance.first_name = prenom
        if password:
            instance.set_password(password)
        instance.save()

        department_id = request.data.get('department_id')
        if department_id is not None:
            profile = getattr(instance, 'hod_profile', None)
            if profile:
                profile.department_id = department_id
                profile.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProgramManagerListViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(
            role_assignments__role__codename='program_manager',
            role_assignments__is_active=True
        )

    def get_serializer_class(self):
        return ProgramManagerUserSerializer

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response([], status=200)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._create_user(request, Role.PROGRAM_MANAGER)

    def update(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return self._update_user(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not has_role(roles, 'admin'):
            return Response({'error': 'Reserve aux administrateurs'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def _create_user(self, request, role):
        email = request.data.get('email')
        password = request.data.get('password')
        nom = request.data.get('last_name', '')
        prenom = request.data.get('first_name', '')

        if not email or not password:
            return Response({'error': 'email et password obligatoires'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email déjà utilisé'}, status=400)

        user = User.objects.create_user(
            email=email, password=password,
            first_name=prenom, last_name=nom,
        )

        from users.views import create_role_assignments, create_profile_for_role
        all_roles = [role]
        extras = [{'role': role, 'data': {
            'program_name': request.data.get('program_name', ''),
            'program_id': request.data.get('program_id'),
        }}]

        if request.data.get('also_professor'):
            all_roles.append(Role.PROFESSOR)
            extras.append({'role': Role.PROFESSOR, 'data': {
                'specialization': request.data.get('specialization', ''),
            }})

        create_role_assignments(user, all_roles)
        for extra in extras:
            create_profile_for_role(user, extra['role'], extra['data'])

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)

    def _update_user(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        email = request.data.get('email', instance.email)
        nom = request.data.get('last_name', instance.last_name)
        prenom = request.data.get('first_name', instance.first_name)
        password = request.data.get('password')

        instance.email = email
        instance.last_name = nom
        instance.first_name = prenom
        if password:
            instance.set_password(password)
        instance.save()

        program_id = request.data.get('program_id')
        if program_id is not None:
            profile = getattr(instance, 'program_manager_profile', None)
            if profile:
                profile.program_id = program_id
                profile.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PlanificationViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Planification.objects.all()
    serializer_class = PlanificationSerializer

    def get_queryset(self):
        roles, user_id = get_role_from_request(self.request)
        if not roles or not user_id:
            return Planification.objects.none()
        if has_role(roles, 'admin'):
            return Planification.objects.all()
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Planification.objects.none()
            hod = getattr(user, 'hod_profile', None)
            if hod and hod.department_id:
                return Planification.objects.filter(
                    filiere__departement_id=hod.department_id
                )
            return Planification.objects.none()
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Planification.objects.none()
            pm = getattr(user, 'program_manager_profile', None)
            if pm and pm.program_id:
                return Planification.objects.filter(
                    filiere_id=pm.program_id
                )
            return Planification.objects.none()
        return Planification.objects.none()

    def _can_manage(self, roles, user_id, planification=None):
        if has_role(roles, 'admin'):
            return True
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return False
            hod = getattr(user, 'hod_profile', None)
            if not hod or not hod.department_id:
                return False
            if planification is not None:
                return planification.filiere.departement_id == hod.department_id
            return True
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return False
            pm = getattr(user, 'program_manager_profile', None)
            if not pm or not pm.program_id:
                return False
            if planification is not None:
                return planification.filiere_id == pm.program_id
            return True
        return False

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not roles:
            return Response([], status=200)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        if not self._can_manage(roles, user_id):
            return Response({'error': 'Acces non autorise'}, status=403)
        filiere_id = request.data.get('filiere')
        if not filiere_id:
            return Response({'error': 'Filiere requise'}, status=400)
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'Utilisateur introuvable'}, status=404)
            hod = getattr(user, 'hod_profile', None)
            if not hod or not hod.department_id:
                return Response({'error': 'Acces non autorise'}, status=403)
            if not Filiere.objects.filter(id=filiere_id, departement_id=hod.department_id).exists():
                return Response({'error': 'Filiere hors de votre departement'}, status=403)
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'Utilisateur introuvable'}, status=404)
            pm = getattr(user, 'program_manager_profile', None)
            if not pm or not pm.program_id:
                return Response({'error': 'Acces non autorise'}, status=403)
            if int(filiere_id) != pm.program_id:
                return Response({'error': 'Filiere hors de votre ressort'}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        instance = self.get_object()
        if not self._can_manage(roles, user_id, instance):
            return Response({'error': 'Acces non autorise'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        instance = self.get_object()
        if not self._can_manage(roles, user_id, instance):
            return Response({'error': 'Acces non autorise'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not roles or not user_id:
            return Response({'error': 'Authentification requise'}, status=401)
        instance = self.get_object()
        if not self._can_manage(roles, user_id, instance):
            return Response({'error': 'Acces non autorise'}, status=403)
        return super().destroy(request, *args, **kwargs)


class SeanceQRViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = SeanceQR.objects.all()
    serializer_class = SeanceQRSerializer

    def get_queryset(self):
        roles, user_id = get_role_from_request(self.request)
        if not roles or not user_id:
            return SeanceQR.objects.none()
        if has_role(roles, 'admin'):
            return SeanceQR.objects.all()
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return SeanceQR.objects.none()
            hod = getattr(user, 'hod_profile', None)
            if hod and hod.department_id:
                return SeanceQR.objects.filter(
                    planification__filiere__departement_id=hod.department_id
                )
            return SeanceQR.objects.none()
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return SeanceQR.objects.none()
            pm = getattr(user, 'program_manager_profile', None)
            if pm and pm.program_id:
                return SeanceQR.objects.filter(
                    planification__filiere_id=pm.program_id
                )
            return SeanceQR.objects.none()
        if has_role(roles, 'professor'):
            return SeanceQR.objects.filter(planification__professor_id=user_id)
        return SeanceQR.objects.none()

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not roles:
            return Response([], status=200)
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not has_role(roles, 'professor'):
            return Response({'error': 'Reserve aux enseignants'}, status=403)
        seance = self.get_object()
        if seance.planification.professor.id != user_id:
            return Response({'error': 'Acces non autorise a cette seance'}, status=403)
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

    def get_queryset(self):
        roles, user_id = get_role_from_request(self.request)
        if not roles or not user_id:
            return Presence.objects.none()
        if has_role(roles, 'admin'):
            return Presence.objects.all()
        if has_role(roles, 'head_of_department'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Presence.objects.none()
            hod = getattr(user, 'hod_profile', None)
            if hod and hod.department_id:
                return Presence.objects.filter(
                    seance__planification__filiere__departement_id=hod.department_id
                )
            return Presence.objects.none()
        if has_role(roles, 'program_manager'):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Presence.objects.none()
            pm = getattr(user, 'program_manager_profile', None)
            if pm and pm.program_id:
                return Presence.objects.filter(
                    seance__planification__filiere_id=pm.program_id
                )
            return Presence.objects.none()
        if has_role(roles, 'professor'):
            return Presence.objects.filter(
                seance__planification__professor_id=user_id
            )
        return Presence.objects.none()

    def list(self, request, *args, **kwargs):
        roles, _ = get_role_from_request(request)
        if not roles:
            return Response([], status=200)
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        roles, user_id = get_role_from_request(request)
        if not has_role(roles, 'professor'):
            return Response({'error': 'Reserve aux enseignants'}, status=403)
        presence = self.get_object()
        if presence.seance.planification.professor.id != user_id:
            return Response({'error': 'Acces non autorise a cette presence'}, status=403)
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
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
        roles = decoded.get('roles', [])
        if isinstance(roles, str):
            roles = [roles]
        user_id = decoded.get('user_id')
    except Exception:
        return Response({'error': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

    if not has_role(roles, 'professor'):
        return Response({'error': 'Acces reserve aux enseignants'}, status=status.HTTP_403_FORBIDDEN)

    try:
        professor = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Enseignant introuvable'}, status=status.HTTP_404_NOT_FOUND)

    if planification.professor != professor:
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
@authentication_classes([])
@permission_classes([AllowAny])
def get_qrcode_seance(request, seance_id):
    auth_header = request.headers.get('Authorization', '')
    try:
        token = auth_header.split(' ')[1]
        decoded = AT(token)
        roles = decoded.get('roles', [])
        if isinstance(roles, str):
            roles = [roles]
        user_id = decoded.get('user_id')
    except Exception:
        return Response({'error': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

    if not has_role(roles, 'professor'):
        return Response({'error': 'Acces reserve aux enseignants'}, status=status.HTTP_403_FORBIDDEN)

    try:
        professor = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Enseignant introuvable'}, status=status.HTTP_404_NOT_FOUND)

    try:
        seance = SeanceQR.objects.get(id=seance_id)
    except SeanceQR.DoesNotExist:
        return Response({'error': 'Seance introuvable'}, status=status.HTTP_404_NOT_FOUND)

    if seance.planification.professor != professor:
        return Response({'error': 'Cette seance ne vous appartient pas'}, status=status.HTTP_403_FORBIDDEN)

    qrcode = QRCode.objects.filter(seance=seance).order_by('-cree_a').first()

    if not qrcode or not qrcode.is_valid():
        qrcode = QRCode.objects.create(seance=seance)

    expire_dans = int((qrcode.cree_a + timedelta(minutes=qrcode.expiration) - timezone.now()).total_seconds())

    return Response({
        'token': str(qrcode.token),
        'seance_id': seance.id,
        'expire_dans': max(expire_dans, 0)
    })


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
@authentication_classes([])
@permission_classes([AllowAny])
def planifications_du_jour(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': 'Token manquant'}, status=status.HTTP_401_UNAUTHORIZED)

    token_str = auth_header.split(' ')[1]
    try:
        token = AT(token_str)
        roles = token.get('roles', [])
        if isinstance(roles, str):
            roles = [roles]
        user_id = token.get('user_id')
    except Exception:
        return Response({'error': 'Token invalide'}, status=status.HTTP_401_UNAUTHORIZED)

    if not has_role(roles, 'professor'):
        return Response({'error': 'Acces reserve aux enseignants'}, status=status.HTTP_403_FORBIDDEN)

    try:
        professor = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Enseignant introuvable'}, status=status.HTTP_404_NOT_FOUND)

    jour_actuel = JOURS_MAP[timezone.now().weekday()]

    planifications = Planification.objects.filter(
        professor=professor,
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
        'date':           str(timezone.localtime().date()),
        'planifications': data,
        'total':          len(data),
    })


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def verifier_etudiant(request):
    data = request.data
    cie    = data.get('CIE') or data.get('massar') or data.get('code_massar')
    email  = data.get('email') or data.get('email_etudiant')

    if not cie and not email:
        return Response(
            {'error': 'CIE (Massar) ou email obligatoire pour la verification'},
            status=400
        )

    profile = None
    if cie:
        try:
            profile = StudentProfile.objects.get(CIE=cie)
        except StudentProfile.DoesNotExist:
            pass

    if not profile and email:
        try:
            user = User.objects.get(email=email)
            profile = getattr(user, 'student_profile', None)
        except User.DoesNotExist:
            pass

    if not profile:
        return Response({
            'found': False,
            'message': 'Etudiant introuvable dans le systeme',
            'recherche': {
                'CIE': cie,
                'email': email,
            }
        }, status=404)

    user = profile.user
    return Response({
        'found': True,
        'message': f'Etudiant trouve : {user.first_name} {user.last_name}',
        'etudiant': {
            'id':       user.id,
            'nom':      user.last_name,
            'prenom':   user.first_name,
            'email':    user.email,
            'CIE':      profile.CIE,
            'filiere':  profile.program.nom_filiere if profile.program else None,
        }
    }, status=200)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def liste_presences_seance(request, seance_id):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return Response({'error': 'Token manquant'}, status=401)

    token_str = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Token expire'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'error': 'Token invalide'}, status=401)

    roles = payload.get('roles', [])
    if isinstance(roles, str):
        roles = [roles]
    if not has_role(roles, 'professor'):
        return Response({'error': 'Acces reserve aux enseignants'}, status=403)

    user_id = payload.get('user_id')

    try:
        seance = SeanceQR.objects.get(id=seance_id)
    except SeanceQR.DoesNotExist:
        return Response({'error': 'Seance introuvable'}, status=404)

    if seance.planification.professor.id != user_id:
        return Response({'error': 'Acces non autorise a cette seance'}, status=403)

    presences = Presence.objects.filter(seance=seance).select_related('student')

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
                "nom": p.student.last_name,
                "prenom": p.student.first_name,
                "CIE": getattr(p.student, 'student_profile', None).CIE if hasattr(p.student, 'student_profile') else '',
                "heure_scan": str(p.heure_scan),
                "date_scan": str(p.date_scan),
                "ip_address": p.ip_address,
            }
            for p in presences
        ]
    }

    return Response(data, status=200)


import openpyxl

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def export_seance_excel(request, seance_id):
    try:
        raw_token     = request.headers.get('Authorization', '').split(' ')[1]
        payload       = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        roles = payload.get('roles', [])
        if isinstance(roles, str):
            roles = [roles]
    except Exception:
        return Response({'error': 'Token invalide'}, status=401)

    try:
        seance = SeanceQR.objects.select_related(
            'planification__professor',
            'planification__filiere',
            'planification__salle'
        ).get(id=seance_id)
    except SeanceQR.DoesNotExist:
        return Response({'error': 'Seance introuvable'}, status=404)

    if has_role(roles, 'professor') and seance.planification.professor.id == user_id:
        pass
    elif has_role(roles, 'admin'):
        pass
    elif has_role(roles, 'head_of_department'):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Acces non autorise'}, status=403)
        hod = getattr(user, 'hod_profile', None)
        if not hod or not hod.department_id:
            return Response({'error': 'Acces non autorise'}, status=403)
        if seance.planification.filiere.departement_id != hod.department_id:
            return Response({'error': 'Seance hors de votre departement'}, status=403)
    elif has_role(roles, 'program_manager'):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Acces non autorise'}, status=403)
        pm = getattr(user, 'program_manager_profile', None)
        if not pm or not pm.program_id:
            return Response({'error': 'Acces non autorise'}, status=403)
        if seance.planification.filiere_id != pm.program_id:
            return Response({'error': 'Seance hors de votre filiere'}, status=403)
    else:
        return Response({'error': 'Acces non autorise'}, status=403)

    filiere        = seance.planification.filiere
    student_profiles = StudentProfile.objects.filter(
        program=filiere
    ).select_related('user').order_by('user__last_name', 'user__first_name')

    presents_ids = set(
        Presence.objects.filter(seance=seance)
        .values_list('student_id', flat=True)
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Seance {seance_id}"

    from openpyxl.styles import Font, PatternFill, Alignment

    style_titre  = Font(bold=True, size=12)
    fill_present = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    fill_absent  = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    fill_header  = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
    bold         = Font(bold=True)

    ws.append(['Filiere',   filiere.nom_filiere])
    ws.append(['Module',    seance.planification.module])
    ws.append(['Salle',     str(seance.planification.salle)])
    ws.append(['Date',      str(seance.date)])
    ws.append(['Semestre',  filiere.semester_filiere])
    ws.append([])

    for row in ws.iter_rows(min_row=1, max_row=4):
        row[0].font = style_titre

    header_row = ["N", "Nom", "Prenom", "CIE", "Filiere", "Presence"]
    ws.append(header_row)

    header_excel_row = ws.max_row
    for cell in ws[header_excel_row]:
        cell.font      = bold
        cell.fill      = fill_header
        cell.alignment = Alignment(horizontal='center')

    for i, sp in enumerate(student_profiles, start=1):
        est_present = sp.user.id in presents_ids
        statut      = 'Present' if est_present else 'Absent'

        ws.append([
            i,
            sp.user.last_name,
            sp.user.first_name,
            sp.CIE,
            str(sp.program),
            statut,
        ])

        statut_cell      = ws.cell(row=ws.max_row, column=6)
        statut_cell.fill = fill_present if est_present else fill_absent
        statut_cell.alignment = Alignment(horizontal='center')

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 15

    filename = f"presences_seance_{seance_id}_{seance.date}.xlsx"
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def scanner_presence(request):
    token_uuid = request.data.get('token')
    cie        = request.data.get('CIE')
    latitude_etudiant = request.data.get('latitude_etudiant')
    longitude_etudiant= request.data.get('longitude_etudiant')

    if not all([token_uuid, cie]):
        return Response({'error': 'token et CIE obligatoires'}, status=400)

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    try:
        qrcode = QRCode.objects.get(token=token_uuid)
    except QRCode.DoesNotExist:
        return Response({'error': 'QR Code invalide'}, status=404)

    if not qrcode.is_valid():
        return Response({'error': 'QR Code expire'}, status=400)

    seance = qrcode.seance

    if latitude_etudiant and longitude_etudiant and seance.latitude_prof and seance.longitude_prof:
        distance = calculer_distance(
            float(seance.latitude_prof), float(seance.longitude_prof),
            float(latitude_etudiant), float(longitude_etudiant)
        )
        if distance > 150:
            return Response({
                'error': f'Vous etes trop loin du QR Code ({int(distance)}m). Vous devez etre dans la salle.'
            }, status=403)

    if Presence.objects.filter(seance=seance, ip_address=ip).exists():
        return Response({'error': 'Ce telephone a deja ete utilise pour cette seance'}, status=400)

    try:
        student_profile = StudentProfile.objects.get(CIE=cie)
    except StudentProfile.DoesNotExist:
        return Response({'error': 'CIE introuvable'}, status=404)

    if Presence.objects.filter(student=student_profile.user, seance=seance).exists():
        return Response({'error': 'Presence deja enregistree'}, status=400)

    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)

    Presence.objects.create(
        student=student_profile.user,
        seance=seance,
        date_scan=now_local.date(),
        heure_scan=now_local.time(),
        ip_address=ip,
    )

    return Response({
        'status': 'success',
        'message': f'Presence enregistree pour {student_profile.user.first_name} {student_profile.user.last_name}',
        'heure': str(now_local.time())[:8],
    })


import cloudinary.uploader

@api_view(['POST', 'DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def update_profile_photo(request):
    roles, user_id = get_role_from_request(request)
    if not roles or not user_id:
        return Response({'error': 'Token invalide'}, status=401)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    if request.method == 'DELETE':
        user.photo_url = None
        user.save()
        return Response({'message': 'Photo supprimee'}, status=200)

    photo = request.FILES.get('photo')
    if not photo:
        return Response({'error': 'Aucune image fournie'}, status=400)

    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if photo.content_type not in allowed_types:
        return Response({'error': 'Format non supporte (jpeg, png, webp)'}, status=status.HTTP_400_BAD_REQUEST)

    if photo.size > 2 * 1024 * 1024:
        return Response({'error': 'Image (max 2 MB)'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        role_name = roles[0] if roles else 'user'
        result = cloudinary.uploader.upload(
            photo,
            folder=f'presenceqr/profiles/{role_name}s/',
            public_id=f'{role_name}_{user_id}',
            overwrite=True,
            transformation=[
                {'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'},
            ]
        )
        url = result['secure_url']
        user.photo_url = url
        user.save()
        return Response({'message': 'Photo mise a jour', 'photo_url': url}, status=200)
    except Exception as e:
        return Response({'error': f'Erreur Cloudinary : {str(e)}'}, status=500)


@api_view(['GET', 'PATCH'])
@authentication_classes([])
@permission_classes([AllowAny])
def my_profile(request):
    roles, user_id = get_role_from_request(request)
    if not roles or not user_id:
        return Response({'error': 'Token invalide'}, status=401)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    student_profile = getattr(user, 'student_profile', None)
    professor_profile = getattr(user, 'professor_profile', None)

    if has_role(roles, 'student'):
        if request.method == 'PATCH':
            return Response({'error': 'Modification non autorisee'}, status=403)
        return Response({
            'id': user.id,
            'nom': user.last_name,
            'prenom': user.first_name,
            'email': user.email,
            'CIE': student_profile.CIE if student_profile else None,
            'filiere': str(student_profile.program) if student_profile and student_profile.program else None,
            'photo_url': user.photo_url,
            'role': 'etudiant',
        })

    if has_role(roles, 'professor'):
        if request.method == 'PATCH':
            return Response({'error': 'Modification non autorisee'}, status=403)
        return Response({
            'id': user.id,
            'nom': user.last_name,
            'prenom': user.first_name,
            'email': user.email,
            'specialization': professor_profile.specialization if professor_profile else None,
            'photo_url': user.photo_url,
            'role': 'enseignant',
        })

    if has_role(roles, 'admin'):
        if request.method == 'PATCH':
            for field in ['last_name', 'first_name', 'email']:
                if field in request.data:
                    setattr(user, field, request.data[field])
            user.save()
        return Response({
            'id': user.id,
            'nom': user.last_name,
            'prenom': user.first_name,
            'email': user.email,
            'photo_url': user.photo_url,
            'role': 'admin',
        })

    return Response({'error': 'Role non reconnu'}, status=400)


import math

def calculer_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def mes_planifications(request):
    roles, professor_id = get_role_from_request(request)
    if not has_role(roles, 'professor'):
        return Response({'error': 'Reserve aux enseignants'}, status=403)

    data = request.data.copy()
    data['professor'] = professor_id

    serializer = PlanificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PATCH', 'DELETE'])
@authentication_classes([])
@permission_classes([AllowAny])
def mes_planifications_detail(request, planification_id):
    roles, professor_id = get_role_from_request(request)
    if not has_role(roles, 'professor'):
        return Response({'error': 'Reserve aux enseignants'}, status=403)

    try:
        planification = Planification.objects.get(id=planification_id)
    except Planification.DoesNotExist:
        return Response({'error': 'Planification introuvable'}, status=404)

    if planification.professor.id != professor_id:
        return Response({'error': 'Acces non autorise a cette planification'}, status=403)

    if request.method == 'DELETE':
        planification.delete()
        return Response({'message': 'Planification supprimee'}, status=200)

    if request.method == 'PATCH':
        data = request.data.copy()
        data.pop('professor', None)

        serializer = PlanificationSerializer(planification, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def emploi_du_temps_etudiant(request):
    roles, user_id = get_role_from_request(request)
    if not has_role(roles, 'student'):
        return Response({'error': 'Reserve aux etudiants'}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Etudiant introuvable'}, status=404)

    student_profile = getattr(user, 'student_profile', None)
    if not student_profile or not student_profile.program:
        return Response({'error': 'Aucune filiere associee'}, status=404)

    planifications = Planification.objects.filter(
        filiere=student_profile.program
    ).select_related('professor', 'salle', 'filiere')

    ordre_jours = {
        'lundi': 1, 'mardi': 2, 'mercredi': 3,
        'jeudi': 4, 'vendredi': 5, 'samedi': 6, 'dimanche': 7
    }
    planifications = sorted(
        planifications,
        key=lambda p: (ordre_jours.get(p.jour.lower(), 99), p.heure_debut)
    )

    data = {
        "filiere": str(student_profile.program),
        "total": len(planifications),
        "planifications": [
            {
                "id": p.id,
                "jour": p.jour,
                "heure_debut": str(p.heure_debut),
                "heure_fin": str(p.heure_fin),
                "module": p.module,
                "salle": p.salle.nom_salle,
                "enseignant": f"{p.professor.first_name} {p.professor.last_name}",
            }
            for p in planifications
        ]
    }

    return Response(data, status=200)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def importer_etudiants(request):
    """Import students from an Excel file (.xlsx)."""
    excel_file = request.FILES.get('file')
    if not excel_file:
        return Response({'error': 'Aucun fichier fourni'}, status=400)

    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return Response({'error': 'Format de fichier invalide. Utilisez un fichier .xlsx'}, status=400)

    try:
        wb = openpyxl.load_workbook(excel_file, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as e:
        return Response({'error': f'Erreur de lecture du fichier: {str(e)}'}, status=400)

    if len(rows) < 2:
        return Response({'error': 'Le fichier est vide ou ne contient que l\'en-tête'}, status=400)

    header = [str(cell).strip().lower() if cell else '' for cell in rows[0]]

    col_map = {}
    expected_cols = ['nom', 'prenom', 'email', 'password', 'cie', 'filiere_id']
    for col in expected_cols:
        try:
            col_map[col] = header.index(col)
        except ValueError:
            return Response({'error': f'Colonne "{col}" manquante dans le fichier'}, status=400)

    try:
        col_map['groupe'] = header.index('groupe')
    except ValueError:
        col_map['groupe'] = None

    success_count = 0
    errors = []
    created_students = []

    for i, row in enumerate(rows[1:], start=2):
        try:
            nom = str(row[col_map['nom']]).strip() if row[col_map['nom']] else ''
            prenom = str(row[col_map['prenom']]).strip() if row[col_map['prenom']] else ''
            email = str(row[col_map['email']]).strip().lower() if row[col_map['email']] else ''
            password = str(row[col_map['password']]) if row[col_map['password']] else ''
            cie = str(row[col_map['cie']]).strip() if row[col_map['cie']] else ''
            filiere_id = row[col_map['filiere_id']]

            if not nom or not prenom or not email or not password or not cie or filiere_id is None:
                errors.append({'row': i, 'message': 'Champs obligatoires manquants'})
                continue

            if User.objects.filter(email=email).exists():
                errors.append({'row': i, 'message': f'Email déjà utilisé: {email}'})
                continue

            if StudentProfile.objects.filter(CIE=cie).exists():
                errors.append({'row': i, 'message': f'CNE déjà existant: {cie}'})
                continue

            try:
                filiere_id = int(filiere_id)
            except (ValueError, TypeError):
                errors.append({'row': i, 'message': f'filiere_id invalide: {filiere_id}'})
                continue

            user = User.objects.create_user(
                email=email, password=password,
                first_name=prenom, last_name=nom,
            )
            from users.views import create_role_assignments, create_profile_for_role
            create_role_assignments(user, [Role.STUDENT])
            create_profile_for_role(user, Role.STUDENT, {
                'CIE': cie,
                'program_id': filiere_id,
            })

            created_students.append(user)
            success_count += 1

        except Exception as e:
            errors.append({'row': i, 'message': str(e)})

    return Response({
        'success': success_count,
        'total': len(rows) - 1,
        'errors': errors,
        'students_created': StudentUserSerializer(created_students, many=True).data,
    })


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def etudiants_par_module(request):
    """List students grouped by module based on planifications."""
    roles, user_id = get_role_from_request(request)
    if not roles or not user_id:
        return Response([], status=200)

    planifications = Planification.objects.all().select_related('filiere')

    if has_role(roles, 'head_of_department'):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response([], status=200)
        hod = getattr(user, 'hod_profile', None)
        if hod and hod.department_id:
            planifications = planifications.filter(filiere__departement_id=hod.department_id)
        else:
            return Response([], status=200)
    elif has_role(roles, 'program_manager'):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response([], status=200)
        pm = getattr(user, 'program_manager_profile', None)
        if pm and pm.program_id:
            planifications = planifications.filter(filiere_id=pm.program_id)
        else:
            return Response([], status=200)
    elif not has_role(roles, 'admin'):
        return Response([], status=200)

    module_data = {}
    for plan in planifications:
        module_name = plan.module
        if not module_name:
            continue
        filiere_id = plan.filiere_id
        filiere_name = plan.filiere.nom_filiere if plan.filiere else ''

        if module_name not in module_data:
            module_data[module_name] = {
                'module': module_name,
                'filieres': set(),
                'filiere_ids': set(),
            }
        module_data[module_name]['filieres'].add(filiere_name)
        module_data[module_name]['filiere_ids'].add(filiere_id)

    result = []
    for module_name, data in module_data.items():
        students = User.objects.filter(
            role_assignments__role__codename='student',
            role_assignments__is_active=True,
            student_profile__program_id__in=data['filiere_ids'],
        ).distinct().order_by('last_name', 'first_name')

        result.append({
            'module': module_name,
            'filieres': sorted(data['filieres']),
            'etudiants': StudentUserSerializer(students, many=True).data,
            'total': students.count(),
        })

    result.sort(key=lambda x: x['module'])
    return Response(result)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def home(request):
    return HttpResponse("Render works!")
