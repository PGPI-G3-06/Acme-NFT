from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from .models import User, Product, Address


from acme_nft_app.models import User, Product

# ------------------------------------- Render views -------------------------------------

def index(request):
    return render(request, "index.html", context={"products": Product.objects.all()})

def login_page(request):
    return render(request, "login.html", context={})

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
        if len(errors) > 0:
            return render(request, "login.html", {
                "errors": errors})
        else:
            user = User(username=username, password=make_password(password), name=name, surname=surname, email=email)
            user.save()
            print(user.id)
            return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))
            
    else:
        return render(request, "login.html")

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

