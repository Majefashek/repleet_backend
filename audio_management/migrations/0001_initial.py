# Generated by Django 4.2.16 on 2024-11-05 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AudioTrack",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "audio_file",
                    models.FileField(unique=True, upload_to="reference_tracks/"),
                ),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                ("artist", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "description",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "category",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Piano", "Piano"),
                            ("Guitar", "Guitar"),
                            ("Drum", "Drum"),
                            ("Vocals", "Vocals"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "difficulty_level",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Easy", "Easy"),
                            ("Medium", "Medium"),
                            ("Hard", "Hard"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "genre",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Pop", "Pop"),
                            ("Rock", "Rock"),
                            ("Classical", "Classical"),
                            ("Jazz", "Jazz"),
                            ("Blues", "Blues"),
                            ("Hip-Hop/Rap", "Hip-Hop/Rap"),
                            ("R&B", "R&B"),
                            ("Country", "Country"),
                            ("Reggae", "Reggae"),
                            ("Soul", "Soul"),
                            ("Metal", "Metal"),
                            ("Gospel", "Gospel"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "musical_element",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Chord Progression", "Chord Progression"),
                            ("Solo Runs", "Solo Runs"),
                            ("Chord P & Solo Runs", "Chord P & Solo Runs"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "music_length",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Part of Music", "Part of Music"),
                            ("Full Music", "Full Music"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
            ],
        ),
    ]