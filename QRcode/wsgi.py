"""
WSGI config for QRcode project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QRcode.settings')

if os.environ.get('RENDER'):
    import django
    django.setup()
    from django.core.management import call_command
    call_command('migrate', '--noinput', interactive=False)

application = get_wsgi_application()
