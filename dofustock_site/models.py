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

    class Meta:
        managed = False  
        db_table = 'items' 
        app_label = 'dofustock_site'

    def save(self, *args, **kwargs):
        kwargs['using'] = 'dofus_items'
        return super().save(*args, **kwargs)

    @classmethod
    def objects(cls):
        return super().objects.using('dofus_items')

class Effect(models.Model):
    item = models.ForeignKey(Item, related_name='effects', on_delete=models.CASCADE)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'effects'
        app_label = 'dofustock_site'

    def save(self, *args, **kwargs):
        kwargs['using'] = 'dofus_items'
        return super().save(*args, **kwargs)

    @classmethod
    def objects(cls):
        return super().objects.using('dofus_items')

class Recipe(models.Model):
    item = models.ForeignKey(Item, related_name='recipes', on_delete=models.CASCADE)
    resource_id = models.IntegerField()
    resource_name = models.CharField(max_length=255)
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recipes'
        app_label = 'dofustock_site'

    def save(self, *args, **kwargs):
        kwargs['using'] = 'dofus_items'
        return super().save(*args, **kwargs)

    @classmethod
    def objects(cls):
        return super().objects.using('dofus_items')