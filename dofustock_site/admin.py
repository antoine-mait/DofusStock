from django.contrib import admin
from .models import User, Item, Effect , Recipe , Craftlist

# Register User model
admin.site.register(User)
admin.site.register(Item)
admin.site.register(Effect)
admin.site.register(Recipe)
admin.site.register(Craftlist)
# Register your models here.
