# restaurant/views.py
from django.shortcuts import render
import random
import datetime
from django.utils import timezone 

def main(request):
    return render(request, 'restaurant/main.html')

def order(request):
    daily_specials = [
        {'name': 'Spaghetti Carbonara', 'price': 12.99},
        {'name': 'Grilled Salmon', 'price': 15.99},
        {'name': 'Chicken Alfredo', 'price': 11.99},
        {'name': 'Veggie Stir-fry', 'price': 9.99},
    ]
    daily_special = random.choice(daily_specials)
    context = {'daily_special': daily_special}
    return render(request, 'restaurant/order.html', context)

def confirmation(request):
    if request.method == 'POST':
        items = request.POST.getlist('items')
        toppings = request.POST.getlist('toppings')
        instructions = request.POST.get('instructions', '')
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email')

        total_price = 0.0
        ordered_items = []
        for item in items:
            name, price = item.split('|')
            price = float(price)
            ordered_items.append({'name': name, 'price': price})
            total_price += price

        toppings_price = len(toppings) * 1.00  
        if toppings_price > 0:
            ordered_items.append({'name': 'Toppings', 'price': toppings_price})
            total_price += toppings_price

        minutes = random.randint(30, 60)
        ready_time = timezone.localtime() + datetime.timedelta(minutes=minutes)
        ready_time_formatted = ready_time.strftime('%I:%M %p')

        context = {
            'ordered_items': ordered_items,
            'total_price': total_price,
            'instructions': instructions,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'ready_time': ready_time_formatted,
        }
        return render(request, 'restaurant/confirmation.html', context)
    else:
        return render(request, 'restaurant/order.html')