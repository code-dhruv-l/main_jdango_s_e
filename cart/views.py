from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product  # Correct import for Product
from .models import Cart, CartItem  # Import your Cart and CartItem models
from django.contrib.auth.decorators import login_required  # Import login_required if needed


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key  # Get the session key for the cart
    if not cart:
        cart = request.session.create()  # Create a new session if it doesn't exist
    return cart
    

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # 1. Identify the cart owner
    if request.user.is_authenticated:
        # logged-in user → store on the User
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        # anonymous user → store on the session
        cart_id = _cart_id(request)
        cart, _ = Cart.objects.get_or_create(cart_id=cart_id)

    # 2. Add / update the item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': 1,
            'user': request.user if request.user.is_authenticated else None
        }
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # 1. get the right cart (user-based or session-based)
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = _cart_id(request)
        cart, _ = Cart.objects.get_or_create(cart_id=cart_id)

    # 2. find the item
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    # 3. decrement or delete
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # 1. find the cart (user or session)
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

    # 2. find & delete the item
    CartItem.objects.filter(cart=cart, product=product).delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    cart_item =[]
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))  # Get the cart by ID
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # Get active cart items
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax =(2 * total) / 100  # Calculate tax (2% of total)
        grand_total = total + tax + 10  # Add shipping cost of $10
    except Cart.DoesNotExist:
        pass 


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }            
    return render(request, 'store/cart.html', context)  # Adjust the template path as



@login_required(login_url='login')  # Use this decorator if you want to restrict access to logged-in users
def checkout(request, total=0, quantity=0, cart_items=None): 
    tax = 0
    grand_total = 0
    cart_item =[]
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))  # Get the cart by ID
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # Get active cart items
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax =(2 * total) / 100  # Calculate tax (2% of total)
        grand_total = total + tax + 10  # Add shipping cost of $10
    except Cart.DoesNotExist:
        pass 


    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }  

    return render(request, 'store/checkout.html',context )