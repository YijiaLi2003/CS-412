# Generated by Django 4.2.16 on 2024-11-11 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Voter",
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
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("street_number", models.CharField(max_length=10)),
                ("street_name", models.CharField(max_length=100)),
                (
                    "apartment_number",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                ("zip_code", models.CharField(max_length=10)),
                ("date_of_birth", models.DateField()),
                ("date_of_registration", models.DateField()),
                ("party_affiliation", models.CharField(max_length=50)),
                ("precinct_number", models.CharField(max_length=10)),
                ("v20state", models.BooleanField()),
                ("v21town", models.BooleanField()),
                ("v21primary", models.BooleanField()),
                ("v22general", models.BooleanField()),
                ("v23town", models.BooleanField()),
                ("voter_score", models.IntegerField()),
            ],
        ),
    ]
