from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import User , Item
import os

# Create your views here.
def index(request):

    return render(request, "dofustock/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "dofustock/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "dofustock/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "dofustock/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "dofustock/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "dofustock/register.html")

def encyclopedie(request):

    all_items = Item.objects.all()
    categories = Item.objects.values_list('category', flat = True).distinct()
    return render(request, "dofustock/encyclopedie.html",{
        "items" : all_items,
        "categories" : categories,

    })

def get_item_types(request):
    category = request.GET.get('category')
    
    # Fetch unique item types for the selected category
    item_types = Item.objects.filter(category=category)\
        .values_list('item_type', flat=True)\
        .distinct()
    
    return JsonResponse(list(item_types), safe=False)

def get_items(request):
    category = request.GET.get('category')
    item_type = request.GET.get('item_type')
    
    # Filter items based on category and item type
    items = Item.objects.filter(
        category=category, 
        item_type=item_type
    ).values()
    
    return JsonResponse(list(items), safe=False)

def search_items(request):
    search_term = request.GET.get('search', '').strip()
    
    if not search_term:
        return JsonResponse([], safe=False)
    
    # Perform a case-insensitive search across all items
    items = Item.objects.filter(
        name__icontains=search_term
    ).values()
    
    return JsonResponse(list(items), safe=False)