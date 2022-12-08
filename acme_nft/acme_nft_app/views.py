import os.path
import string
import random
from datetime import datetime
from django.contrib import auth, messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django import forms
from django.core import serializers
from django.http import HttpResponseNotFound, HttpResponseRedirect, \
    HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
import ast
import braintree

from io import BytesIO, StringIO
from django.template.loader import get_template
from django.views.generic import ListView, CreateView, DetailView
from xhtml2pdf import pisa

from acme_nft import settings as django_settings
from django.core.mail import send_mail, EmailMessage

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

# ------------------------------------- Render views -------------------------------------

def index(request):
    
    products = Product.objects.all()
    try:
        if request.GET['order-by'] == 'collections':
            products = Product.objects.all().order_by('collection')

    except KeyError:
        pass
    try:
        if request.GET['order-by'] == 'author':
            products = Product.objects.all().order_by('author__name')

    except KeyError:
        pass

    try:
        if request.GET['buscar'] != '':
            products = Product.objects.all().filter(
                name__icontains=request.GET[
                    'buscar']) | Product.objects.all().filter(
                collection__icontains=request.GET[
                    'buscar']) | Product.objects.all().filter(
                author__name__icontains=request.GET['buscar'])

        else:
            products = []
    except KeyError:
        pass

    entries = ProductEntry.objects.all()
    products_to_list = []
    wishlist = []

    try:
        page_number = int(request.GET['page'])
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

    return render(request, "index.html", context={"user": request.user,
                                                  "products": products_to_list,
                                                  "wishlist": wishlist,
                                                  "pages_range": range(0,
                                                                       possible_pages),
                                                  "current_page": page_number,
                                                  "needs_pagination": possible_pages > 1,
                                                  }
                  )


def signin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("acme-nft:index"))
    else:
        return render(request, "login.html", context={})


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
                           "comments": comments, "in_wishlist": in_wishlist})

def wishlist(request):
    
    if not request.user.is_authenticated:     
        messages.error(request, 'Tienes que iniciar sesión primero')
        return HttpResponseRedirect(reverse("acme-nft:signin"))

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
    user = User.objects.get(username=request.user)
    if request.method == 'GET':

        return render(request, "profile.html", {
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
    return render(request, "show_address.html",
                  context={"list_address": list_address})


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

        errors = check_errors(block, city, code_postal, door, errors, floor,
                              number,
                              street_name)
        if len(errors) > 0:
            are_errors = True
            return render(request, "new_address.html", {
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

            address = Address(user_id=request.user.id, street_name=street_name,
                              number=number, block=block, floor=floor,
                              door=door, city=city, code_postal=code_postal)
            address.save()
            return HttpResponseRedirect(
                reverse("acme-nft:show_address", args=(request.user.id,)))
    else:
        return render(request, "new_address.html")


def delete_address(request, address_id):
    address = Address.objects.get(id=address_id)
    address.delete()
    return HttpResponseRedirect(
        reverse("acme-nft:show_address", args=(request.user.id,)))


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

        errors = check_errors(block, city, code_postal, door, errors, floor,
                              number,
                              street_name)
        if len(errors) > 0:
            are_errors = True
            return render(request, "new_address.html", {
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

            return HttpResponseRedirect(
                reverse("acme-nft:show_address", args=(request.user.id,)))
    else:
        address = Address.objects.get(id=address_id)
        street_name = address.street_name
        number = address.number
        floor = address.floor
        if floor is None:
            floor = ""
        block = address.block
        if block is None:
            block = ""
        door = address.door
        if door is None:
            door = ""
        city = address.city
        code_postal = address.code_postal

        return render(request, "update_address.html", {
            "street_name": street_name,
            "number": number,
            "floor": floor,
            "block": block,
            "door": door,
            "city": city,
            "code_postal": code_postal,
            "id": address_id, })


def check_errors(block, city, code_postal, door, errors, floor, number,
                 street_name):
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


# ------------------------ Showcase ------------------------

def showcase(request):
    products_showcase = Product.objects.filter(is_showcase=True)

    return render(request, "showcase.html", {
        "products_showcase": products_showcase,
    })


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

    addresses = None

    if user:
        addresses = Address.objects.filter(user_id=user.id)
    
    if error:
        messages.error(request, error)


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
    nonce_from_the_client = request.POST['paymentMethodNonce']
    products_request = list(
        map(lambda x: int(x), request.POST.get('products').split(',')))

    products_entry = ProductEntry.objects.filter(id__in=products_request,
                                                 entry_type='CART')

    products = Product.objects.filter(productentry__in=products_entry)

    for p in products:
        p.stock = p.stock - products_entry.get(product=p).quantity
        p.save()

    total = 0

    for product in products_entry:
        total += product.product.price * product.quantity

    address = request.POST.get('address')

    ref_code = ''.join(
        list(map(lambda x: str(x), products_request))) + ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=10))

    order = Order(ref_code=ref_code, payment_method=PaymentMethod.card.value,
                  address=address, status=Status.sent.value)

    order.save()

    products_entry.update(order=order, entry_type='ORDER')

    if request.user.is_authenticated:
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email
    else:
        first_name = request.POST['name']
        last_name = ''
        email = request.POST['email']

    customer_kwargs = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }
    customer_create = braintree.Customer.create(customer_kwargs)
    customer_id = customer_create.customer.id
    result = braintree.Transaction.sale({
        "amount": f"{total:.2f}",
        "payment_method_nonce": nonce_from_the_client,
        "options": {
            "submit_for_settlement": True
        }
    })

    user = request.user



    if not user.is_authenticated:
        name = request.POST['name']
        e = request.POST['email']
        pdf = get_invoice_pdf(order, name, e)
    else:
        e = user.email
        pdf = get_invoice_pdf(order)

    email = EmailMessage('Acme NFT',
                         f'Gracias por su compra, su pedido es {ref_code}',
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
        user = None

    street_name = request.POST['street_name']
    number = request.POST['number']
    floor = request.POST['floor']
    block = request.POST['block']
    door = request.POST['door']
    city = request.POST['city']
    code_postal = request.POST['postal_code']

    Address.objects.create(user=user, street_name=street_name, number=number,
                           floor=floor, block=block, door=door, city=city,
                           code_postal=code_postal)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
    orders = Order.objects.filter(
        productentry__user_id=request.user.id).order_by('-date').distinct()

    return render(request, "show-orders.html", {
        "orders": orders,
    })


def order(request, order_id):
    order = Order.objects.get(pk=order_id)
    products = ProductEntry.objects.filter(order_id=order_id)
    total = final_price(products)
    return render(request, "order-details.html", {
        "order": order,
        "products": products,
        "total": total,
    })


def final_price(products):
    final_price = 0
    for product in products:
        final_price += product.product.price * product.quantity
    return final_price


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


# ------------------------ common ------------------------
def bytes_to_dict(bytes_d):
    dict_str = bytes_d.decode('utf-8')
    return ast.literal_eval(dict_str)


def get_invoice_pdf(order_id, name=None, email=None):
    order_ = Order.objects.get(id=order_id.id)
    products = ProductEntry.objects.filter(order=order_,
                                           entry_type='ORDER').annotate()
    user = products[0].user

    total_by_product = {p.product.id: p.product.price * p.quantity for p in
                        products}

    total = sum(total_by_product.values())

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

    path = f'invoices/{order_.ref_code}.csv'



    with open(f'invoices/{order_.ref_code}.pdf', 'wb') as f:
        f.write(result.getvalue())

    return f'invoices/{order_.ref_code}.pdf'

    
    
# ------------------------ Suggestions ------------------------
def sugesstions(request, product_id):
    product = Product.objects.get(pk=product_id)
    suggestions = Product.objects.filter(collection=product.collection).exclude(
        pk=product_id) | Product.objects.filter(author_id=product.author_id).exclude(pk=product_id)

    while len(suggestions) < 5:
        suggestions = suggestions | Product.objects.all().order_by('?').exclude(
        pk=product_id)[:5-len(suggestions)]
    return JsonResponse({'suggestions': list(suggestions.values())})

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

