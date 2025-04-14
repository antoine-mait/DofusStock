from django.contrib import admin
from django.db import models
from django.contrib.admin import widgets
from .models import User, Item, Effect, Recipe, Craftlist , Price
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin

# First, register the standard inlines and admin classes

class EffectInline(admin.TabularInline):
    model = Effect
    extra = 1
    readonly_fields = ['description']
    fields = ['description']

class RecipeInline(admin.TabularInline):
    model = Recipe
    extra = 1

class PriceInline(admin.TabularInline):
    model = Price
    extra = 1
    fields = ['price', 'date_updated']
    readonly_fields = ['date_updated']

class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'ankama_id', 'category', 'item_type', 'level', 'get_latest_price']
    search_fields = ['name', 'ankama_id']
    list_filter = ['category', 'item_type', 'level', 'is_weapon']
    readonly_fields = ['description_display']
    fieldsets = [
        (None, {'fields': ['ankama_id', 'name', 'category', 'item_type', 'level', 'is_weapon', 'image_url']}),
        ('Description', {'fields': ['description_display']}),
    ]
    inlines = [EffectInline, RecipeInline, PriceInline]
    
    def description_display(self, obj):
        return obj.description
    description_display.short_description = 'Item Description'

    def get_latest_price(self, obj):
        latest_price = obj.prices.order_by('-date_updated').first()
        if latest_price:
            return f"{latest_price.price}"
        return "No price"
    get_latest_price.short_description = 'Current Price'

class CraftlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items']
    filter_horizontal = ['item']
    
    def get_items(self, obj):
        return ", ".join([item.name for item in obj.item.all()])
    
    get_items.short_description = 'Items in Craftlist'
    
    search_fields = ['user__username']
    autocomplete_fields = ['item']

# Now handle the User admin customization

class CraftlistInline(admin.StackedInline):
    model = Craftlist
    filter_horizontal = ['item']
    can_delete = False
    verbose_name_plural = 'Craftlist'

class CustomUserAdmin(UserAdmin):
    inlines = UserAdmin.inlines + (CraftlistInline,)
    list_display = UserAdmin.list_display + ('view_craftlist',)
    
    def view_craftlist(self, obj):
        try:
            craftlist = Craftlist.objects.get(user=obj)
            url = reverse('admin:dofustock_site_craftlist_change', args=[craftlist.id])
            return format_html('<a href="{}">View Craftlist</a>', url)
        except Craftlist.DoesNotExist:
            return format_html('<span>No Craftlist</span>')
        
    view_craftlist.short_description = 'Craftlist'

# Register all models
admin.site.register(Item, ItemAdmin)
admin.site.register(Craftlist, CraftlistAdmin)
admin.site.register(Price)
# Register User with custom admin - instead of unregistering and re-registering
admin.site.register(User, CustomUserAdmin)