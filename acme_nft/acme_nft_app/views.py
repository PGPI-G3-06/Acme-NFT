from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password, is_password_usable
from django.contrib.auth.models import AnonymousUser, User, UserManager
from django.contrib.sessions.models import Session
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Address, EntryType, Opinion, Product, ProductEntry

# ------------------------------------- Constants -------------------------------------

max_products_per_page = 10

# ------------------------------------- Render views -------------------------------------

def index(request):
    print(request.path)

    if request.path == "/order-by-collections/":
        products = Product.objects.order_by('collection')
    elif request.path == "/order-by-author/":
        products = Product.objects.order_by('author_id')
    else:
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

    # Load products to show in view

    for i in range(page_number*max_products_per_page, page_number*max_products_per_page+max_products_per_page):
        if(i < len(products)):
            products_to_list.append(products[i])

    # Load wishlist to render hearts

    for product in products_to_list:
        for entry in entries:
            if entry.product == product and entry.user==request.user and entry.entry_type == 'WISHLIST':
                wishlist.append(entry.product_id)

    return render(request, "index.html", context={"user": request.user,
                                                "products": products_to_list,
                                                "wishlist": wishlist,
                                                "pages_range": range(0, possible_pages),
                                                "current_page": page_number
                                                }
                )




def signin(request):
    return render(request, "login.html", context={})

def product_detail(request, product_id):
    
    product = get_object_or_404(Product, pk=product_id)

    in_wishlist = False

    for entry in ProductEntry.objects.all():
        if entry.product == product and entry.user==request.user and entry.entry_type == 'WISHLIST':
            in_wishlist = True
            break
    
    comments = Opinion.objects.filter(product=product)

    return render(request, "product_details.html", context={"user": request.user, "product": product, "comments": comments, "in_wishlist": in_wishlist})

def hello(request, user_id):

    user = get_object_or_404(User, pk=user_id)

    return render(request, "hello.html", context={'user': user})

def error(request):
    return render(request, "error.html", context={})

# ------------------------------------- API views -------------------------------------

# ------------------------ Login page ------------------------

def login(request):

    user = authenticate(username=request.POST['username'], password=request.POST['password'])

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect(reverse("acme-nft:index"))
    else:
        return HttpResponseRedirect(reverse("acme-nft:error"))
    
def signout(request):

    auth.logout(request)
    return HttpResponseRedirect(reverse("acme-nft:index"))

def signup(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']

        errors = []
        if username == " " or password == " " or first_name == " " or last_name == " " or email == " ": # Check if any field is empty
            empty = "Todos los campos del formulario deben estar rellenos"
            errors.append(empty)
        if first_name[0].islower():
            first_letter_name = "La primera letra del nombre debe ser mayúscula"
            errors.append(first_letter_name)
        if last_name[0].islower():
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
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "are_errors": are_errors
            })
        else:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
            user.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse("acme-nft:index"))
            
    else:
        return render(request, "login.html")
        
        
def edit_user(request):
    user = User.objects.get(username=request.user)
    if request.method == 'GET':


        return render(request, "profile.html",{
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
    })

    else:

        user_attrs = request.POST
        user.first_name = user_attrs['first_name']
        user.last_name = user_attrs['last_name']
        user.username = user_attrs['username']
        user.email = user_attrs['email']
        user.save()

    return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))


# ------------------------ Address ------------------------

def show_adrress(request, user_id):

    user = User.objects.get(id=user_id)
    list_address = user.address_set.all()
    print(list_address)
    return render(request, "show-address.html", context={"list_address": list_address})

def new_address(request):

    if request.method == "POST":

        errors = []

        street_name = request.POST['street_name']
        number = request.POST['number']
        if request.POST['floor'] == "":
            floor = None
        else:
            floor = request.POST['floor']
        if request.POST['block'] == "":
            block = None
        else:
            block = request.POST['block']
        door = request.POST['door']
        city = request.POST['city']
        code_postal = request.POST['code_postal']

        errors = check_errors(block, city, code_postal, door, errors, floor, number,
                                                         street_name)
        if len(errors) > 0:
            are_errors = True
            return render(request, "new-address.html", {
                "errors": errors,
                "street_name": street_name,
                "number": number,
                "floor": floor,
                "block": block,
                "door": door,
                "city": city,
                "code_postal": code_postal,
                "are_errors": are_errors,
            })
        else:
            user = User.objects.get(id=2)
            address = Address(user_id=user.id, street_name=street_name, number=number, block=block, floor=floor, door=door, city=city, code_postal=code_postal)
            address.save()
            return HttpResponseRedirect(reverse("acme-nft:show-address", args=(user.id,)))
    else:
        return render(request, "new-address.html")

def delete_address(request, address_id):

    address = Address.objects.get(id=address_id)
    address.delete()
    return HttpResponseRedirect(reverse("acme-nft:show-address", args=(2,)))


def update_address(request, address_id):

    if request.method == "POST":

        address = Address.objects.get(id=address_id)

        errors = []

        street_name = request.POST['street_name']
        number = request.POST['number']
        if request.POST['floor'] == "":
            floor = None
        else:
            floor = request.POST['floor']
        if request.POST['block'] == "":
            block = None
        else:
            block = request.POST['block']
        door = request.POST['door']
        city = request.POST['city']
        code_postal = request.POST['code_postal']

        errors = check_errors(block, city, code_postal, door, errors, floor, number,
                                                         street_name)
        if len(errors) > 0:
            are_errors = True
            return render(request, "new-address.html", {
                "errors": errors,
                "street_name": street_name,
                "number": number,
                "floor": floor,
                "block": block,
                "door": door,
                "city": city,
                "code_postal": code_postal,
                "are_errors": are_errors,
            })
        else:
            address.street_name = street_name
            address.number = number
            address.floor = floor
            address.block = block
            address.door = door
            address.city = city
            address.code_postal = code_postal
            address.save()
            return HttpResponseRedirect(reverse("acme-nft:show-address", args=(2,)))
    else:
        address = Address.objects.get(id=address_id)
        street_name = address.street_name
        number = address.number
        floor = address.floor
        if floor == None:
            floor = ""
        block = address.block
        if block == None:
            block = ""
        door = address.door
        if door == None:
            door = ""
        city = address.city
        code_postal = address.code_postal
        id = address.id

        return render(request, "update-address.html", {
                      "street_name": street_name,
                      "number": number,
                      "floor": floor,
                        "block": block,
                        "door": door,
                        "city": city,
                        "code_postal": code_postal,
                        "id": id,})


def check_errors(block, city, code_postal, door, errors, floor, number, street_name):
    if len(street_name) > 60:
        street_name_length = "El nombre de la calle no puede tener más de 60 caracteres"
        errors.append(street_name_length)
    if len(door) > 1:
        door_length = "La puerta no puede tener más de 1 caracter"
        errors.append(door_length)
    if code_postal.isdigit() == False:
        code_postal_digit = "El código postal debe ser un número"
        errors.append(code_postal_digit)
    else:
        code_postal = int(code_postal)
    if block != None:
        if block.isdigit() == False:
            block_digit = "El bloque debe ser un número"
            errors.append(block_digit)
        else:
            block = int(block)
    if floor != None:
        if floor.isdigit() == False:
            floor_digit = "El piso debe ser un número"
            errors.append(floor_digit)
        else:
            floor = int(floor)
    if number != None:
        if number.isdigit() == False:
            number_digit = "El número debe ser un número"
            errors.append(number_digit)
        else:
            number = int(number)
    if len(city) > 60:
        city_length = "El nombre de la ciudad no puede tener más de 60 caracteres"
        errors.append(city_length)
    return errors

# -------------------------- Cart --------------------------

def add_to_cart(request, product_id):
    
    quantity = int(request.POST['quantity'])
    
    if quantity > 0:
        user = request.user
        
        if not user.is_authenticated:
            user = None
        product = Product.objects.get(id=product_id)
        try:
            entry = ProductEntry.objects.get(product=product, entry_type='CART', user=user)
            entry.quantity = entry.quantity + quantity
        except:
            entry = ProductEntry(product=product, entry_type='CART', user=user, quantity=quantity)
        entry.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseNotFound("Invalid Quantity")

# ------------------------ Wishlist ------------------------

def add_to_wishlist(request, product_id):

    try: 
        user = request.user
        product = Product.objects.get(pk=product_id)
        entry = ProductEntry.objects.get(product=product, entry_type='WISHLIST', user=user)
        entry.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
    
        product = get_object_or_404(Product, pk=product_id)
        user = request.user
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
