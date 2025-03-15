from django.shortcuts import render
from orders.models import MenuItem, Category

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms(request):
    return render(request, 'terms.html')

def contacts_view(request):
    return render(request, 'contacts.html')

def menu(request):
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    menu_data = {}

    for category in categories:
        if query:
            items = MenuItem.objects.filter(category=category, name__icontains=query, is_available=True)
        else:
            items = MenuItem.objects.filter(category=category, is_available=True)
        if items.exists():
            menu_data[category] = items

    context = {
        'menu_data': menu_data,
        'query': query,
    }
    return render(request, 'menu.html', context)
