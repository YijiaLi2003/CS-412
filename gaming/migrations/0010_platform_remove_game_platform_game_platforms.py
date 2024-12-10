# Generated by Django 4.2.16 on 2024-12-10 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gaming", "0009_alter_game_platform"),
    ]

    operations = [
        migrations.CreateModel(
            name="Platform",
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
                ("name", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.RemoveField(model_name="game", name="platform",),
        migrations.AddField(
            model_name="game",
            name="platforms",
            field=models.ManyToManyField(related_name="games", to="gaming.platform"),
        ),
    ]
