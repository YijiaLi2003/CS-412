# Generated by Django 4.2.16 on 2024-10-03 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Profile",
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
                ("first_name", models.CharField(max_length=30)),
                ("last_name", models.CharField(max_length=30)),
                ("city", models.CharField(max_length=50)),
                ("email_address", models.EmailField(max_length=254, unique=True)),
                ("profile_image_url", models.URLField(blank=True)),
            ],
        ),
    ]