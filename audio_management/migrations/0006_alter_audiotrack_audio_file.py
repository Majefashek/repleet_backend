# Generated by Django 4.2.16 on 2024-11-21 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio_management', '0005_myreferencetracks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiotrack',
            name='audio_file',
            field=models.FileField(blank=True, null=True, unique=True, upload_to='reference_tracks/'),
        ),
    ]
