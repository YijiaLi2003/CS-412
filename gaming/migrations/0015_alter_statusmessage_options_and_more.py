# Generated by Django 4.2.16 on 2024-12-10 16:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("gaming", "0014_comment_like"),
    ]

    operations = [
        migrations.AlterModelOptions(name="statusmessage", options={},),
        migrations.AlterField(
            model_name="statusmessage",
            name="timestamp",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
