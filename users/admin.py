from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, RoleConfig, UserRoleAssignment,
    AdminProfile, ProfessorProfile, HeadOfDepartmentProfile,
    ProgramManagerProfile, StudentProfile,
)


class UserRoleAssignmentInline(admin.TabularInline):
    model = UserRoleAssignment
    extra = 1


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False


class ProfessorProfileInline(admin.StackedInline):
    model = ProfessorProfile
    can_delete = False


class HeadOfDepartmentProfileInline(admin.StackedInline):
    model = HeadOfDepartmentProfile
    can_delete = False


class ProgramManagerProfileInline(admin.StackedInline):
    model = ProgramManagerProfile
    can_delete = False


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'get_full_name', 'get_roles_display', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = [UserRoleAssignmentInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    def get_roles_display(self, obj):
        roles = obj.get_active_roles()
        return ', '.join(r.replace('_', ' ').title() for r in roles) if roles else '—'
    get_roles_display.short_description = 'Rôles'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        inlines = super().get_inline_instances(request, obj)
        if obj.has_role('admin'):
            inlines.append(AdminProfileInline(self.model, self.admin_site))
        if obj.has_role('professor'):
            inlines.append(ProfessorProfileInline(self.model, self.admin_site))
        if obj.has_role('head_of_department'):
            inlines.append(HeadOfDepartmentProfileInline(self.model, self.admin_site))
        if obj.has_role('program_manager'):
            inlines.append(ProgramManagerProfileInline(self.model, self.admin_site))
        if obj.has_role('student'):
            inlines.append(StudentProfileInline(self.model, self.admin_site))
        return inlines


@admin.register(RoleConfig)
class RoleConfigAdmin(admin.ModelAdmin):
    list_display = ('codename', 'display_name')


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'assigned_at')
    list_filter = ('role', 'is_active')
