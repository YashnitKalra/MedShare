from django.contrib import admin
from .models import *
import datetime
from django.utils.html import format_html

class General_User_Admin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "firstname", "lastname", "Area_Name", "Latitude", "Longitude","Requests_Remaining")

    def id(self, obj):
        return obj.User.id
    def username(self, obj):
        return obj.User.username
    def email(self, obj):
        return obj.User.email
    def firstname(self, obj):
        return obj.User.first_name
    def lastname(self, obj):
        return obj.User.last_name
    def latitude(self, obj):
        return obj.User.latitude
    def longitude(self, obj):
        return obj.User.longitude

class Medicinal_Product_Admin(admin.ModelAdmin):
    list_display = ("id", "Name", "Description", "donator_email", "Expiry_Date", "has_Expired", "Quantity")

    def donator_email(self, obj):
        return obj.General_User.User.email
    def has_Expired(self, obj):
        if obj.Expiry_Date > datetime.datetime.today().date():
            return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
        else:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')

class Donation_Admin(admin.ModelAdmin):
    list_display = ("Donation", "Medicinal_Product_ID", "Donator_Email", "Receiver_Email", "Quantity", "Date", "Status")

    def Donation(self, obj):
        return obj
    def Medicinal_Product_ID(self, obj):
        return obj.Medicinal_Product.id
    def Donator_Email(self, obj):
        return obj.Donator.User.email
    def Receiver_Email(self, obj):
        return obj.Receiver.User.email

# Register your models here.
admin.site.register(General_User, General_User_Admin)
admin.site.register(Medicinal_Product, Medicinal_Product_Admin)
admin.site.register(Donation, Donation_Admin)