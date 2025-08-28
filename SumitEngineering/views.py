from django.shortcuts import render
from store.models import Product

def home(request):
    # Show only one product per category on the home page
    from category.models import category
    categories = category.objects.all()
    products = []
    for cat in categories:
        product = Product.objects.filter(category=cat, is_available=True).order_by('-id').first()
        if product:
            products.append(product)
    # Limit to 8 categories/products if needed
    products = products[:8]
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)