from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0002_rename_id_planification_seanceqr_planification_and_more'),
    ]

    operations = [

        # 1. Ajouter une nouvelle colonne FK (nullable)
        migrations.AddField(
            model_name='etudiant',
            name='filiere_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='gestion.filiere',
            ),
        ),

        # 2. Remplir la FK à partir du texte existant
        migrations.RunSQL(
            sql="""
                UPDATE gestion_etudiant e
                SET filiere_fk_id = f.id
                FROM gestion_filiere f
                WHERE LOWER(e.filier_etudiant) = LOWER(f.nom_filiere);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 3. Supprimer l'ancien CharField
        migrations.RemoveField(
            model_name='etudiant',
            name='filier_etudiant',
        ),

        # 4. Renommer la nouvelle colonne
        migrations.RenameField(
            model_name='etudiant',
            old_name='filiere_fk',
            new_name='filier_etudiant',
        ),
    ]