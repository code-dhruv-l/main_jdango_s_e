from django.shortcuts import render
from .form import Registrationform
from .models import Account
from django.contrib import messages as messages ,auth
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#varification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator as account_activation_token
from django.core.mail import EmailMessage


from cart.views import _cart_id
from cart.models import Cart, CartItem
import requests





# Create your views here.

def register(request):
    if request.method == 'POST':
        form = Registrationform(request.POST)
        if form.is_valid():
            # Process the form data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]  # Use email prefix as username
            phone_number = form.cleaned_data['phone_number']

            user =Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                username=username,
            )
            user.phone_number = phone_number
            user.save()

            # User activation
            currect_site = get_current_site(request)
            mail_suject = "Plaese Activate Your Account"
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': currect_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(
                mail_suject,
                message,
                from_email='Sumit Engineering & Food Processing Machinery <limbasiyadhruv735@gmail.com>', 
                to=[to_email]
            )
            send_email.send()

            # messages.success(request, "Thank You for registering with us. A verification email has been sent to your email address. Please check your inbox and click on the activation link to activate your account.")
            return redirect('/accounts/login/?command=verification&email=' + user.email)  # Redirect to a success page or login page
    else:
        form = Registrationform()

    context = {
            'form': form,
        }    
    # Registration logic here
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, username=email, password=password)

        if user is not None:
            # --- Merge anonymous cart into logged-in cart ---
            session_cart_id = _cart_id(request)
            if session_cart_id:
                try:
                    anon_cart = Cart.objects.get(cart_id=session_cart_id)
                except Cart.DoesNotExist:
                    anon_cart = None

                if anon_cart:
                    # Get or create the real cart for this user
                    user_cart, _ = Cart.objects.get_or_create(user=user)

                    for anon_item in anon_cart.cartitem_set.all():
                        # Merge quantities if the item already exists for this user
                        user_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=anon_item.product,
                            defaults={'quantity': anon_item.quantity, 'user': user}
                        )
                        if not created:
                            user_item.quantity += anon_item.quantity
                            user_item.save()

                    # Clean up
                    anon_cart.delete()
                    # Optionally drop the session key as well
                    if 'cart_id' in request.session:
                        del request.session['cart_id']

            auth.login(request, user)
            messages.success(request, "You have logged in successfully.")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'accounts/login.html')



@login_required(login_url='login')
def logout(request):
    # Logout logic here
    auth.logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated successfully.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid.")
        return redirect('register')
    

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')   



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            # User activation
            currect_site = get_current_site(request)
            mail_suject = "Reset Your Password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': currect_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_suject, message, to=[to_email])
            send_email.send()
            messages.success(request, "A password reset email has been sent to your email address. Please check your inbox and follow the instructions.")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist.")  
            return redirect('forgot_password')  
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password.")
        return redirect('reset_password')
    else:
        messages.error(request, "This link has expired.")
        return redirect('login')    
    

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Your password has been reset successfully. You can now log in with your new password.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match. Please try again.")
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')