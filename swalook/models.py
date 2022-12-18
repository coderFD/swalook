from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class User_data(models.Model):   # model instance for store signup objects
    
    Name               = models.CharField(max_length=1000,)
    MobileNo           = models.CharField(max_length=10,null=True,blank=True)
    email              = models.EmailField()
    Password           = models.CharField(max_length=1000,)
    id                 = models.AutoField(primary_key=True,editable=False)
    invoice_number     = models.IntegerField(default=0,null=True,editable=True) # generated invoice count of each user
    date_time          = models.DateTimeField(auto_now_add=False,null=True)
    vendor_id          = models.CharField(null=False,max_length=6) # id of vendor [note that vendor name and id are not same]
    ip                 = models.CharField(max_length=200,null=True,blank=True)
    reg_dev_id         = models.TextField() # register device ids
    dev_limit          = models.CharField(max_length=20,null=True,blank=True) # device limit
    
    def __str__(self):
        return str(self.Name)


class Client_service_data(models.Model):
    
    vendor_name        = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    Name               = models.CharField(max_length=20,)
    Address            = models.CharField(max_length=100,)
    Mobileno           = models.CharField(max_length=12,)
    email              = models.CharField(max_length=50,)
    service_catg_name  = models.CharField(max_length=100,)
    date_time          = models.DateTimeField(auto_now_add=False,null=True)
    id                 = models.AutoField(primary_key=True,editable=False)
    prise              = models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    service_by         = models.CharField(max_length=20,)
    
    def __str__(self):
        return str(self.Name)

class Invoice(Client_service_data): # model instance for store invoice objects

    Discont     = models.BigIntegerField(null=True,blank=True)
    total       = models.BigIntegerField(null=True,blank=True)
    slno        = models.CharField(max_length=20,null=True,blank=True)
    s_gst       = models.BigIntegerField(null=True,blank=True)
    c_gst       = models.BigIntegerField(null=True,blank=True)  
    grand_total = models.BigIntegerField(null=True,blank=True)

    def __str__(self):
        return str(self.vendor_name)

class Apointment(models.Model):  # model objects for store appointments 
    
    user           = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    customer_name  = models.CharField(max_length=100,null=True,blank=True)
    contact_number = models.CharField(max_length=15,null=True,blank=True)
    email          = models.CharField(max_length=100,null=True,blank=True)
    services       = models.CharField(max_length=100,null=True,blank=True)
    price          = models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    booking_date   = models.DateField(auto_now_add=False,null=True)
    booking_time   = models.CharField(max_length=100,null=True,blank=True)
    id             = models.AutoField(primary_key=True,editable=False)
    
    def __str__(self):
        return str(self.customer_name)

class Service_data(models.Model): # model object for store available services of indivisual user
    
    #user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    service        = models.CharField(max_length=30)
    service_prise  = models.CharField(max_length=30)

    def __str__(self):
        return str(self.service)
  

class store_invoice_data_service(models.Model): # model object for store invoice selected services 
    
    service  = models.CharField(max_length=30)
    slnoo    = models.IntegerField(null=True,blank=True) # indexing the selected service of each user
    prise    = models.IntegerField(null=True,blank=True)
    slno     = models.CharField(max_length=30) # slno of invoice
    total    = models.BigIntegerField(null=True,blank=True)
    discount = models.IntegerField(null=True,blank=True)
    
    def __str__(self):
        return str(self.slno)

class store_app_service_data(models.Model): # model object for store appointment selected services 

    service  = models.CharField(max_length=30)
    slnoo    = models.IntegerField(null=True,blank=True) # indexing the selected service of each user
    
    def __str__(self):
        return str(self.slnoo)






    

