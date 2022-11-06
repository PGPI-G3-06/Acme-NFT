import django.contrib.auth
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.contrib.sessions.models import Session
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
            Session.session_key = user.id
            return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))
        else:
            return HttpResponseRedirect(reverse("acme-nft:error"))
    except:
        return HttpResponseRedirect(reverse("acme-nft:error"))



def register(request):

    #Se puede modificar un usuario desde el registro xD

    user_attrs = request.POST

    user = User(username=user_attrs['username'], email=user_attrs['email'], password=make_password(user_attrs['password']))
    user.save()

    return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))

def edit_user(request):

    user = User.objects.get(id=2)
    print(user.username)
    if request.method == 'GET':


        return render(request, "profile.html",{
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'surname': user.surname,
    })

    else:

        user_attrs = request.POST
        user.name = user_attrs['name']
        user.surname = user_attrs['surname']
        user.username = user_attrs['username']
        user.email = user_attrs['email']
        user.save()

    return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))