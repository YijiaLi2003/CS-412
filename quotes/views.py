from django.shortcuts import render
import random

# List of quotes and images (already created in the current app)
quotes = [
    "God is dead. God remains dead. And we have killed him.",
    "He who has a why to live can bear almost any how.",
    "That which does not kill us makes us stronger.",
    "To live is to suffer, to survive is to find some meaning in the suffering."

]

images = [
    "https://images.squarespace-cdn.com/content/v1/5ed93e72d9d43b5bb06c8f18/fe0cca27-fc71-4f5c-b3a6-1cdff1feb5a4/steve_af_Nietzsche_confidently_standing_on_hill_active_volcano__a2bab431-88ec-4271-be34-14b128bdd6bb.png",
    "https://m.media-amazon.com/images/I/613ZVoVVeXL._AC_UF1000,1000_QL80_.jpg",
    "https://miro.medium.com/v2/resize:fit:1024/1*eERm8z2JE7VOI6quYvE3AQ.jpeg",
    "https://www.klassik-stiftung.de/assets/media/f/6/csm_Stoeving_Portraet_Nietzsche_f54c8b8b98.jpg"

]

# View to show a random quote and image
def quote(request):
    selected_quote = random.choice(quotes)
    selected_image = random.choice(images)
    context = {'quote': selected_quote, 'image': selected_image}
    return render(request, 'quotes/quote.html', context)

# New view: Show all quotes and images
def show_all(request):
    context = {
        'quotes': quotes,
        'images': images,
    }
    return render(request, 'quotes/show_all.html', context)

# New view: About page with biographical info
def about(request):
    bio = {
        'name': 'Friedrich Nietzsche', 
        'bio': 'Friedrich Wilhelm Nietzsche (15 October 1844 - 25 August 1900) was a German classical scholar, philosopher, and critic of culture, who became one of the most influential of all modern thinkers.',
        'creator': 'Yijia Li',  
        'creator_bio': 'I am Yijia Li, the creator of this web application, a CS student at BU.',
    }
    return render(request, 'quotes/about.html', bio)
