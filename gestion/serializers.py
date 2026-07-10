from rest_framework import serializers
from .models import Departement, Filiere, Semestre, Module, Salle, Planification, SeanceQR, QRCode, Presence, AuditLog
from users.models import User, StudentProfile


class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = '__all__'


class FiliereSerializer(serializers.ModelSerializer):
    departement_name = serializers.CharField(source='departement.nom_departement', read_only=True, allow_null=True)

    class Meta:
        model = Filiere
        fields = ['id', 'nom_filiere', 'departement', 'departement_name']


class SemestreSerializer(serializers.ModelSerializer):
    filiere_name = serializers.CharField(source='filiere.nom_filiere', read_only=True)

    class Meta:
        model = Semestre
        fields = ['id', 'nom_semestre', 'filiere', 'filiere_name']


class ModuleSerializer(serializers.ModelSerializer):
    semestre = serializers.PrimaryKeyRelatedField(many=True, queryset=Semestre.objects.all())
    semestre_name = serializers.SerializerMethodField(read_only=True)
    filiere = serializers.SerializerMethodField(read_only=True)
    filiere_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'nom_module', 'semestre', 'semestre_name', 'filiere', 'filiere_name']

    def get_semestre_name(self, obj):
        names = obj.semestre.values_list('nom_semestre', flat=True)
        return ', '.join(names) if names else ''

    def get_filiere(self, obj):
        names = list(set(obj.semestre.values_list('filiere__nom_filiere', flat=True)))
        return ', '.join(names) if names else ''

    def get_filiere_name(self, obj):
        names = list(set(obj.semestre.values_list('filiere__nom_filiere', flat=True)))
        return ', '.join(names) if names else ''


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = '__all__'


class PlanificationSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(read_only=True)
    semestre_name = serializers.CharField(read_only=True)

    class Meta:
        model = Planification
        fields = ['id', 'professor', 'salle', 'filiere', 'semestre', 'module',
                  'module_ref', 'module_name', 'semestre_name', 'jour',
                  'heure_debut', 'heure_fin']


class SeanceQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeanceQR
        fields = '__all__'


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'


class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = '__all__'


class StudentUserSerializer(serializers.ModelSerializer):
    CIE = serializers.CharField(source='student_profile.CIE', read_only=True)
    filiere = serializers.CharField(source='student_profile.program.nom_filiere', read_only=True, allow_null=True)
    filiere_id = serializers.IntegerField(source='student_profile.program_id', read_only=True, allow_null=True)
    module_ids = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'photo_url', 'CIE', 'filiere', 'filiere_id', 'module_ids', 'modules']

    def get_module_ids(self, obj):
        profile = getattr(obj, 'student_profile', None)
        if profile:
            return list(profile.modules.values_list('id', flat=True))
        return []

    def get_modules(self, obj):
        profile = getattr(obj, 'student_profile', None)
        if profile:
            return list(profile.modules.values_list('nom_module', flat=True))
        return []


class ProfessorUserSerializer(serializers.ModelSerializer):
    specialization = serializers.CharField(source='professor_profile.specialization', read_only=True, allow_null=True)
    department_ids = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'photo_url', 'specialization', 'department_ids']

    def get_department_ids(self, obj):
        profile = getattr(obj, 'professor_profile', None)
        if profile:
            return list(profile.departements.values_list('id', flat=True))
        return []


class HeadOfDepartmentUserSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(source='hod_profile.department_id', read_only=True, allow_null=True)
    department_name = serializers.CharField(source='hod_profile.department.nom_departement', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'photo_url', 'department_id', 'department_name']


class ProgramManagerUserSerializer(serializers.ModelSerializer):
    program_id = serializers.IntegerField(source='program_manager_profile.program_id', read_only=True, allow_null=True)
    program_name = serializers.CharField(source='program_manager_profile.program.nom_filiere', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'photo_url', 'program_id', 'program_name']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action_type', 'description', 'timestamp', 'related_object_type', 'related_object_id']

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name or obj.user.last_name else obj.user.email
        return "Système"
