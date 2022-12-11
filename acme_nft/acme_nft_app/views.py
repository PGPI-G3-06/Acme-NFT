import os.path
import string
import random
from datetime import datetime
from django.contrib import auth, messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseNotFound, HttpResponseRedirect, \
    HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import ast
import braintree

from io import BytesIO, StringIO
from django.template.loader import get_template
from django.views.generic import ListView, CreateView, DetailView
from xhtml2pdf import pisa

from acme_nft import settings as django_settings
from django.core.mail import EmailMessage

from django.db.models import ImageField
from .models import *

gateway = braintree.BraintreeGateway(
    braintree.Configuration.configure(
        environment=braintree.Environment.Sandbox,
        merchant_id=django_settings.BRAINTREE_MERCHANT_ID,
        public_key=django_settings.BRAINTREE_PUBLIC_KEY,
        private_key=django_settings.BRAINTREE_PRIVATE_KEY
    )
)

# ------------------------------------- Constants -------------------------------------

MAX_PRODUCTS_PER_PAGE = 10
PROFILE_ERRORS = {}
ADDRESS_ERRORS = {}


# ------------------------------------- Render views -------------------------------------

def index(request):
    products = Product.objects.all()
    
    try:
        if str(request.GET['collection']):
            products = products.filter(collection=str(request.GET['collection']).strip())

    except KeyError:
        pass
    
    try:
        if str(request.GET['order-by']).strip() == 'collection':
            products = products.order_by('collection')

    except KeyError:
        pass
    
    try:
        if str(request.GET['order-by']).strip() == 'author':
            products = products.order_by('author__name')

    except KeyError:
        pass

    try:
        search_param = str(request.GET['buscar']).strip()
        if search_param != '':
            products = products.filter(
                name__icontains=search_param) | products.filter(
                collection__icontains=search_param) | products.filter(
                author__name__icontains=search_param)
        else:
            return HttpResponseRedirect(reverse('acme-nft:index'))

    except KeyError:
        pass

    entries = ProductEntry.objects.all()
    products_to_list = []
    wishlist = []

    try:
        page_number = int(str(request.GET['page']).strip())
    except KeyError:
        page_number = 0

    if len(products) % MAX_PRODUCTS_PER_PAGE == 0:
        possible_pages = int(len(products) / MAX_PRODUCTS_PER_PAGE)
    else:
        possible_pages = int(len(products) / MAX_PRODUCTS_PER_PAGE) + 1

    # Load products to show in view

    for i in range(page_number * MAX_PRODUCTS_PER_PAGE,
                   page_number * MAX_PRODUCTS_PER_PAGE + MAX_PRODUCTS_PER_PAGE):
        if i < len(products):
            products_to_list.append(products[i])

    # Load wishlist to render hearts

    for product in products_to_list:
        for entry in entries:
            if entry.product == product and entry.user == request.user and entry.entry_type == 'WISHLIST':
                wishlist.append(entry.product_id)
                
    showcase_products = Product.objects.filter(showcase=True)
    
    # Load collections
    
    collections = Product.objects.values('collection').distinct()

    return render(request, "index.html", context={"user": request.user,
                                                  "products": products_to_list,
                                                  "showcase_products": showcase_products,
                                                  "wishlist": wishlist,
                                                  "pages_range": range(0,
                                                                       possible_pages),
                                                  "current_page": page_number,
                                                  "needs_pagination": possible_pages > 1,
                                                  "collections": collections,
                                                  }
                  )


def signin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("acme-nft:index"))
    else:
        return render(request, "login.html", context={"is_signin": True})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    in_wishlist = False

    for entry in ProductEntry.objects.all():
        if entry.product == product and entry.user == request.user and entry.entry_type == 'WISHLIST':
            in_wishlist = True
            break

    comments = Comment.objects.filter(product=product)

    return render(request, "product_details.html",
                  context={"user": request.user, "product": product,
                           "suggested_products": None,
                           "comments": comments, "in_wishlist": in_wishlist})


def wishlist(request):
    if not request.user.is_authenticated:
        return is_authenticated(request)

    products = Product.objects.filter(productentry__user=request.user, productentry__entry_type='WISHLIST').distinct()
    products_to_list = []

    if not products:
        messages.error(request, 'No hay productos en la lista de deseos')
        return HttpResponseRedirect(reverse("acme-nft:index"))

    try:
        page_number = int(request.GET['page'])
    except KeyError:
        page_number = 0

    if len(products) % MAX_PRODUCTS_PER_PAGE == 0:
        possible_pages = int(len(products) / MAX_PRODUCTS_PER_PAGE)
    else:
        possible_pages = int(len(products) / MAX_PRODUCTS_PER_PAGE) + 1

    for i in range(page_number * MAX_PRODUCTS_PER_PAGE,
                   page_number * MAX_PRODUCTS_PER_PAGE + MAX_PRODUCTS_PER_PAGE):
        if i < len(products):
            products_to_list.append(products[i])

    return render(request, "wishlist.html", context={"user": request.user,
                                                     "products": products_to_list,
                                                     "total": len(products),
                                                     "wishlist": products_to_list,
                                                     "pages_range": range(0,
                                                                          possible_pages),
                                                     "current_page": page_number,
                                                     "needs_pagination": possible_pages > 1,
                                                     }
                  )


# ------------------------------------- API views -------------------------------------

# ------------------------ Login page ------------------------

def is_authenticated(request):  
    messages.error(request, "Debes estar registrado para acceder a esta página")
    return HttpResponseRedirect(reverse("acme-nft:signup"))

def login(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect(reverse("acme-nft:index"))
    else:
        messages.error(request, "Usuario o contraseña incorrectos")
        return HttpResponseRedirect(reverse("acme-nft:signin"))


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
        if username == " " or password == " " or first_name == " " or last_name == " " or email == " ":  # Check if any field is empty
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
            user = User.objects.create_user(username=username,
                                            password=password,
                                            first_name=first_name,
                                            last_name=last_name, email=email)
            user.save()
            ProfilePicture.objects.create(user=user)
            auth.login(request, user)
            return HttpResponseRedirect(reverse("acme-nft:index"))

    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("acme-nft:index"))
        else:
            return render(request, "login.html")


def edit_user(request):
    
    if not request.user.is_authenticated:
        return is_authenticated(request)
    
    user = User.objects.get(username=request.user)
    profile_picture, _ = ProfilePicture.objects.get_or_create(user=user)
    
    name_errors = PROFILE_ERRORS[user.username+'name_errors'] if PROFILE_ERRORS and PROFILE_ERRORS[user.username+'name_errors'] else []
    surname_errors = PROFILE_ERRORS[user.username+'surname_errors'] if PROFILE_ERRORS and PROFILE_ERRORS[user.username+'surname_errors'] else []
    username_errors = PROFILE_ERRORS[user.username+'username_errors'] if PROFILE_ERRORS and PROFILE_ERRORS[user.username+'username_errors'] else []
    email_errors = PROFILE_ERRORS[user.username+'email_errors'] if PROFILE_ERRORS and PROFILE_ERRORS[user.username+'email_errors'] else []
    profile_pic_errors = PROFILE_ERRORS[user.username+'profile_pic_errors'] if PROFILE_ERRORS and PROFILE_ERRORS[user.username+'profile_pic_errors'] else []
    
    if request.method == 'GET':
        first_name = user.first_name
        surname = user.last_name
        username = user.username
        email = user.email
        profile_picture = str(profile_picture.image)
        
        if PROFILE_ERRORS:
            first_name= PROFILE_ERRORS[user.username+'name']
            surname = PROFILE_ERRORS[user.username+'surname']
            username = PROFILE_ERRORS[user.username+'username']
            email = PROFILE_ERRORS[user.username+'email']
            profile_picture = PROFILE_ERRORS[user.username+'profile_pic']
            
            del PROFILE_ERRORS[user.username+'name']
            del PROFILE_ERRORS[user.username+'surname']
            del PROFILE_ERRORS[user.username+'username']
            del PROFILE_ERRORS[user.username+'email']
            del PROFILE_ERRORS[user.username+'profile_pic']
            
            del PROFILE_ERRORS[user.username+'name_errors']
            del PROFILE_ERRORS[user.username+'surname_errors']
            del PROFILE_ERRORS[user.username+'username_errors']
            del PROFILE_ERRORS[user.username+'email_errors']
            del PROFILE_ERRORS[user.username+'profile_pic_errors']
            
        return render(request, "profile.html", {
            'first_name': first_name,
            'last_name': surname,
            'username': username,
            'email': email,
            'profile_picture': profile_picture,
            'name_errors': name_errors,
            'surname_errors': surname_errors,
            'username_errors': username_errors,
            'email_errors': email_errors,
            'profile_pic_errors': profile_pic_errors,
        })
    else:
        user_attrs = request.POST
        first_name = str(user_attrs['first_name']).strip()
        surname = str(user_attrs['last_name']).strip()
        username = str(user_attrs['username']).strip()
        email = str(user_attrs['email']).strip()
        profile_pic = str(user_attrs['profile_pic']).strip()
        
        required_field = "Este campo es obligatorio"
        if not first_name or first_name == '':
            name_errors.append(required_field)
        if not surname or surname == '':
            surname_errors.append(required_field)
        if not username or username == '':
            username_errors.append(required_field)
        if not email or email == '':
            email_errors.append(required_field)
        if not profile_pic:
            profile_pic = ""
        
        if first_name and first_name[0].islower():
            name_errors.append("La primera letra del nombre debe ser mayúscula")
        if surname and surname[0].islower():
            surname_errors.append("La primera letra del apellido debe ser mayúscula")
        if username and 3 >= len(username) <= 24:
            username_errors.append("El nombre de usuario debe tener entre 4 y 24 caracteres")
        if email and 3 >= len(email) <= 64:
            email_errors.append("El email debe tener entre 4 y 64 caracteres")
        if profile_pic and len(profile_pic) >= 90:
            profile_pic_errors.append("La imagen debe tener menos de 90 caracteres")
            
        try:
            if user.username != username and username:
                User.objects.get(username=username)
                username_errors.append("El nombre de usuario ya existe")
        except User.DoesNotExist:
            pass
        
        try:
            if user.email != email and email:
                User.objects.get(email=email)
                email_errors.append("El email ya está registrado")
        except User.DoesNotExist:
            pass
        
        if name_errors or surname_errors or username_errors or email_errors or profile_pic_errors:
            PROFILE_ERRORS[user.username+'name'] = first_name
            PROFILE_ERRORS[user.username+'surname'] = surname
            PROFILE_ERRORS[user.username+'username'] = username
            PROFILE_ERRORS[user.username+'email'] = email
            PROFILE_ERRORS[user.username+'profile_pic'] = profile_pic
            PROFILE_ERRORS[user.username+'name_errors'] = name_errors
            PROFILE_ERRORS[user.username+'surname_errors'] = surname_errors
            PROFILE_ERRORS[user.username+'username_errors'] = username_errors
            PROFILE_ERRORS[user.username+'email_errors'] = email_errors
            PROFILE_ERRORS[user.username+'profile_pic_errors'] = profile_pic_errors
            return HttpResponseRedirect(reverse("acme-nft:profile"))
            
        user.first_name = first_name
        user.last_name = surname
        user.username = username
        user.email = email
        profile_picture.image = profile_pic
        
        try:
            user.save()
            profile_picture.save()
            messages.success(request, "Perfil actualizado correctamente")
        except Exception:
            messages.error(request, "Ha ocurrido un error al actualizar el perfil")

    return HttpResponseRedirect(reverse("acme-nft:profile"))


# ------------------------ Address ------------------------

def show_adrress(request):
    if not request.user.is_authenticated:
        return is_authenticated(request)
    
    user = User.objects.get(username=request.user)
    list_address = user.address_set.all()
    first = list_address[0] if list_address else None
    last = list_address[len(list_address)-1] if list_address else None
    return render(request, "address.html", context={
        "list_address": list_address,
        "first": first,
        "last": last,
        })


def new_address(request):
    
    if not request.user.is_authenticated:
        return is_authenticated(request)
    
    user = User.objects.get(username=request.user)
    
    return address_form(request, user)


def delete_address(request, address_id):
    if not request.user.is_authenticated:
        return is_authenticated(request)

    address = Address.objects.get(id=address_id)
    
    if address.user == request.user:
        try:
            address.delete()
            messages.success(request, "Dirección eliminada correctamente")
        except Exception:
            messages.error(request, "Ha ocurrido un error al eliminar la dirección")
    else:
        messages.error(request, "No tienes permiso para eliminar esta dirección")
        
    return HttpResponseRedirect(reverse("acme-nft:show_address"))


def update_address(request, address_id):
    
    if not request.user.is_authenticated:
        return is_authenticated(request)
    
    user = User.objects.get(username=request.user)
    
    try:
        address = Address.objects.get(id=address_id)
    except Address.DoesNotExist:
        messages.error(request, "No tienes permiso para editar esta dirección")
        return HttpResponseRedirect(reverse("acme-nft:show_address"))
    
    if address.user != user:
        messages.error(request, "No tienes permiso para editar esta dirección")
        return HttpResponseRedirect(reverse("acme-nft:show_address"))
    
    return address_form(request, user, address)


def address_form(request, user, address=None):
    
    title_errors = ADDRESS_ERRORS[user.username+'title_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'title_errors'] else []
    street_name_errors = ADDRESS_ERRORS[user.username+'street_name_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'street_name_errors'] else []
    number_errors = ADDRESS_ERRORS[user.username+'number_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'number_errors'] else []
    block_errors = ADDRESS_ERRORS[user.username+'block_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'block_errors'] else []
    floor_errors = ADDRESS_ERRORS[user.username+'floor_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'floor_errors'] else []
    door_errors = ADDRESS_ERRORS[user.username+'door_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'door_errors'] else []
    city_errors = ADDRESS_ERRORS[user.username+'city_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'city_errors'] else []
    code_postal_errors = ADDRESS_ERRORS[user.username+'code_postal_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'code_postal_errors'] else []
    
    if request.method == "POST":

        address_attrs = request.POST
        title = str(address_attrs['title']).strip()
        street_name = str(address_attrs['street_name']).strip()
        number = str(address_attrs['number']).strip()
        block = str(address_attrs['block']).strip()
        floor = str(address_attrs['floor']).strip()
        door = str(address_attrs['door']).strip()
        city = str(address_attrs['city']).strip()
        code_postal = str(address_attrs['code_postal']).strip()

        required_field = "Este campo es obligatorio"
        if not title or title == '':
            title_errors.append(required_field)
        if not street_name or street_name == '':
            street_name_errors.append(required_field)
        if not number or number == '':
            number_errors.append(required_field)
        if not city or city == '':
            city_errors.append(required_field)
        if not code_postal or code_postal == '':
            code_postal_errors.append(required_field)
        if not block or block == '':
            block = None
        if not floor or floor == '':
            floor = None
        if not door or door == '':
            door = None
        
        if title and len(title) > 32:
            title_length = "El título no puede tener más de 32 caracteres"
            title_errors.append(title_length)
        if street_name and len(street_name) > 60:
            street_name_length = "El nombre de la calle no puede tener más de 60 caracteres"
            street_name_errors.append(street_name_length)
        if door and len(door) > 3:
            door_length = "La puerta no puede tener más de 3 caracteres"
            door_errors.append(door_length)
        if code_postal and code_postal.isdigit() == False:
            code_postal_digit = "El código postal debe ser un número"
            code_postal_errors.append(code_postal_digit)
        if block and block.isdigit() == False:
            block_digit = "El bloque debe ser un número"
            block_errors.append(block_digit)
        if floor and floor.isdigit() == False:
            floor_digit = "El piso debe ser un número"
            floor_errors.append(floor_digit)
        if number and number.isdigit() == False:
            number_digit = "El número debe ser un número"
            number_errors.append(number_digit)
        if city and len(city) > 60:
            city_length = "El nombre de la ciudad no puede tener más de 60 caracteres"
            city_errors.append(city_length)

        if title_errors or street_name_errors or number_errors or block_errors or floor_errors or door_errors or city_errors or code_postal_errors:
            ADDRESS_ERRORS[user.username+'title_errors'] = title_errors
            ADDRESS_ERRORS[user.username+'street_name_errors'] = street_name_errors
            ADDRESS_ERRORS[user.username+'number_errors'] = number_errors
            ADDRESS_ERRORS[user.username+'block_errors'] = block_errors
            ADDRESS_ERRORS[user.username+'floor_errors'] = floor_errors
            ADDRESS_ERRORS[user.username+'door_errors'] = door_errors
            ADDRESS_ERRORS[user.username+'city_errors'] = city_errors
            ADDRESS_ERRORS[user.username+'code_postal_errors'] = code_postal_errors
            ADDRESS_ERRORS[user.username+'title'] = title
            ADDRESS_ERRORS[user.username+'street_name'] = street_name
            ADDRESS_ERRORS[user.username+'number'] = number
            ADDRESS_ERRORS[user.username+'block'] = block
            ADDRESS_ERRORS[user.username+'floor'] = floor
            ADDRESS_ERRORS[user.username+'door'] = door
            ADDRESS_ERRORS[user.username+'city'] = city
            ADDRESS_ERRORS[user.username+'code_postal'] = code_postal
            if address:
                return HttpResponseRedirect(reverse("acme-nft:update_address"), args=(address.id,))
            else:
                return HttpResponseRedirect(reverse("acme-nft:new_address"))
        
        new_address = None
        if address:
            address.title=title
            address.street_name=street_name
            address.number=number
            address.block=block
            address.floor=floor
            address.door=door
            address.city=city
            address.code_postal=code_postal
            new_address = address
        else:
            new_address = Address(user_id=user.id, title=title, street_name=street_name,
                              number=number, block=block, floor=floor,
                              door=door, city=city, code_postal=code_postal)
        try:
            new_address.save()
            messages.success(request, "Dirección registrada correctamente")
        except Exception:
            messages.error(request, "Ha ocurrido un error al guardar la dirección")
    
        return HttpResponseRedirect(reverse("acme-nft:show_address"))
    else:
        title = address.title if address else ""
        street_name = address.street_name if address else ""
        number = address.number if address else ""
        block = address.block if address else ""
        floor = address.floor if address else ""
        door = address.door if address else ""
        city = address.city if address else ""
        code_postal = address.code_postal if address else ""
        
        if ADDRESS_ERRORS:
            title = ADDRESS_ERRORS[user.username+'title']
            street_name = ADDRESS_ERRORS[user.username+'street_name']
            number = ADDRESS_ERRORS[user.username+'number']
            block = ADDRESS_ERRORS[user.username+'block']
            floor = ADDRESS_ERRORS[user.username+'floor']
            door = ADDRESS_ERRORS[user.username+'door']
            city = ADDRESS_ERRORS[user.username+'city']
            code_postal = ADDRESS_ERRORS[user.username+'code_postal']
            
            del ADDRESS_ERRORS[user.username+'title']
            del ADDRESS_ERRORS[user.username+'street_name']
            del ADDRESS_ERRORS[user.username+'number']
            del ADDRESS_ERRORS[user.username+'block']
            del ADDRESS_ERRORS[user.username+'floor']
            del ADDRESS_ERRORS[user.username+'door']
            del ADDRESS_ERRORS[user.username+'city']
            del ADDRESS_ERRORS[user.username+'code_postal']
            
            del ADDRESS_ERRORS[user.username+'title_errors']
            del ADDRESS_ERRORS[user.username+'street_name_errors']
            del ADDRESS_ERRORS[user.username+'number_errors']
            del ADDRESS_ERRORS[user.username+'block_errors']
            del ADDRESS_ERRORS[user.username+'floor_errors']
            del ADDRESS_ERRORS[user.username+'door_errors']
            del ADDRESS_ERRORS[user.username+'city_errors']
            del ADDRESS_ERRORS[user.username+'code_postal_errors']
        
        return render(request, "address_form.html", context={
            'type': "UPDATE" if address else "NEW",
            'id': address.id if address else None,
            'title': title,
            'street_name': street_name,
            'number': number,
            'a_block': block,
            'floor': floor,
            'door': door,
            'city': city,
            'code_postal': code_postal,
            'title_errors': title_errors,
            'street_name_errors': street_name_errors,
            'number_errors': number_errors,
            'block_errors': block_errors,
            'floor_errors': floor_errors,
            'door_errors': door_errors,
            'city_errors': city_errors,
            'code_postal_errors': code_postal_errors,
        })

# ------------------------ Showcase ------------------------

def showcase(request):
    products_showcase = Product.objects.filter(is_showcase=True)

    return render(request, "showcase.html", {
        "products_showcase": products_showcase,
    })


def add_showcase(request, product_id):
    product = Product.objects.get(id=product_id)

    s_product = Product.objects.filter(is_showcase=True).count()

    if s_product < 7:
        product.is_showcase = True
        product.save()

    return HttpResponseRedirect(reverse("acme-nft:showcase"))


def delete_showcase(request, product_id):
    product = Product.objects.get(id=product_id)

    product.is_showcase = False
    product.save()

    return HttpResponseRedirect(reverse("acme-nft:showcase"))


# -------------------------- Cart --------------------------

def add_to_cart(request, product_id):
    quantity = int(request.POST['quantity'])

    if quantity > 0:
        user = request.user
        product = Product.objects.get(id=product_id)

        if not user.is_authenticated:
            user = None
        try:
            entry = ProductEntry.objects.get(product=product,
                                             entry_type='CART', user=user)
            entry.quantity = entry.quantity + quantity
        except ProductEntry.DoesNotExist:
            entry = ProductEntry(product=product, entry_type='CART', user=user,
                                 quantity=quantity)

        if entry.quantity <= product.stock:

            entry.save()
            messages.success(request, 'Producto añadido a la cesta')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            messages.error(request, 'La cantidad de producto a añadir debe ser menor o igual que el stock del producto')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        messages.error(request, 'La cantidad debe ser positiva')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart_view(request, error=None):
    user = request.user
    if not user.is_authenticated:
        user = None
    entries = ProductEntry.objects.filter(user=user, entry_type='CART')
    
    title_errors = ADDRESS_ERRORS[user.username+'title_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'title_errors'] else []
    street_name_errors = ADDRESS_ERRORS[user.username+'street_name_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'street_name_errors'] else []
    number_errors = ADDRESS_ERRORS[user.username+'number_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'number_errors'] else []
    block_errors = ADDRESS_ERRORS[user.username+'block_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'block_errors'] else []
    floor_errors = ADDRESS_ERRORS[user.username+'floor_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'floor_errors'] else []
    door_errors = ADDRESS_ERRORS[user.username+'door_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'door_errors'] else []
    city_errors = ADDRESS_ERRORS[user.username+'city_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'city_errors'] else []
    code_postal_errors = ADDRESS_ERRORS[user.username+'code_postal_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'code_postal_errors'] else []

    for entry in entries:
        if entry.product.stock == 0:
            entry.delete()

            messages.error(request,
                           'El producto ' + entry.product.name + ' no está disponible y ha sido eliminado de la cesta')
        elif entry.quantity > entry.product.stock:
            entry.quantity = entry.product.stock
            entry.save()
            messages.error(request, 'La cantidad de producto ' + entry.product.name + ' ha sido reducida a ' + str(
                entry.product.stock) + ' unidades')

    entries = ProductEntry.objects.filter(user=user, entry_type='CART')

    addresses = None

    if user:
        addresses = Address.objects.filter(user_id=user.id)

    if error:
        messages.error(request, error)
        
    if request.method == "GET":
        title = ""
        street_name = ""
        number = ""
        block = ""
        floor = ""
        door = ""
        city = ""
        code_postal = ""
        
        if ADDRESS_ERRORS:
            title = ADDRESS_ERRORS[user.username+'title']
            street_name = ADDRESS_ERRORS[user.username+'street_name']
            number = ADDRESS_ERRORS[user.username+'number']
            block = ADDRESS_ERRORS[user.username+'block']
            floor = ADDRESS_ERRORS[user.username+'floor']
            door = ADDRESS_ERRORS[user.username+'door']
            city = ADDRESS_ERRORS[user.username+'city']
            code_postal = ADDRESS_ERRORS[user.username+'code_postal']
            
            del ADDRESS_ERRORS[user.username+'title']
            del ADDRESS_ERRORS[user.username+'street_name']
            del ADDRESS_ERRORS[user.username+'number']
            del ADDRESS_ERRORS[user.username+'block']
            del ADDRESS_ERRORS[user.username+'floor']
            del ADDRESS_ERRORS[user.username+'door']
            del ADDRESS_ERRORS[user.username+'city']
            del ADDRESS_ERRORS[user.username+'code_postal']
            
            del ADDRESS_ERRORS[user.username+'title_errors']
            del ADDRESS_ERRORS[user.username+'street_name_errors']
            del ADDRESS_ERRORS[user.username+'number_errors']
            del ADDRESS_ERRORS[user.username+'block_errors']
            del ADDRESS_ERRORS[user.username+'floor_errors']
            del ADDRESS_ERRORS[user.username+'door_errors']
            del ADDRESS_ERRORS[user.username+'city_errors']
            del ADDRESS_ERRORS[user.username+'code_postal_errors']
            
        address_errors = False
        if title_errors or street_name_errors or number_errors or block_errors or floor_errors or door_errors or city_errors or code_postal_errors:
            address_errors = True
        
        return render(request, "cart.html", context={
            "cart": entries,
            "addresses": addresses,
            'title': title,
            'street_name': street_name,
            'number': number,
            'a_block': block,
            'floor': floor,
            'door': door,
            'city': city,
            'code_postal': code_postal,
            'title_errors': title_errors,
            'street_name_errors': street_name_errors,
            'number_errors': number_errors,
            'block_errors': block_errors,
            'floor_errors': floor_errors,
            'door_errors': door_errors,
            'city_errors': city_errors,
            'code_postal_errors': code_postal_errors,
            'address_errors': str(address_errors),
        })

    return render(request, "cart.html", {
        "cart": entries,
        "addresses": addresses,
    })


def resume_cart_view(request):
    user = request.user
    if not user.is_authenticated:
        user = None

    products_ids = request.POST.getlist('productos')
    pay = request.POST.get('pagos')
    address_id = request.POST.get('envios')

    name = '_'
    email = '_'

    if user is None:
        address = request.POST.get('direccion')
        name = request.POST.get('nombre')
        email = request.POST.get('email')
    else:
        address = Address.objects.get(id=address_id)

    if len(products_ids) == 0:
        return cart_view(request, error="No has seleccionado ningún producto")

    products = ProductEntry.objects.filter(id__in=products_ids, user=user,
                                           entry_type='CART')

    for entry in products:
        if entry.product.stock == 0:
            entry.delete()
            messages.error(request,
                           'El producto ' + entry.product.name + ' no está disponible y ha sido eliminado de la cesta')
        elif entry.quantity > entry.product.stock:
            entry.quantity = entry.product.stock
            entry.save()
            messages.error(request, 'La cantidad de producto ' + entry.product.name + ' ha sido reducida a ' + str(
                entry.product.stock) + ' unidades')

    products = ProductEntry.objects.filter(user=user, entry_type='CART')

    try:
        braintree_client_token = braintree.ClientToken.generate(
            {"customer_id": user.id})
    except Exception:
        braintree_client_token = braintree.ClientToken.generate({})

    return render(request, "resume-cart.html", {
        "products": products,
        "address": address,
        "pay": pay,
        "braintree_client_token": braintree_client_token,
        "name": name,
        "email": email,
    })


def payment(request):
    products_request = list(
        map(lambda x: int(x), request.POST.get('products').split(',')))

    products_entry = ProductEntry.objects.filter(id__in=products_request,
                                                 entry_type='CART')

    products = Product.objects.filter(productentry__in=products_entry)

    for p in products:
        p.stock = p.stock - products_entry.get(product=p).quantity
        p.save()

    address = request.POST.get('address')

    ref_code = ''.join(
        list(map(lambda x: str(x), products_request))) + ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=10))

    if request.POST.get('payment_method') == 'tarjeta':

        order_ = Order(ref_code=ref_code, payment_method=PaymentMethod.card.value,
                       address=address, status=Status.delivered.value)

    else:
        order_ = Order(ref_code=ref_code, payment_method=PaymentMethod.transference.value,
                       address=address, status=Status.to_be_paid.value)

    order_.save()

    products_entry.update(order=order_, entry_type='ORDER')

    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email
    else:
        first_name = request.POST['name']
        last_name = ''
        email = request.POST['email']

    if request.POST.get('pay') == 'TARJETA':
        nonce_from_the_client = request.POST['paymentMethodNonce']

        customer_kwargs = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
        customer_create = braintree.Customer.create(customer_kwargs)
        customer_id = customer_create.customer.id
        result = braintree.Transaction.sale({
            "amount": f"{order_.total():.2f}",
            "payment_method_nonce": nonce_from_the_client,
            "options": {
                "submit_for_settlement": True
            }
        })

    user = request.user

    if not user.is_authenticated:
        name = request.POST['name']
        e = request.POST['email']
        pdf = get_invoice_pdf(order_, name, e)
    else:
        e = user.email
        pdf = get_invoice_pdf(order_)
        
    if user.is_authenticated:
        full_name = user.first_name + ' ' + user.last_name
    else:
        full_name = str(request.POST['name']).strip()

    if str(request.POST.get('payment_method')).strip().upper() == 'TARJETA':
        message = f'Gracias por su compra, {full_name}, su pedido es el #{ref_code}.'

    else:
        message = f'Gracias por su compra, {full_name}, su pedido es el #{ref_code}.\nRecuerde que debe realizar el pago en la cuenta bancaria: ES6000491500051234567892 para que la compra y la factura sean válidas.'

    email = EmailMessage('Acme NFT: Factura de pedido #{}'.format(ref_code),
                         message,
                         'no-replay-acmenftinc@gmail.com',
                         [e])
    email.attach_file(pdf)
    email.send()

    return HttpResponse('Ok')


def edit_amount_cart(request, product_id):
    user = request.user
    if not user.is_authenticated:
        user = None
    product = Product.objects.get(id=product_id)
    entry = ProductEntry.objects.get(product=product, entry_type='CART',
                                     user=user)

    quantity = int(bytes_to_dict(request.body)['quantity'])
    if 0 < quantity <= entry.product.stock:
        entry.quantity = quantity
        entry.save()
        return HttpResponse('Ok')
    else:
        return HttpResponseNotFound("Invalid Quantity")


def delete_from_cart(request, product_id):
    user = request.user
    if not user.is_authenticated:
        user = None
    product = Product.objects.get(id=product_id)
    entry = ProductEntry.objects.get(product=product, entry_type='CART',
                                     user=user)
    entry.delete()
    return HttpResponse('Ok')


def add_address_in_cart(request):
    user = request.user
    if not user.is_authenticated:
        return is_authenticated(request)

    title_errors = ADDRESS_ERRORS[user.username+'title_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'title_errors'] else []
    street_name_errors = ADDRESS_ERRORS[user.username+'street_name_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'street_name_errors'] else []
    number_errors = ADDRESS_ERRORS[user.username+'number_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'number_errors'] else []
    block_errors = ADDRESS_ERRORS[user.username+'block_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'block_errors'] else []
    floor_errors = ADDRESS_ERRORS[user.username+'floor_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'floor_errors'] else []
    door_errors = ADDRESS_ERRORS[user.username+'door_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'door_errors'] else []
    city_errors = ADDRESS_ERRORS[user.username+'city_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'city_errors'] else []
    code_postal_errors = ADDRESS_ERRORS[user.username+'code_postal_errors'] if ADDRESS_ERRORS and ADDRESS_ERRORS[user.username+'code_postal_errors'] else []
    
    if request.method == "POST":

        address_attrs = request.POST
        title = str(address_attrs['title']).strip()
        street_name = str(address_attrs['street_name']).strip()
        number = str(address_attrs['number']).strip()
        block = str(address_attrs['block']).strip()
        floor = str(address_attrs['floor']).strip()
        door = str(address_attrs['door']).strip()
        city = str(address_attrs['city']).strip()
        code_postal = str(address_attrs['code_postal']).strip()

        required_field = "Este campo es obligatorio"
        if not title or title == '':
            title_errors.append(required_field)
        if not street_name or street_name == '':
            street_name_errors.append(required_field)
        if not number or number == '':
            number_errors.append(required_field)
        if not city or city == '':
            city_errors.append(required_field)
        if not code_postal or code_postal == '':
            code_postal_errors.append(required_field)
        if not block or block == '':
            block = None
        if not floor or floor == '':
            floor = None
        if not door or door == '':
            door = None
        
        if title and len(title) > 32:
            title_length = "El título no puede tener más de 32 caracteres"
            title_errors.append(title_length)
        if street_name and len(street_name) > 60:
            street_name_length = "El nombre de la calle no puede tener más de 60 caracteres"
            street_name_errors.append(street_name_length)
        if door and len(door) > 3:
            door_length = "La puerta no puede tener más de 3 caracteres"
            door_errors.append(door_length)
        if code_postal and code_postal.isdigit() == False:
            code_postal_digit = "El código postal debe ser un número"
            code_postal_errors.append(code_postal_digit)
        if block and block.isdigit() == False:
            block_digit = "El bloque debe ser un número"
            block_errors.append(block_digit)
        if floor and floor.isdigit() == False:
            floor_digit = "El piso debe ser un número"
            floor_errors.append(floor_digit)
        if number and number.isdigit() == False:
            number_digit = "El número debe ser un número"
            number_errors.append(number_digit)
        if city and len(city) > 60:
            city_length = "El nombre de la ciudad no puede tener más de 60 caracteres"
            city_errors.append(city_length)

        if title_errors or street_name_errors or number_errors or block_errors or floor_errors or door_errors or city_errors or code_postal_errors:
            ADDRESS_ERRORS[user.username+'title_errors'] = title_errors
            ADDRESS_ERRORS[user.username+'street_name_errors'] = street_name_errors
            ADDRESS_ERRORS[user.username+'number_errors'] = number_errors
            ADDRESS_ERRORS[user.username+'block_errors'] = block_errors
            ADDRESS_ERRORS[user.username+'floor_errors'] = floor_errors
            ADDRESS_ERRORS[user.username+'door_errors'] = door_errors
            ADDRESS_ERRORS[user.username+'city_errors'] = city_errors
            ADDRESS_ERRORS[user.username+'code_postal_errors'] = code_postal_errors
            ADDRESS_ERRORS[user.username+'title'] = title
            ADDRESS_ERRORS[user.username+'street_name'] = street_name
            ADDRESS_ERRORS[user.username+'number'] = number
            ADDRESS_ERRORS[user.username+'block'] = block
            ADDRESS_ERRORS[user.username+'floor'] = floor
            ADDRESS_ERRORS[user.username+'door'] = door
            ADDRESS_ERRORS[user.username+'city'] = city
            ADDRESS_ERRORS[user.username+'code_postal'] = code_postal
            return HttpResponseRedirect(reverse("acme-nft:cart"))
        
        new_address = None
        
        new_address = Address(user_id=user.id, title=title, street_name=street_name,
                            number=number, block=block, floor=floor,
                            door=door, city=city, code_postal=code_postal)
        try:
            new_address.save()
            messages.success(request, "Dirección registrada correctamente")
        except Exception:
            messages.error(request, "Ha ocurrido un error al guardar la dirección")
    
        return HttpResponseRedirect(reverse("acme-nft:cart"))
    else:

        return HttpResponseRedirect(reverse("acme-nft:cart"))


# ------------------------ Wishlist ------------------------

def add_to_wishlist(request, product_id):
    
    try:
        user = request.user
        product = Product.objects.get(pk=product_id)
        entry = ProductEntry.objects.get(product=product,
                                         entry_type='WISHLIST', user=user)
        entry.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except ProductEntry.DoesNotExist:

        product = get_object_or_404(Product, pk=product_id)
        user = request.user
        entry = ProductEntry(quantity=None, entry_type='WISHLIST',
                             product=product, user=user)
        entry.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# ------------------------ Comments ------------------------

def add_comment(request, product_id):
    if request.method == "POST":
        user = User.objects.get(pk=1)
        product = Product.objects.get(pk=product_id)

        comment_text = request.POST['comment']

        comment = Comment(text=comment_text, product=product, user=user)
        comment.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# ------------------------ Orders ------------------------

def orders(request):
    if not request.user.is_authenticated:
        return is_authenticated(request)
    
    delivered_orders = Order.objects.filter(productentry__user_id=request.user.id, status=Status.delivered).order_by('-date').distinct()
    first_delivered = delivered_orders.first()
    last_delivered = delivered_orders.last()
    to_be_paid_orders = Order.objects.filter(productentry__user_id=request.user.id, status=Status.to_be_paid).order_by('-date').distinct()
    first_to_be_paid = to_be_paid_orders.first()
    last_to_be_paid = to_be_paid_orders.last()

    return render(request, "orders.html", {
        "delivered_orders": delivered_orders,
        "first_delivered": first_delivered,
        "last_delivered": last_delivered,
        "to_be_paid_orders": to_be_paid_orders,
        "first_to_be_paid": first_to_be_paid,
        "last_to_be_paid": last_to_be_paid,
    })


def order(request, order_id):
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "No se ha encontrado la orden")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    products = ProductEntry.objects.filter(order_id=order_id)
    
    if products and products[0].user != None and not request.user.is_authenticated:
        return is_authenticated(request)
    
    if products and products[0].user != None and products[0].user.id != request.user.id:
        messages.error(request, "No se ha encontrado la orden")
        return HttpResponseRedirect(reverse("acme-nft:orders"))
    
    return render(request, "order-details.html", {
        "order": order,
        "products": products,
        "total": order.total(),
    })
    
def search_order(request):
    if request.method == 'POST':
        ref_code = str(request.POST['order_code_ref']).strip()
        
        if not ref_code or ref_code == '':
            messages.error(request, 'Introduzca un código de referencia válido')
            return HttpResponseRedirect(reverse("acme-nft:search_order"))
        
        ref_code = ref_code[1:] if ref_code[0] == '#' else ref_code
        order = Order.objects.filter(ref_code=ref_code)
        if order:
            return HttpResponseRedirect(reverse('acme-nft:order', args=(order[0].id,)))
        else:
            messages.error(request, 'El código de referencia no existe')
            return HttpResponseRedirect(reverse("acme-nft:search_order"))

    else:
        return render(request, 'search-order.html')


# ------------------------ Customer Service ------------------------
def customer_service(request):
    return render(request, "customer-service.html")


def complaint(request):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        complaint_title = request.POST['title']
        complaint_text = request.POST['complaint']
        complaint = Complaint(title=complaint_title,
                              description=complaint_text, user=user,
                              date=datetime.now())
        complaint.save()
        messages.success(request, 'Su reclamación ha sido procesada y se le hará llegar a la administración de la web')
        return HttpResponseRedirect(reverse("acme-nft:service"))


def opinion(request):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        opinion_title = request.POST['title']
        opinion_text = request.POST['opinion']
        opinion = Opinion(title=opinion_title, description=opinion_text,
                          user=user, date=datetime.now())
        opinion.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def opinions(request):
    opinions = list(Opinion.objects.all().order_by('-date'))
    return render(request, "opinions.html", {
        "opinions": opinions,
    })


# ------------------------ Common ------------------------
def bytes_to_dict(bytes_d):
    dict_str = bytes_d.decode('utf-8')
    return ast.literal_eval(dict_str)


def get_invoice_pdf(order_id, name=None, email=None):
    order_ = Order.objects.get(id=order_id.id)
    products = ProductEntry.objects.filter(order=order_,
                                           entry_type='ORDER').annotate()
    user = products[0].user

    total = order_.total

    if name is None:
        name = user.first_name + " " + user.last_name
        email = user.email

    context_dict = {"order_reference": order_.ref_code,
                    "products": products,
                    "client": {
                        "name": name,
                        "email": email,
                    },
                    "pay": order_.payment_method,
                    "address": order_.address,
                    "total": total,
                    }

    template = get_template('invoice.html')
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(
        StringIO(html),
        dest=result,
        encoding='UTF-8'
    )

    # save pdf
    if not os.path.exists('invoices/'):
        os.makedirs('invoices/')

    with open(f'invoices/{order_.ref_code}.pdf', 'wb') as f:
        f.write(result.getvalue())

    return f'invoices/{order_.ref_code}.pdf'


# ------------------------ Suggestions ------------------------
def sugesstions(request, product_id):
    product = Product.objects.get(pk=product_id)
    suggestions = Product.objects.filter(collection=product.collection).exclude(
        pk=product_id) | Product.objects.filter(author_id=product.author_id).exclude(pk=product_id)

    products_to_exclude = [s.id for s in suggestions]
    products_to_exclude.append(product_id)
    random = Product.objects.all().order_by('?').exclude(name__in=products_to_exclude)[:5 - len(suggestions)]
    return JsonResponse({'suggestions': list(suggestions.values())
                         + list(random.values())})


def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']

        contact = Contact(name=name, email=email, subject=subject)
        contact.save()
        messages.success(request, 'Mensaje enviado correctamente')
        return render(request, "contact.html")
    else:
        return render(request, "contact.html")


# ------------------------ Services term ------------------------

def get_service_terms(request):
    return render(request, "service-terms.html")

# ------------------------ Returns Policy ------------------------

def get_returns_policy(request):
    return render(request, "returns-policy.html")

# ------------------------ Data Protection Policy ------------------------

def get_data_protection_policy(request):
    return render(request, "data-protection-policy.html")

# ------------------------ admin ------------------------

class AdminListProducts(ListView):
    model = Product
    template_name = 'admin-list-products.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.all().order_by('id')


@permission_required('is_staff')
def update_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'GET':
        product = Product.objects.get(pk=product_id)
        r = product.rarity
        a = product.author

        rarity = [(rarity, rarity.value) for rarity in RarityType if rarity.value != r]
        authors = Author.objects.exclude(id__in=[a.id]).all()

        return render(request, 'admin-update-product.html', {'product': product, 'rarity': rarity, 'authors': authors})
    elif request.method == 'POST':
        new_stock = request.POST['stock']
        new_price = request.POST['price']
        new_rarity = request.POST['rarity']
        new_offer_price = request.POST['offer_price']
        new_showcase = bool(request.POST['showcase'])

        if new_offer_price == '':
            new_offer_price = None

        if new_stock != product.stock:
            product.stock = new_stock
        if new_price != product.price:
            product.price = new_price
        if new_rarity != product.rarity:
            product.rarity = new_rarity
        if new_offer_price != product.offer_price:
            product.offer_price = new_offer_price

        if new_showcase != product.showcase:
            product.showcase = new_showcase

        product.save()

        return HttpResponseRedirect(reverse('acme-nft:admin'))


# only admin
@permission_required('is_staff')
def create_product(request):
    if request.method == 'GET':
        rarity = [(rarity, rarity.value) for rarity in RarityType]
        authors = Author.objects.all()
        return render(request, 'admin-form-product.html', {'rarity': rarity, 'authors': authors})
    elif request.method == 'POST':
        name = request.POST['name']
        collection = request.POST['collection']
        price = request.POST['price']
        offer_price = request.POST['offer_price']
        if offer_price == '':
            offer_price = None
        stock = request.POST['stock']
        url = request.POST['url']
        rarity = request.POST['rarity']
        showcase = bool(request.POST['showcase'])

        if request.POST['select-author'] == 'true':
            author = Author.objects.get(pk=request.POST['author-select'])
        else:
            author = Author.objects.create(name=request.POST['author-input'])

        product = Product(name=name, collection=collection, price=price,
                          stock=stock, image_url=url, rarity=rarity, offer_price=offer_price, author=author,
                          showcase=showcase)
        product.save()
        return HttpResponseRedirect(reverse('acme-nft:admin'))


class AdminListOrders(ListView):
    model = Order
    template_name = 'admin-list-orders.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return Order.objects.all().order_by('id')


def change_order_status(request, order_id):
    order = Order.objects.get(pk=order_id)

    new_status = bytes_to_dict(request.body)['status']
    order.status = new_status
    order.save()

    return HttpResponseRedirect(reverse('acme-nft:admin'))
