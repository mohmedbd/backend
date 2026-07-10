import django.db.models.deletion
from django.db import migrations, models


def copy_fk_to_m2m(apps, schema_editor):
    Module = apps.get_model('gestion', 'Module')
    for module in Module.objects.iterator():
        if module.semestre_id is not None:
            module.semestre_m2m.add(module.semestre_id)


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='semestre_m2m',
            field=models.ManyToManyField(related_name='modules', to='gestion.semestre'),
        ),
        migrations.RunPython(copy_fk_to_m2m, reverse_code=migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='module',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='module',
            name='semestre',
        ),
        migrations.RenameField(
            model_name='module',
            old_name='semestre_m2m',
            new_name='semestre',
        ),
        migrations.AddConstraint(
            model_name='module',
            constraint=models.UniqueConstraint(fields=('nom_module',), name='unique_module_name'),
        ),
    ]
