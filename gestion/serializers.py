from rest_framework import serializers
from .models import Departement, Filiere, Salle, Planification, SeanceQR, QRCode, Presence
from users.models import User, StudentProfile


class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = '__all__'


class FiliereSerializer(serializers.ModelSerializer):
    departement_name = serializers.CharField(source='departement.nom_departement', read_only=True, allow_null=True)

    class Meta:
        model = Filiere
        fields = ['id', 'nom_filiere', 'semester_filiere', 'departement', 'departement_name']


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = '__all__'


class PlanificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planification
        fields = '__all__'


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

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'photo_url', 'CIE', 'filiere']


class ProfessorUserSerializer(serializers.ModelSerializer):
    specialization = serializers.CharField(source='professor_profile.specialization', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'photo_url', 'specialization']


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
