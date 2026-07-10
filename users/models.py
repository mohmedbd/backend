from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.exceptions import ValidationError
import uuid


class Role(models.TextChoices):
    ADMIN = 'admin', 'Administrateur'
    HEAD_OF_DEPARTMENT = 'head_of_department', 'Chef de département'
    PROGRAM_MANAGER = 'program_manager', 'Responsable de filière'
    PROFESSOR = 'professor', 'Enseignant'
    STUDENT = 'student', 'Étudiant'


ROLE_HIERARCHY = [
    Role.ADMIN,
    Role.HEAD_OF_DEPARTMENT,
    Role.PROGRAM_MANAGER,
    Role.PROFESSOR,
]

ROLE_CUMULATION = {
    Role.ADMIN: {Role.HEAD_OF_DEPARTMENT, Role.PROGRAM_MANAGER, Role.PROFESSOR},
    Role.HEAD_OF_DEPARTMENT: {Role.PROGRAM_MANAGER, Role.PROFESSOR},
    Role.PROGRAM_MANAGER: {Role.PROFESSOR},
    Role.PROFESSOR: set(),
    Role.STUDENT: set(),
}

ACADEMIC_EMAIL_DOMAINS = [
    '@edu.ma',
    '@univ.ma',
    '@uae.ma',
    '@uhp.ma',
    '@usms.ma',
    '@ump.ma',
    '@umi.ma',
    '@uit.ma',
]


def validate_role_combination(roles):
    roles = set(roles)
    if not roles:
        return

    if Role.STUDENT in roles and len(roles) > 1:
        raise ValidationError("Un étudiant ne peut pas cumuler d'autres rôles.")

    non_student_roles = {r for r in roles if r != Role.STUDENT}
    if len(non_student_roles) <= 1:
        return

    for r in non_student_roles:
        allowed = ROLE_CUMULATION.get(r, set())
        others = non_student_roles - {r}
        if others.issubset(allowed):
            return

    raise ValidationError(
        "Combinaison de rôles invalide. Consultez les règles de cumul."
    )


def validate_academic_email(email):
    if not any(email.lower().endswith(domain) for domain in ACADEMIC_EMAIL_DOMAINS):
        raise ValidationError(
            f"L'email doit être un email académique valide: {', '.join(ACADEMIC_EMAIL_DOMAINS)}"
        )


class CustomUserManager(UserManager):
    def _generate_username(self, email):
        return email.split('@')[0][:30] or str(uuid.uuid4())[:30]

    def create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = self._generate_username(email)
        return super().create_user(email=email, password=password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = self._generate_username(email)
        return super().create_superuser(email=email, password=password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    roles = models.ManyToManyField(
        'RoleConfig',
        through='UserRoleAssignment',
        blank=True,
    )

    def get_active_roles(self):
        return list(
            self.role_assignments.filter(is_active=True)
            .values_list('role__codename', flat=True)
        )

    def has_role(self, role_codename):
        return self.role_assignments.filter(
            role__codename=role_codename, is_active=True
        ).exists()

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'


class RoleConfig(models.Model):
    codename = models.CharField(max_length=30, unique=True)
    display_name = models.CharField(max_length=50)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = 'Rôle'
        verbose_name_plural = 'Rôles'


class UserRoleAssignment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='role_assignments'
    )
    role = models.ForeignKey(
        RoleConfig, on_delete=models.CASCADE, related_name='assignments'
    )
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = 'Assignation de rôle'
        verbose_name_plural = 'Assignations de rôles'

    def clean(self):
        existing_roles = set(
            UserRoleAssignment.objects.filter(user=self.user, is_active=True)
            .exclude(pk=self.pk)
            .values_list('role__codename', flat=True)
        )
        if self.is_active:
            new_roles = existing_roles | {self.role.codename}
            validate_role_combination(new_roles)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} → {self.role.display_name}"


class AdminProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='admin_profile'
    )
    can_manage_departments = models.BooleanField(default=True)
    can_manage_programs = models.BooleanField(default=True)
    can_manage_users = models.BooleanField(default=True)
    can_manage_system = models.BooleanField(default=True)

    def __str__(self):
        return f"Profil Admin: {self.user.email}"

    class Meta:
        verbose_name = 'Profil Administrateur'
        verbose_name_plural = 'Profils Administrateurs'


class ProfessorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='professor_profile'
    )
    specialization = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    can_create_seances = models.BooleanField(default=True)
    can_scan_qr = models.BooleanField(default=False)
    can_export_presences = models.BooleanField(default=True)
    departements = models.ManyToManyField(
        'gestion.Departement',
        blank=True,
        related_name='professors',
    )

    def __str__(self):
        return f"Profil Enseignant: {self.user.email}"

    class Meta:
        verbose_name = 'Profil Enseignant'
        verbose_name_plural = 'Profils Enseignants'


class HeadOfDepartmentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='hod_profile'
    )
    department = models.ForeignKey(
        'gestion.Departement',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='heads_of_department',
    )
    can_manage_professors = models.BooleanField(default=True)
    can_manage_schedules = models.BooleanField(default=True)
    can_view_all_department_data = models.BooleanField(default=True)

    def __str__(self):
        return f"Chef Dept {self.department.nom_departement if self.department else 'N/A'}: {self.user.email}"

    class Meta:
        verbose_name = 'Profil Chef de Département'
        verbose_name_plural = 'Profils Chefs de Département'


class ProgramManagerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='program_manager_profile'
    )
    program_name = models.CharField(max_length=100, blank=True)
    program = models.ForeignKey(
        'gestion.Filiere',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='program_managers',
    )
    can_manage_students = models.BooleanField(default=True)
    can_manage_program_schedule = models.BooleanField(default=True)
    can_view_program_presences = models.BooleanField(default=True)

    def __str__(self):
        return f"Resp. {self.program_name}: {self.user.email}"

    class Meta:
        verbose_name = 'Profil Responsable de Filière'
        verbose_name_plural = 'Profils Responsables de Filière'


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='student_profile'
    )
    CIE = models.CharField(max_length=30, unique=True)
    program = models.ForeignKey(
        'gestion.Filiere',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    enrollment_date = models.DateField(auto_now_add=True)
    can_scan_presence = models.BooleanField(default=True)
    can_view_own_schedule = models.BooleanField(default=True)

    def __str__(self):
        return f"Étudiant {self.CIE}: {self.user.email}"

    class Meta:
        verbose_name = 'Profil Étudiant'
        verbose_name_plural = 'Profils Étudiants'
