# Generated by Django 4.2.16 on 2024-12-10 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gaming", "0017_alter_like_unique_together_remove_comment_content_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment", name="content", field=models.TextField(default=""),
        ),
    ]
