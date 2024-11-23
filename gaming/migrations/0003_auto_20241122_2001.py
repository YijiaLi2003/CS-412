from django.db import migrations
from datetime import datetime

def add_games(apps, schema_editor):
    Genre = apps.get_model('gaming', 'Genre')
    Game = apps.get_model('gaming', 'Game')
    
    # Helper function to get Genre object by name
    def get_genre(name):
        try:
            return Genre.objects.get(name=name)
        except Genre.DoesNotExist:
            return Genre.objects.create(name=name)
    
    games = [
        {
            "title": "Braid, Anniversary Edition",
            "platform": "PC, Xbox 360, PlayStation 3, PlayStation 4, Nintendo Switch, macOS, Linux",
            "genre": "Puzzle",
            "release_date": datetime.strptime("2014-01-01", "%Y-%m-%d").date(),
            "developer": "Jonathan Blow",
            "publisher": "Microsoft Studios",
        },
        {
            "title": "Celeste",
            "platform": "PC, Xbox One, PlayStation 4, Nintendo Switch",
            "genre": "Platformer",
            "release_date": datetime.strptime("2018-01-25", "%Y-%m-%d").date(),
            "developer": "Matt Makes Games",
            "publisher": "Matt Makes Games",
        },
        {
            "title": "Outer Wilds",
            "platform": "PC, Xbox One, PlayStation 4, Nintendo Switch",
            "genre": "Adventure",
            "release_date": datetime.strptime("2020-05-28", "%Y-%m-%d").date(),
            "developer": "Mobius Digital",
            "publisher": "Annapurna Interactive",
        },
        {
            "title": "Portal 2",
            "platform": "PC, Mac, Linux, Xbox 360, PlayStation 3",
            "genre": "Puzzle",
            "release_date": datetime.strptime("2011-04-19", "%Y-%m-%d").date(),
            "developer": "Valve Corporation",
            "publisher": "Valve Corporation",
        },
        {
            "title": "Undertale",
            "platform": "PC, macOS, Linux, PlayStation 4, PlayStation Vita, Nintendo Switch, Xbox One",
            "genre": "RPG",
            "release_date": datetime.strptime("2015-09-15", "%Y-%m-%d").date(),
            "developer": "Toby Fox",
            "publisher": "Toby Fox",
        },
        {
            "title": "What Remains of Edith Finch",
            "platform": "PC, PlayStation 4, Xbox One, Nintendo Switch",
            "genre": "Adventure",
            "release_date": datetime.strptime("2017-04-25", "%Y-%m-%d").date(),
            "developer": "Giant Sparrow",
            "publisher": "Annapurna Interactive",
        },
        {
            "title": "The Witness",
            "platform": "PC, PlayStation 4, Xbox One, Nintendo Switch",
            "genre": "Puzzle",
            "release_date": datetime.strptime("2016-01-26", "%Y-%m-%d").date(),
            "developer": "Thekla, Inc.",
            "publisher": "Thekla, Inc.",
        },
        {
            "title": "It Takes Two",
            "platform": "PC, PlayStation 4, PlayStation 5, Xbox One, Xbox Series X/S",
            "genre": "Action-adventure",
            "release_date": datetime.strptime("2021-03-26", "%Y-%m-%d").date(),
            "developer": "Hazelight Studios",
            "publisher": "Electronic Arts",
        },
        {
            "title": "BioShock Remastered",
            "platform": "PC, PlayStation 4, Xbox One",
            "genre": "First-person shooter",
            "release_date": datetime.strptime("2016-08-25", "%Y-%m-%d").date(),
            "developer": "Irrational Games",
            "publisher": "2K Games",
        },
        {
            "title": "Cuphead",
            "platform": "PC, Xbox One, Nintendo Switch, macOS",
            "genre": "Platformer",
            "release_date": datetime.strptime("2017-09-29", "%Y-%m-%d").date(),
            "developer": "Studio MDHR",
            "publisher": "Studio MDHR",
        },
        {
            "title": "DARK SOULS™: REMASTERED",
            "platform": "PC, PlayStation 4, Xbox One",
            "genre": "Action RPG",
            "release_date": datetime.strptime("2018-05-25", "%Y-%m-%d").date(),
            "developer": "FromSoftware",
            "publisher": "Bandai Namco Entertainment",
        },
        {
            "title": "DEATH STRANDING DIRECTOR'S CUT",
            "platform": "PC, PlayStation 5",
            "genre": "Survival",
            "release_date": datetime.strptime("2022-09-24", "%Y-%m-%d").date(),
            "developer": "Kojima Productions",
            "publisher": "Sony Interactive Entertainment",
        },
        {
            "title": "Divinity: Original Sin 2",
            "platform": "PC, macOS, Linux, PlayStation 4, Xbox One, Nintendo Switch",
            "genre": "RPG",
            "release_date": datetime.strptime("2017-09-14", "%Y-%m-%d").date(),
            "developer": "Larian Studios",
            "publisher": "Larian Studios",
        },
        {
            "title": "God of War",
            "platform": "PlayStation 4, PC",
            "genre": "Action-adventure",
            "release_date": datetime.strptime("2018-04-20", "%Y-%m-%d").date(),
            "developer": "Santa Monica Studio",
            "publisher": "Sony Interactive Entertainment",
        },
        {
            "title": "Grand Theft Auto V",
            "platform": "PC, PlayStation 3, PlayStation 4, PlayStation 5, Xbox 360, Xbox One, Xbox Series X/S",
            "genre": "Action-adventure",
            "release_date": datetime.strptime("2013-09-17", "%Y-%m-%d").date(),
            "developer": "Rockstar North",
            "publisher": "Rockstar Games",
        },
        {
            "title": "Half-Life: Alyx",
            "platform": "PC (VR)",
            "genre": "First-person shooter",
            "release_date": datetime.strptime("2020-03-23", "%Y-%m-%d").date(),
            "developer": "Valve Corporation",
            "publisher": "Valve Corporation",
        },
        {
            "title": "Hellblade: Senua's Sacrifice",
            "platform": "PC, PlayStation 4, Xbox One, Nintendo Switch",
            "genre": "Action-adventure",
            "release_date": datetime.strptime("2017-08-08", "%Y-%m-%d").date(),
            "developer": "Ninja Theory",
            "publisher": "Ninja Theory",
        },
        {
            "title": "INSIDE",
            "platform": "PC, PlayStation 4, Xbox One, Nintendo Switch",
            "genre": "Puzzle",
            "release_date": datetime.strptime("2016-06-29", "%Y-%m-%d").date(),
            "developer": "Playdead",
            "publisher": "Playdead",
        },
        {
            "title": "The Last of Us™ Part I",
            "platform": "PlayStation 5, PC",
            "genre": "Action-adventure",
            "release_date": datetime.strptime("2022-09-02", "%Y-%m-%d").date(),
            "developer": "Naughty Dog",
            "publisher": "Sony Interactive Entertainment",
        },
        {
            "title": "Red Dead Redemption 2",
            "platform": "PC, PlayStation 4, Xbox One, Stadia",
            "genre": "Action-adventure",
            "release_date": datetime.strptime("2018-10-26", "%Y-%m-%d").date(),
            "developer": "Rockstar Games Red Dead Studios",
            "publisher": "Rockstar Games",
        },
        {
            "title": "Terraria",
            "platform": "PC, PlayStation 4, PlayStation 3, PlayStation Vita, Xbox 360, Xbox One, Nintendo Switch, iOS, Android, macOS, Linux",
            "genre": "Sandbox",
            "release_date": datetime.strptime("2011-05-16", "%Y-%m-%d").date(),
            "developer": "Re-Logic",
            "publisher": "Re-Logic",
        },
    ]
    
    for game_data in games:
        genre = get_genre(game_data["genre"])
        Game.objects.create(
            title=game_data["title"],
            platform=game_data["platform"],
            genre=genre,
            release_date=game_data["release_date"],
            developer=game_data["developer"],
            publisher=game_data["publisher"],
        )

class Migration(migrations.Migration):

    dependencies = [
        ('gaming', '0002_auto_20241122_1945'),  
    ]

    operations = [
        migrations.RunPython(add_games),
    ]
