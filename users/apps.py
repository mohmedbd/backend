from django.apps import AppConfig
from django.db.models.signals import post_migrate


def init_roles(sender, **kwargs):
    from .models import Role, RoleConfig
    for codename, display_name in Role.choices:
        RoleConfig.objects.get_or_create(
            codename=codename,
            defaults={'display_name': display_name}
        )


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        post_migrate.connect(init_roles, sender=self)
