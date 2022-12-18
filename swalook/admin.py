from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(User_data)
class User_data(admin.ModelAdmin):
    list_display = ['Name','vendor_id','MobileNo',"email"]

@admin.register(Apointment)
class appointment_data(admin.ModelAdmin):
    list_display = ['customer_name','user',]

@admin.register(Invoice)
class invoice_data(admin.ModelAdmin):
    list_display = ['Name','vendor_name',]

@admin.register(Service_data)
class service_data(admin.ModelAdmin):
    list_display = ["service","service_prise",]


