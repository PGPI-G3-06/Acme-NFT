from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse

from acme_nft_app.models import User


def index(request):
    return render(request, "index.html", context={})

def register(request):

    #Se puede modificar un usuario desde el registro xD

    user_attrs = request.POST

    user = User(username=user_attrs['username'], email=user_attrs['email'], password=make_password(user_attrs['password']))
    user.save()

    return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))

def login(request):

    try:
        user = User.objects.get(email=request.POST['email'])

        if check_password(request.POST['password'], user.password):
            return HttpResponseRedirect(reverse("acme-nft:hello", args=(user.id,)))
        else:
            return HttpResponseRedirect(reverse("acme-nft:error"))
    except:
        return HttpResponseRedirect(reverse("acme-nft:error"))

def hello(request, user_id):

    user = get_object_or_404(User, pk=user_id)

    return render(request, "hello.html", context={'user': user})

def error(request):
    return render(request, "error.html", context={})