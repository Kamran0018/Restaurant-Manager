from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Category, MenuItem, Cart, Order, OrderItem, ContactMessage

# -------------------------
# SIGNUP USER
# -------------------------
def signup_user(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        # Password check
        if password != password2:
            return render(request, "website/signup.html", {
                "error": "Passwords do not match"
            })

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        return redirect('login')

    return render(request, "website/signup.html")


# -------------------------
# LOGIN USER
# -------------------------
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('/')

    return render(request, "website/login.html")


# -------------------------
# LOGOUT USER
# -------------------------
def logout_user(request):
    logout(request)
    return redirect('/login/')


# ------------------------------
# Home Page → Show Categories
# ------------------------------
def home(request):
    categories = Category.objects.all()
    return render(request, 'website/home.html', {'categories': categories})


# ------------------------------
# Menu → Show Food Items
# ------------------------------
def menu_items(request, category_id):
    items = MenuItem.objects.filter(category_id=category_id, is_available=True)
    return render(request, 'website/menu_items.html', {'items': items})


# ------------------------------
# Add To Cart
# ------------------------------
@login_required
def add_to_cart(request, item_id):
    item = MenuItem.objects.get(id=item_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        item=item,
    )

    if not created:
        cart_item.quantity += 1  
    cart_item.save()

    messages.success(request, "Item added to cart!")
    return redirect('view_cart')


# ------------------------------
# View Cart
# ------------------------------
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(i.item.price * i.quantity for i in cart_items)

    return render(request, 'website/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


# ------------------------------
# Remove Item From Cart
# ------------------------------
@login_required
def remove_from_cart(request, cart_id):
    Cart.objects.get(id=cart_id, user=request.user).delete()
    return redirect('view_cart')


# ------------------------------
# Place Order
# ------------------------------
@login_required
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    total = sum(i.item.price * i.quantity for i in cart_items)

    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        status="Pending",
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            item=cart_item.item,
            quantity=cart_item.quantity,
            price=cart_item.item.price,
        )

    cart_items.delete()

    messages.success(request, "Order placed successfully!")
    return redirect('home')


# ------------------------------
# Contact Form Save
# ------------------------------
def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            message=request.POST['message']
        )
        messages.success(request, "Thank you! We will contact you soon.")
        return redirect('contact')

    return render(request, 'website/contact.html')


# ------------------------------
# User Profile
# ------------------------------
@login_required
def profile(request):
    return render(request, 'website/profile.html')
