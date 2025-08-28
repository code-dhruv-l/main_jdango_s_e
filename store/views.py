from django.shortcuts import render
from .models import Product  # Adjust the import based on your actual model name
from django.shortcuts import get_object_or_404
from category.models import category  # Assuming you have a category model
from cart.views import _cart_id
from cart.models import CartItem  # Assuming you have a CartItem model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q  # For complex queries
from django.db.models import Max
from django.contrib import messages
from .models import UserMessage  # Assuming you have a UserMessage model
from django.shortcuts import redirect
from .models import PriceInquiry  # Assuming you have a PriceInquiry model
from .models import ReviewRating  # Assuming you have a ReviewRating model
from .forms import ReviewForm  # Assuming you have a ReviewForm defined in forms.py


# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('-id')
        total_products = products.count()
    else:
        from django.db.models import Max
        latest_per_category = (
            Product.objects
            .filter(is_available=True)
            .values('category')
            .annotate(latest_id=Max('id'))
        )
        latest_ids = [item['latest_id'] for item in latest_per_category]
        products = Product.objects.filter(id__in=latest_ids).order_by('-id')
        total_products = products.count()

    # Pagination
    paginator = Paginator(products, 9)
    page = request.GET.get('page', 1)
    try:
        paged_products = paginator.page(page)
    except PageNotAnInteger:
        paged_products = paginator.page(1)
    except EmptyPage:
        paged_products = paginator.page(paginator.num_pages)

    context = {
        'products': paged_products,
        'product_count': len(paged_products),
        'total_products': total_products,
    }
    return render(request, 'store/store.html', context)




def home(request):
    # Get the latest product ID per category
    latest_per_category = (
        Product.objects
        .filter(is_available=True)
        .values('category')
        .annotate(latest_id=Max('id'))
    )

    # Get only the latest product IDs (one per category)
    latest_ids = [item['latest_id'] for item in latest_per_category]

    # Limit to only 8 products max
    products = Product.objects.filter(id__in=latest_ids, is_available=True).order_by('-id')[:8]

    context = {
        'products': products,
    }
    return render(request, 'home.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug, is_available=True)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    #get the reviews for the product 
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)


    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'reviews': reviews,  
    }       
    return render(request, 'store/product_detail.html', context)  # Adjust the template path as necessary


def search(request):
    products = []
    total_products = 0
    keyword = ''
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            total_products = products.count()

    # Pagination
    paginator = Paginator(products, 9)  # Show 9 products per page
    page = request.GET.get('page', 1)
    try:
        paged_products = paginator.page(page)
    except PageNotAnInteger:
        paged_products = paginator.page(1)
    except EmptyPage:
        paged_products = paginator.page(paginator.num_pages)

    context = {
        'products': paged_products,
        'product_count': len(paged_products),
        'total_products': total_products,
        'keyword': keyword,  # Add keyword to context
    }        
    return render(request, 'store/store.html', context) # Adjust the template path as necessary




def submit_message(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        message_text = request.POST.get('message')
        if name and message_text:
            UserMessage.objects.create(name=name, message=message_text)
            messages.success(request, "Your message has been submitted successfully.")
        else:
            messages.error(request, "Both name and message are required.")
    return redirect(request.META.get('HTTP_REFERER', '/')+ '#footer-form')



from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from .models import PriceInquiry  # Make sure this model exists and is imported

def submit_price_inquiry(request):
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        requirement = request.POST.get('requirement')

        if purpose and requirement:
            # Save to database
            inquiry = PriceInquiry.objects.create(purpose=purpose, requirement=requirement)

            # Email details
            subject = "New Price Inquiry"
            message = f"Purpose: {purpose}\nRequirement: {requirement}"
            recipient_list = ['limbasiyadhruv735@gmail.com']  # Replace with your email

            try:
                send_mail(subject, message, 'limbasiyadhruv735@gmail.com', recipient_list)
            except Exception as e:
                print("Email error:", e)

            messages.success(request, "Thank you! Your requirement was submitted.")
        else:
            messages.error(request, "Please fill all fields.")

        return redirect(request.META.get('HTTP_REFERER', '/'))


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, "Your review has been updated successfully.")
            else:
                messages.error(request, "Review update failed. Please check your input.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Your review has been submitted successfully.")
            else:
                messages.error(request, "Review submission failed. Please check your input.")
            return redirect(url)

    
