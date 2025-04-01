from django.contrib import admin
from .models import User, Item, Effect , Recipe , Craftlist

# Register User model
admin.site.register(User)
admin.site.register(Item)
admin.site.register(Effect)
admin.site.register(Recipe)
# Register your models here.


# Customized admin for Craftlist
class CraftlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items']
    filter_horizontal = ['item']  # This creates a better interface for the M2M relationship
    
    def get_items(self, obj):
        return ", ".join([item.name for item in obj.item.all()])
    
    get_items.short_description = 'Items in Craftlist'
    
    # If you want to add search functionality to the items selection
    search_fields = ['user__username']
    autocomplete_fields = ['item']  # Enables autocomplete for the item field
    
admin.site.register(Craftlist, CraftlistAdmin)

# To enable autocomplete on the Item model
class ItemAdmin(admin.ModelAdmin):
    search_fields = ['name', 'ankama_id']

# Re-register Item with the custom admin
admin.site.unregister(Item)
admin.site.register(Item, ItemAdmin)