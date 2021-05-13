from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class General_User(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    Area_Name = models.CharField(max_length=100)
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    Requests_Remaining = models.IntegerField(default=3)

class Medicinal_Product(models.Model):
    General_User = models.ForeignKey(General_User, on_delete=models.CASCADE)
    Name = models.CharField(max_length=25)
    Description = models.CharField(max_length=70, default="")
    Expiry_Date = models.DateField()
    Quantity = models.IntegerField(default=1)

class Donation(models.Model):
    status = ((-2,"Unsuccessful"), (-1,"Rejected"), (0,"Pending"), (1,"Accepted"), (2,"Successful"))
    Medicinal_Product = models.ForeignKey(Medicinal_Product, on_delete=models.CASCADE)
    Donator = models.ForeignKey(General_User, on_delete=models.CASCADE, related_name="Donator")
    Receiver = models.ForeignKey(General_User, on_delete=models.CASCADE, related_name="Receiver")
    Date = models.DateField()
    Status = models.IntegerField(choices=status, default=0)
    Quantity = models.IntegerField(default=1)