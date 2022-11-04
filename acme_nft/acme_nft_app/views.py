from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse


from acme_nft_app.models import User

# ------------------------------------- Render views -------------------------------------

def index(request):
    return render(request, "index.html", context={})

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

        return
    else:
        return render(request, "login.html")


    #user_attrs = request.POST

    #if user_attrs['password'] != user_attrs['password2']:
    #    return HttpResponseRedirect(reverse("acme-nft:error"))

    #user = User(username=user_attrs['username'],
    #           email=user_attrs['email'],
    #           password=make_password(user_attrs['password']),
    #           name=user_attrs['name'],
    #          surname=user_attrs['surname'])
    #user.save()

    #return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))