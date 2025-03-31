from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Item(models.Model):
    ankama_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    item_type = models.CharField(max_length=50)
    level = models.IntegerField()
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=255, blank=True)
    is_weapon = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} / {self.ankama_id} / {self.category} / {self.item_type} / {self.level}"
    
class Effect(models.Model):
    item = models.ForeignKey(Item, related_name='effects', on_delete=models.CASCADE, default=1)
    description = models.TextField()

    def __str__(self):
            return f"effect of {self.item.name}"

class Recipe(models.Model):
    item = models.ForeignKey(Item, related_name='recipes', on_delete=models.CASCADE, default=1)  # Assuming ID 1 exists
    resource_id = models.IntegerField()
    resource_name = models.CharField(max_length=255)
    quantity = models.IntegerField()

    def __str__(self):
            return f"Recipe of {self.item.name}"
    
class Craftlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ManyToManyField(Item)

    def __str__(self):
        return f"Craft list of {self.user.username}"