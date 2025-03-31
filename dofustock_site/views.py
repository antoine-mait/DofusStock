from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect 
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from .models import User , Item , Craftlist
from playwright.sync_api import sync_playwright
import json
from django.db.models import Case, When, IntegerField, Value


from .utils import sanitize_filename
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
    
    # Get all items that match the search term
    items = Item.objects.filter(name__icontains=search_term)
    
    # Annotate items with a relevance score
    items = items.annotate(
        relevance=Case(
            # Exact match gets highest priority
            When(name__iexact=search_term, then=Value(100)),
            # Starts with search term gets high priority
            When(name__istartswith=search_term, then=Value(80)),
            # Contains "Replique" gets lower priority
            When(name__icontains="Replique", then=Value(10)),
            # Default relevance
            default=Value(50),
            output_field=IntegerField(),
        )
    ).order_by('-relevance')  # Sort by relevance, highest first
    
    return JsonResponse(list(items.values()), safe=False)

def get_items_recipe(request, ankama_id):
    try:
        # Use the path parameter directly
        item = Item.objects.get(ankama_id=ankama_id)
        
        effects = list(item.effects.values())
        recipes = list(item.recipes.values())
        
        # Combine item data with related data
        item_data = item.__dict__
        item_data.pop('_state', None)  
        item_data['effects'] = effects
        item_data['recipes'] = recipes
        
        return JsonResponse(item_data)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    
def item_detail(request, ankama_id):
    try:
        item = Item.objects.get(ankama_id=ankama_id)
        
        # Get craftlist for the current user
        craftlist = set()
        if request.user.is_authenticated:
            user_craftlist, _ = Craftlist.objects.get_or_create(user=request.user)
            craftlist = set(user_craftlist.item.values_list("ankama_id", flat=True))
        
        # Sanitize filename
        item.sanitized_name = sanitize_filename(item.name)
        
        # Fetch recipes with full resource details
        recipes = []
        for recipe in item.recipes.all():
            recipe_dict = recipe.__dict__
            
            # Try to find the resource item
            try:
                resource_item = Item.objects.get(ankama_id=recipe.resource_id)
                recipe_dict['resource_image'] = f"/media/IMG/{resource_item.category}/{resource_item.item_type}/{resource_item.ankama_id}-{sanitize_filename(resource_item.name)}.png"
            except Item.DoesNotExist:
                recipe_dict['resource_image'] = '/media/IMG/equipment/Outil/489-Loupe.png'
            
            recipes.append(recipe_dict)
        
        effects = list(item.effects.values())
        
        return render(request, "dofustock/item.html", {
            'item': item,
            'effects': effects,
            'recipes': recipes,
            'craftlist': craftlist,
        })
    except Item.DoesNotExist:
        return HttpResponseRedirect(reverse("encyclopedie"))
    
def scrape_dofus_build_items(request, url):
    print(f"Scraping started for URL: {url}")
    
    try:
        # Define excluded items
        exclude_items = [
            'Personnage', 'Capital vitalité', 'Capital', 'Parchemin', 
            'Parchemin vitalité', 'Bonus caracs', 
            'Bonus agilité', 'Bonus sagesse', 'Bonus force', 'Bonus chance',
            'Forgemagie', 'Dofusbook Touch', 'Dofusbook Retro', 'Logo Dofusbook'
        ]
        
        print("Initializing Playwright...")
        # Using Playwright for web scraping
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=True)
            print("Browser launched, creating page...")
            page = browser.new_page()
            print(f"Navigating to URL: {url}")
            page.goto(url, wait_until='networkidle')
            print("Page loaded, extracting items...")
            
            # Extract items using JavaScript execution with improved item detection
            build_items = page.evaluate('''() => {
                console.log("Evaluating JavaScript in page context");
                
                const items = new Set();
                const excludeItems = %s;
                
                // Strategy 1: Look at tooltips
                const tooltips = document.querySelectorAll('.CmpTooltip-text');
                console.log("Found tooltips:", tooltips.length);
                
                tooltips.forEach(tooltip => {
                    const details = tooltip.querySelectorAll('div');
                    details.forEach(detail => {
                        const text = detail.textContent.trim();
                        if (text.includes(':')) {
                            const item = text.split(':')[0].trim();
                            items.add(item);
                        }
                    });
                });
                const pictureImages = document.querySelectorAll('img.picture');
                pictureImages.forEach(img => {
                    if (img.alt && img.alt.trim() !== '') {
                        items.add(img.alt.trim());
                    }
                });
                
                // Apply filtering at the end only
                return Array.from(items).filter(item => 
                    !excludeItems.includes(item) && !item.startsWith('Panoplie') && !item.endsWith('oplie')
                );
            }''' % json.dumps(exclude_items))
            
            print(f"Items extracted: {build_items}")
            browser.close()
            print("Browser closed")
            
            return build_items
    
    except Exception as e:
        import traceback
        print(f"Exception in scrape_dofus_build_items: {e}")
        traceback.print_exc()
        return []
    
def craft_list(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    craftlist, _ = Craftlist.objects.get_or_create(user=request.user)
    items = craftlist.item.all()  

    for item in items : 
        item.sanitized_name = sanitize_filename(item.name)

    # Fetch recipes with full resource details
    recipes = []
    for recipe in item.recipes.all():
        recipe_dict = recipe.__dict__
        
        # Try to find the resource item
        try:
            resource_item = Item.objects.get(ankama_id=recipe.resource_id)
            recipe_dict['resource_image'] = f"/media/IMG/{resource_item.category}/{resource_item.item_type}/{resource_item.ankama_id}-{sanitize_filename(resource_item.name)}.png"
        except Item.DoesNotExist:
            recipe_dict['resource_image'] = '/media/IMG/equipment/Outil/489-Loupe.png'
        
        recipes.append(recipe_dict)

    return render(request, "dofustock/craft_list.html", {
        "items": items,
        "craftlist": set(items.values_list("ankama_id", flat=True)),
        "recipes": recipes,
    })

def scrape_build(request):
    url = request.GET.get('url', '')
    
    # Print debug information to your server console
    print(f"Received scrape request for URL: {url}")
    
    if not url or not url.startswith('https://d-bk.net/'):
        print("Invalid URL format")
        return JsonResponse({'error': 'Invalid URL'}, status=400)
    
    try:
        # Call your existing scrape function
        print("Starting web scraping...")
        items = scrape_dofus_build_items(request, url)
        print(f"Scraping complete, found {len(items)} items: {items}")
        return JsonResponse(items, safe=False)
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full traceback to server console
        return JsonResponse({'error': str(e)}, status=500)

def toggle_craftlist(request, ankama_id):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, ankama_id=ankama_id)  
        craftlist, _ = Craftlist.objects.get_or_create(user=request.user)
        if item in craftlist.item.all():
            craftlist.item.remove(item)
        else:
            craftlist.item.add(item)
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    return redirect("login")