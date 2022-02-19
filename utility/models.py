from django.db import models


# Create your models here.
class LocationStore(models.Model):
    name = models.CharField(max_length=255)
    lat = models.CharField(max_length=255)
    long = models.CharField(max_length=255)
    lga = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)
    name_id = models.IntegerField()
