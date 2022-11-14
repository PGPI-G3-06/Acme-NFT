from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse


from acme_nft_app.models import User, Product, ProductEntry, EntryType, Opinion

# ------------------------------------- Constants -------------------------------------

max_products_per_page = 10

# ------------------------------------- Render views -------------------------------------

def index(request):

    products = Product.objects.all()
    entries = ProductEntry.objects.all()
    products_to_list = []
    wishlist = []

    try:
        page_number = int(request.GET['page'])
    except:
        page_number = 0
    
    if len(products) % max_products_per_page == 0:
        possible_pages = int(len(products) / max_products_per_page)
    else:
        possible_pages = int(len(products) / max_products_per_page) + 1
        
    try:
        user = User.objects.get(User, pk=1)
    except:
        user = User(username="anonymous")

    # Load products to show in view

    for i in range(page_number*max_products_per_page, page_number*max_products_per_page+max_products_per_page):
        if(i < len(products)):
            products_to_list.append(products[i])

    # Load wishlist to render hearts

    for product in products_to_list:
        for entry in entries:
            if entry.product == product and entry.user==user and entry.entry_type == 'WISHLIST':
                wishlist.append(entry.product_id)

    return render(request, "index.html", context={"user": user,
                                                "products": products_to_list,
                                                "wishlist": wishlist,
                                                "pages_range": range(0, possible_pages),
                                                "current_page": page_number
                                                }
                )

def login_page(request):
    return render(request, "login.html", context={})

def product_detail(request, product_id):
    
    product = get_object_or_404(Product, pk=product_id)
    try:
        user = get_object_or_404(User, pk=1)
    except:
        user = User(username="anonymous")

    in_wishlist = False

    for entry in ProductEntry.objects.all():
        if entry.product == product and entry.user==user and entry.entry_type == 'WISHLIST':
            in_wishlist = True
            break
    
    comments = Opinion.objects.filter(product=product)

    return render(request, "product_details.html", context={"user": user, "product": product, "comments": comments, "in_wishlist": in_wishlist})

def hello(request, user_id):

    user = get_object_or_404(User, pk=user_id)

    return render(request, "hello.html", context={'user': user})

def error(request):
    return render(request, "error.html", context={})

# ------------------------------------- API views -------------------------------------

# ------------------------ Login page ------------------------

def login(request):

    try:
        user = User.objects.get(email=request.POST['email'])

        if check_password(request.POST['password'], user.password):
            return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))
        else:
            return HttpResponseRedirect(reverse("acme-nft:error"))
    except:
        return HttpResponseRedirect(reverse("acme-nft:error"))

def register(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']

        errors = []
        if username == " " or password == " " or name == " " or surname == " " or email == " ": # Check if any field is empty
            empty = "Todos los campos del formulario deben estar rellenos"
            errors.append(empty)
        if name[0].islower():
            first_letter_name = "La primera letra del nombre debe ser mayúscula"
            errors.append(first_letter_name)
        if surname[0].islower():
            first_letter_surname = "La primera letra del apellido debe ser mayúscula"
            errors.append(first_letter_surname)
        if len(password) < 8:
            password_length = "La contraseña debe tener al menos 8 caracteres"
            errors.append(password_length)
        if len(username) < 4:
            username_length = "El nombre de usuario debe tener al menos 4 caracteres"
            errors.append(username_length)
        for user in User.objects.all():
            if user.username == username:
                username_exists = "El nombre de usuario ya existe"
                errors.append(username_exists)
            if user.email == email:
                email_exists = "El email ya existe"
                errors.append(email_exists)
        if len(errors) > 0:
            are_errors = True
            return render(request, "login.html", {
                "errors": errors,
                "username": username,
                "password": password,
                "name": name,
                "surname": surname,
                "email": email,
                "are_errors": are_errors
            })
        else:
            user = User(username=username, password=make_password(password), name=name, surname=surname, email=email)
            user.save()
            print(user.id)
            return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))
            
    else:
        return render(request, "login.html")

# ------------------------ Wishlist ------------------------

def add_to_wishlist(request, product_id):

    try: 
        user = User.objects.get(pk=1) # This will be the logged user
        product = Product.objects.get(pk=product_id)
        entry = ProductEntry.objects.get(product=product, entry_type='WISHLIST', user=user)
        entry.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
    
        product = get_object_or_404(Product, pk=product_id)
        user = get_object_or_404(User, pk=1)
        entry = ProductEntry(quantity=None, entry_type='WISHLIST', product=product, user=user)
        entry.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# ------------------------ Comments ------------------------

def add_comment(request, product_id):
    
    if request.method == "POST":

        user = User.objects.get(pk=1)
        product = Product.objects.get(pk=product_id)
        
        comment_text = request.POST['comment']
        
        comment = Opinion(text=comment_text, product=product, user=user)
        comment.save()
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        