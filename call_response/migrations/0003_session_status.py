# Generated by Django 4.2.16 on 2024-11-18 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call_response', '0002_session_teacher_alter_session_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='status',
            field=models.CharField(default='pending', max_length=20),
        ),
    ]