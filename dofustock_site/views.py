from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect 
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import User , Item , Craftlist , Price
from playwright.sync_api import sync_playwright
import json
from django.db.models import Case, When, IntegerField, Value
from django.template.defaultfilters import floatformat

from .utils import sanitize_filename , calculate_craft_cost , format_craft_cost

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("encyclopedie"))
        else:
            return render(request, "dofustock/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "dofustock/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("encyclopedie"))

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

def item_detail(request, ankama_id):
    try:
        item = Item.objects.get(ankama_id=ankama_id)
        
        # Get the latest price for this item
        try:
            latest_price = item.prices.latest('date_updated')
            if latest_price.price is not None:
                if latest_price.price == 0:
                    item.price = "No Data"
                else:
                    # Format with spaces
                    price_int = int(latest_price.price)
                    item.price = f"{price_int:,}".replace(',', ' ')
            else:
                item.price = "N/A"
        except:
            item.price = "N/A"
            
        # Get craftlist for the current user
        craftlist = set()
        if request.user.is_authenticated:
            user_craftlist, _ = Craftlist.objects.get_or_create(user=request.user)
            craftlist = set(user_craftlist.item.values_list("ankama_id", flat=True))
        
        # Sanitize filename
        item.sanitized_name = sanitize_filename(item.name)
        
        # Fetch recipes with full resource details
        recipes = []
        total_craft_cost, all_prices_available = calculate_craft_cost(item)
        
        for recipe in item.recipes.all():
            recipe_dict = {
                'resource_id': recipe.resource_id,
                'resource_name': recipe.resource_name,
                'quantity': recipe.quantity,
            }
            
            # Try to find the resource item
            try:
                resource_item = Item.objects.get(ankama_id=recipe.resource_id)
                recipe_dict['resource_image'] = f"/media/IMG/{resource_item.category}/{resource_item.item_type}/{resource_item.ankama_id}-{sanitize_filename(resource_item.name)}.png"
                
                # Get the latest price for this resource
                try:
                    resource_price = resource_item.prices.latest('date_updated')
                    if resource_price.price is not None:
                        if resource_price.price == 0:
                            recipe_dict['unit_price'] = "No Data"
                            recipe_dict['total_price'] = "No Data"
                        else:
                            # Store the numeric values
                            unit_price = int(resource_price.price)
                            total_price = unit_price * recipe.quantity
                            
                            # Format prices
                            recipe_dict['unit_price'] = f"{unit_price:,}".replace(',', ' ')
                            recipe_dict['total_price'] = f"{total_price:,}".replace(',', ' ')
                    else:
                        recipe_dict['unit_price'] = "N/A"
                        recipe_dict['total_price'] = "N/A"
                except:
                    recipe_dict['unit_price'] = "N/A"
                    recipe_dict['total_price'] = "N/A"
                    
            except Item.DoesNotExist:
                recipe_dict['resource_image'] = '/media/IMG/equipment/Outil/489-Loupe.png'
                recipe_dict['unit_price'] = "N/A"
                recipe_dict['total_price'] = "N/A"
            
            recipes.append(recipe_dict)
        
        # Format the total craft cost
        item.craft_cost = format_craft_cost(total_craft_cost, all_prices_available)
        
        effects = list(item.effects.values())
        
        return render(request, "dofustock/item.html", {
            'item': item,
            'effects': effects,
            'recipes': recipes,
            'craftlist': craftlist,
        })
    except Item.DoesNotExist:
        return HttpResponseRedirect(reverse("encyclopedie"))
    
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
    
    # Convert to list and add price and craft cost info
    items_list = list(items)
    for item in items_list:
        # Add regular price
        try:
            latest_price = Price.objects.filter(item_id=item['id']).latest('date_updated')
            item['price'] = str(latest_price.price)
        except:
            item['price'] = "N/A"
        
        # Calculate craft cost
        try:
            item_obj = Item.objects.get(id=item['id'])
            total_craft_cost, all_prices_available = calculate_craft_cost(item_obj)
            item['craft_cost'] = format_craft_cost(total_craft_cost, all_prices_available)
        except:
            item['craft_cost'] = "N/A"
    
    return JsonResponse(items_list, safe=False)

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
    
    # Convert to list and add price and craft cost info
    items_list = list(items.values())
    for item in items_list:
        # Add regular price
        try:
            latest_price = Price.objects.filter(item_id=item['id']).latest('date_updated')
            item['price'] = str(latest_price.price)
        except:
            item['price'] = "N/A"
        
        # Calculate craft cost
        try:
            item_obj = Item.objects.get(id=item['id'])
            total_craft_cost, all_prices_available = calculate_craft_cost(item_obj)
            item['craft_cost'] = format_craft_cost(total_craft_cost, all_prices_available)
        except:
            item['craft_cost'] = "N/A"
    
    return JsonResponse(items_list, safe=False)

def get_items_recipe(request, ankama_id):
    try:
        # Use the path parameter directly
        item = Item.objects.get(ankama_id=ankama_id)
        
        # Get the latest price
        try:
            latest_price = item.prices.latest('date_updated')
            price = latest_price.price
        except:
            price = None
        
        effects = list(item.effects.values())
        recipes = list(item.recipes.values())
        
        # Combine item data with related data
        item_data = item.__dict__
        item_data.pop('_state', None)  
        item_data['effects'] = effects
        item_data['recipes'] = recipes
        item_data['price'] = price
        
        return JsonResponse(item_data)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
   
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

def craft_list(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    craftlist, _ = Craftlist.objects.get_or_create(user=request.user)
    items = craftlist.item.all()
    
    # Process items and their recipes
    items_with_recipes = []
    
    # Dictionary to track total resources needed
    total_resources = {}
    
    total_hdv_price = 0
    can_calculate_hdv_total = True

    for item in items:
        # Get the latest price for this item
        try:
            latest_price = item.prices.latest('date_updated')
            if latest_price.price is not None:
                if latest_price.price == 0:
                    item_price = "No Data"
                    can_calculate_hdv_total = False
                else:
                    # Format with spaces - same as in item_detail
                    price_int = int(latest_price.price)
                    item_price = f"{price_int:,}".replace(',', ' ')

                    total_hdv_price += price_int
            else:
                item_price = "N/A"
                can_calculate_hdv_total = False
        except:
            item_price = "N/A"
            can_calculate_hdv_total = False
            
        total_craft_cost, all_prices_available = calculate_craft_cost(item)
        craft_cost = format_craft_cost(total_craft_cost, all_prices_available)

        item_data = {
            'ankama_id': item.ankama_id,
            'name': item.name,
            'category': item.category,
            'item_type': item.item_type,
            'level': item.level,
            'price': item_price,
            'craft_cost': craft_cost,
            'sanitized_name': sanitize_filename(item.name),
            'recipes': []
        }
        
        # Process recipes for this item
        for recipe in item.recipes.all():
            recipe_dict = {
                'quantity': recipe.quantity,
                'resource_name': recipe.resource_name,
                'resource_id': recipe.resource_id
            }
            
            # Try to find the resource item
            try:
                resource_item = Item.objects.get(ankama_id=recipe.resource_id)
                resource_image = f"/media/IMG/{resource_item.category}/{resource_item.item_type}/{resource_item.ankama_id}-{sanitize_filename(resource_item.name)}.png"
                recipe_dict['resource_image'] = resource_image
                
                # Get resource price if available
                try:
                    resource_price_obj = resource_item.prices.latest('date_updated')
                    if resource_price_obj.price is not None:
                        if resource_price_obj.price == 0:
                            recipe_dict['resource_price'] = "No Data"
                            recipe_dict['total_price'] = "No Data"
                        else:
                            # Format resource price with spaces
                            price_int = int(resource_price_obj.price)
                            recipe_dict['resource_price'] = f"{price_int:,}".replace(',', ' ')
                            # Calculate and format total price (price * quantity)
                            total_price = price_int * recipe.quantity
                            recipe_dict['total_price'] = f"{total_price:,}".replace(',', ' ')
                    else:
                        recipe_dict['resource_price'] = "N/A"
                        recipe_dict['total_price'] = "N/A"
                except:
                    recipe_dict['resource_price'] = "N/A"
                    recipe_dict['total_price'] = "N/A"
                
                # Add to total resources
                resource_key = str(recipe.resource_id)
                if resource_key not in total_resources:
                    total_resources[resource_key] = {
                        'resource_id': recipe.resource_id,
                        'resource_name': recipe.resource_name,
                        'quantity': 0,
                        'resource_image': resource_image,
                        'resource_price': recipe_dict['resource_price']
                    }
                total_resources[resource_key]['quantity'] += recipe.quantity
                
            except Item.DoesNotExist:
                recipe_dict['resource_image'] = '/media/IMG/equipment/Outil/489-Loupe.png'
                recipe_dict['resource_price'] = "N/A"
                
                # Add to total resources even if resource item not found
                resource_key = str(recipe.resource_id)
                if resource_key not in total_resources:
                    total_resources[resource_key] = {
                        'resource_id': recipe.resource_id,
                        'resource_name': recipe.resource_name,
                        'quantity': 0,
                        'resource_image': '/media/IMG/equipment/Outil/489-Loupe.png',
                        'resource_price': "N/A"
                    }
                total_resources[resource_key]['quantity'] += recipe.quantity
                
            item_data['recipes'].append(recipe_dict)
            
        items_with_recipes.append(item_data)
    
    # Convert total_resources dictionary to a list for the template
    all_resources = list(total_resources.values())
    
    # Calculate total price of all resources if possible
    total_cost = 0
    can_calculate_total = True
    
    for resource in all_resources:
        if resource['resource_price'] != "N/A" and resource['resource_price'] != "No Data":
            try:
                # Extract numeric value from formatted price string
                numeric_price = float(resource['resource_price'].replace(' ', ''))
                resource_cost = numeric_price * resource['quantity']
                resource['total_cost'] = resource_cost
                total_cost += resource_cost
            except (ValueError, TypeError):
                can_calculate_total = False
                resource['total_cost'] = "N/A"
        else:
            can_calculate_total = False
            resource['total_cost'] = "N/A"
    
    # Format the total costs of individual resources
    for resource in all_resources:
        if resource['total_cost'] != "N/A":
            # Format with spaces
            resource['total_cost'] = f"{int(resource['total_cost']):,}".replace(',', ' ')
    
    # Format the grand total cost
    if can_calculate_total:
        total_cost_formatted = f"{int(total_cost):,}".replace(',', ' ')
    else:
        total_cost_formatted = "N/A"
    
    # Format the total HDV price
    if can_calculate_hdv_total:
        total_hdv_price_formatted = f"{int(total_hdv_price):,}".replace(',', ' ')
    else:
        total_hdv_price_formatted = "N/A"

        numeric_total_cost = None
    numeric_hdv_price = None
    
    if total_cost_formatted != "N/A":
        numeric_total_cost = int(total_cost)
    
    if total_hdv_price_formatted != "N/A":
        numeric_hdv_price = int(total_hdv_price)
    
    # Determine which price is better
    price_comparison = None
    if numeric_total_cost is not None and numeric_hdv_price is not None:
        if numeric_total_cost > numeric_hdv_price:
            price_comparison = "hdv_better"  # HDV price is lower (better)
        elif numeric_total_cost < numeric_hdv_price:
            price_comparison = "craft_better"  # Craft price is lower (better)
        else:
            price_comparison = "equal"

    return render(request, "dofustock/craft_list.html", {
        "items": items_with_recipes,
        "craftlist": set(items.values_list("ankama_id", flat=True)),
        "all_resources": all_resources,
        "total_cost": total_cost_formatted,
        "total_hdv_price": total_hdv_price_formatted,
        "price_comparison": price_comparison 
    })

def toggle_craftlist(request, ankama_id):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, ankama_id=ankama_id)  
        craftlist, _ = Craftlist.objects.get_or_create(user=request.user)
        
        if item in craftlist.item.all():
            craftlist.item.remove(item)
            status = 'removed'
        else:
            craftlist.item.add(item)
            status = 'added'
        
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_ajax:
            return JsonResponse({'status': status, 'item_id': ankama_id})
        
        # If not AJAX, redirect as before
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    
    # If not authenticated and it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    return redirect("login")
