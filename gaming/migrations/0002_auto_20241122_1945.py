from django.db import migrations

def populate_genres(apps, schema_editor):
    Genre = apps.get_model('gaming', 'Genre')
    genre_list = [
        "Adventure",
        "Action",
        "Sports",
        "Simulation",
        "Platformer",
        "RPG",
        "First-person shooter",
        "Action-adventure",
        "Fighting",
        "Real-time strategy",
        "Racing",
        "Shooter",
        "Puzzle",
        "Casual",
        "Strategy game",
        "Massively multiplayer online role-playing",
        "Stealth",
        "Party",
        "Action RPG",
        "Tactical role-playing",
        "Survival",
        "Battle Royale",
    ]
    for genre_name in genre_list:
        Genre.objects.get_or_create(name=genre_name)

class Migration(migrations.Migration):

    dependencies = [
        ('gaming', '0001_initial'),  # Ensure this matches your last migration file
    ]

    operations = [
        migrations.RunPython(populate_genres),
    ]
