# Create your views here.
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
import requests
import datetime as dt
import random as r
from .process import render_to_pdf
import pdfkit as p # install this first 
from swalook_backend.settings import BASE_DIR
from django.core.mail import send_mail
import jwt 
import json
from .serializer import *
from rest_framework.decorators import api_view,renderer_classes,APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer
from swalook_backend import settings
from twilio.rest import Client # install this first
from django.urls import reverse
from django.contrib.auth.hashers import make_password,check_password

# ''' api endpoints'''
# class Route(APIView):
#     def get(self,request): # endpoints to reach api 
        
#         self.route = [
#         '/api/',

#         '/api/user/signup/',

#         '/api/user/login/',

#         'api/user/user_data/<vendor_id>/<device_ids>',
        
#         '/api/user/add/invoice/<vendor_id>/',
     
#         '/api/user/add/appointments/<vendor_id>/',
        
#         '/api/user/appointment/search/',
       
#         ]

#         return Response({"Endpoints":self.route})

''' signup '''
class user_verify(APIView):  
    def post(self,request):
        a:int = r.randint(0,9) # random int combination for vendor_id
        b:int = r.randint(0,9)
        c:int = r.randint(0,9)

        data  = request.POST
        def validate(data=data):  # custom validator
            if len(data.get("password")) < 8:
                messages.info(request,"password: Minimum 8 Character Required")
                return True
            if data.get("password") != data.get("pwd"):
                messages.info(request,"Confirm password: not Matched")
                return True
            if "@" not in data.get('mobile'):

                if len(str(data.get("mobile"))) < 10:
                    messages.info(request,"enter a valid Mobile No")
                    return True
                if len(str(data.get("mobile"))) > 10:
                    messages.info(request,"enter a valid Mobile No")
                    return True
            else:
                return False
        v = validate()
        if v:
            return redirect(reverse("signup"))
        else:
            m_e                       = data.get("mobile")
            signup_obj                = User_data() 
            signup_obj.Name           = data.get("name")
            name_                     = str(signup_obj.Name)
            if "@" in m_e:
                signup_obj.email      = m_e
            else:
                signup_obj.MobileNo   = m_e                        
            signup_obj.Password       = make_password(data.get("pwd"))
            signup_obj.date_time      = dt.datetime.today()
            signup_obj.vendor_id      = name_[0:2] + str(a) + str(b) + str(c)
            get_ip                    = request.META.get('HTTP_X_FORWARDED_FOR')
            if get_ip:
                self.ip               = get_ip.split(',')[0]
            else:
                self.ip               = request.META.get('REMOTE_ADDR')
            signup_obj.ip             = self.ip
            signup_obj.reg_dev_id     = json.dumps([])
            signup_obj.dev_limit      = 1
            signup_obj.save()
            user                      = User.objects.create(username=m_e) # creating user object
            user.set_password(data.get('pwd'))
            user.save()
            a                         = r.randint(0,9) 
            b                         = r.randint(0,8)
            c                         = r.randint(0,7)
            d                         = r.randint(0,6)
            user_sign_in_data:dict = {
                'username':m_e,
                'password':signup_obj.Password,                
                'device_id':str(a)+str(b)+str(c)+str(d)
            }
            token                     = jwt.encode(user_sign_in_data, 'SECRET', algorithm='HS256')
            dev_id                    = signup_obj.reg_dev_id
            dev                       = json.decoder.JSONDecoder()
            device_id                 = dev.decode(dev_id)
            if len(device_id) == 0:
                device_id.append(token)
                signup_obj.reg_dev_id = json.dumps(device_id)
                signup_obj.save()
                request.session['id'] = data.get('mobile')
                cookie_ = redirect("/login")
                cookie_.set_cookie("device_id",value=token,max_age=315360000 * 5)
                return cookie_
            return redirect(reverse("signup"))

@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])       # rendering the signup Template
def signup_page(request):
    ''' it shows the signup page get method '''
    if request.user.is_authenticated:
        return redirect(reverse("dashboard"))
    return Response(template_name="signup.html") 


# this view is for responsible for verify the user login for both application and api
''' login '''
@api_view(['GET','POST'])
@renderer_classes([TemplateHTMLRenderer])    
def login_view_Create(request,*_token_):  # authenticating user login page view 
    ''' login view verify user and render login page 
    if user is verified then redirect to index'''
    if request.user.is_authenticated:
        return redirect(reverse("dashboard"))
    if request.method == "POST":
        data = request.data
        def validate(data=data):    # custom validator
            if len(data.get("password"))        < 8:
                messages.info(request,"password Minimum 8 Character Required")
                return True
                
            if "@" not in data.get("mobile"):
                if len(str(data.get("mobile"))) < 10:
                    messages.info(request,"enter a valid Mobile No")
                    return True
                if len(str(data.get("mobile"))) > 10:
                    messages.info(request,"enter a valid Mobile No")
                    return True
                    
                    
            if "@" in data.get("mobile"):
                if len(str(data.get("mobile"))) < 5:
                                
                    messages.info(request,"invalid email id")
                    return True
            else:
                return False
        v = validate()
        if v:
            return redirect(reverse("login"))
        else:
            username:str          = data.get("mobile")
            Password:str          = data.get("password")
            if "@" in username:
                signin_obj = User_data.objects.get(email=username)
            else:
                signin_obj = User_data.objects.get(MobileNo=username)
            if check_password(Password,signin_obj.Password):
                a                 = r.randint(0,9) 
                b                 = r.randint(0,8)
                c                 = r.randint(0,7)
                d                 = r.randint(0,6)
                user_sign_in_data = {
                    'username':username,
                    'password':Password,
                    'device_id':str(a)+str(b)+str(c)+str(d)}
                token             = jwt.encode(user_sign_in_data,'SECRET',algorithm='HS256')
                dev_id            = signin_obj.reg_dev_id
                dev               = json.decoder.JSONDecoder()
                device_id         = dev.decode(dev_id)
                if request.COOKIES.get("device_id") == None:
                    if len(device_id) < int(signin_obj.dev_limit):
                        device_id.append(token)
                        signin_obj.reg_dev_id = json.dumps(device_id)
                        signin_obj.save()
                        request.session['id'] = data.get('mobile')
                        user                  = auth.authenticate(username = username, password = Password)
                        if user is not None:
                            auth.login(request,user)
                            request.session['id']   = data.get('mobile')
                            request.session['name'] = str(request.user)
                            cookie_                 = redirect("login")
                            cookie_.set_cookie("device_id",value=token,max_age=315360000 * 5)
                            return cookie_
                    
                    elif int(signin_obj.dev_limit) == len(device_id):
                        return HttpResponse("<h1>Not Allowed</h1>")
                    
                    else:
                        pass


                else:
                    print("i am here")
                    dev__ = request.COOKIES.get("device_id")
                    if len(device_id) == 1:
                        if dev__ == device_id[0]:
                            user                             = auth.authenticate(username = username, password = Password)
                            if user is not None:
                                auth.login(request,user)
                                request.session['id']        = data.get('mobile')
                                request.session['name']      = str(request.user)
                                return redirect("/")
                    else:   
                        for device in device_id:
                            if dev__ == device:
                                user                         = auth.authenticate(username = username, password = Password)
                                if user is not None:
                                    auth.login(request,user)
                                    request.session['id']    = data.get('mobile')
                                    request.session['name']  = str(request.user)
                                    return redirect("/")
                            

            else:
                print("here")
                return redirect(reverse("login")) 
    return Response(template_name="login.html") 

''' dashboard and search '''
class dashboard(APIView):
    ''' showing the dash board with user data'''
    def __init__(self,):
        self.context:dict = {}
        self.g_data:str   = ""
        self.session_id   = None
        global ids
   
 
    def get(self,request,vendor_id=None,device_ids=None):
        ''' render the dash board of requested user with data'''
        
        self.session_id = request.session.get('name')
        if request.user.is_authenticated:
            try:

                if "@" in self.session_id:
                    signin_data        = User_data.objects.get(email=self.session_id)
                else:
                    signin_data        = User_data.objects.get(MobileNo=self.session_id)
                
                if "@" in self.session_id:
                        user_obj       =  signin_data
                else:
                        user_obj       = signin_data
                dev_id                 = signin_data.reg_dev_id
                dev                    = json.decoder.JSONDecoder()
                device_id              = dev.decode(dev_id)
                dev_uid                = request.COOKIES.get('device_id')
                leng                   = len(device_id)
                if int(signin_data.dev_limit) < int(leng):
                    if leng > 1:
                        for i in device_id:
                            if i == dev_uid:
                                ind            = device_id.index(i)
                                device_id.pop(ind)
                                
                        signin_data.reg_dev_id = json.dumps(device_id)
                        signin_data.save()
                        auth.logout(request)
                        return HttpResponse(request,'<h1>Session Expire</h1>')
                            
                else:
                    self.context["users"] = user_obj.Name
                    inv = Invoice.objects.filter(vendor_name=request.user)
                    for i in inv:
                        i.service_catg_name = i.service_catg_name.removeprefix("[")
                        i.service_catg_name = i.service_catg_name.removesuffix("]")
                        service             = i.service_catg_name
                        stri_data           = ""
                        
                        for j in service:
                            if j == "'":
                                pass
                            elif j == ",":
                                pass
                            else:
                                stri_data   = stri_data+j
                        i.service_catg_name = stri_data
                        i.save()
                            
                        
                    self.context["invoice_data"] = inv[::-1]
                    ap_obj = Apointment.objects.filter(user=request.user)
                    for i in ap_obj:
                        i.services               = i.services.removeprefix("[")
                        i.services               = i.services.removesuffix("]")
                        serv                     = i.services
                        stri_data                = ""
                        for j in serv:
                            if j == "'":
                                pass
                            elif j == ",":
                                pass
                            else:
                                stri_data        = stri_data+j
                        i.services               = stri_data
                        i.save()
                            
                        
                        
                    
                    ap_obj_len                   = len(ap_obj)
                    if ap_obj_len != 0:
                        if ap_obj_len >= 5:
                            ind_ex               = ap_obj_len - 5
                            dat_a:list           = []
                            for i in range(ind_ex,ap_obj_len):
                                dat_a.append(ap_obj[i])
                            self.context["ap_data"]                 = dat_a[::-1]
                            self.context["dialouge"]                = "5 Recents Appointments"
                            cookie_                                 = render(request,"profiledashboard.html",self.context)
                            cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
                            return cookie_
                        else:
                            self.context["ap_data"]                 = ap_obj [::-1]
                            self.context["dialouge"]                = "Upcoming Appointments"
                            cookie_                                 = render(request,"profiledashboard.html",self.context)
                            cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
                            return cookie_
                    else:
                                
                        self.context["ap_data"]                     = ap_obj
                        self.context["dialouge"]                    = "Upcoming Appointments"
                        cookie_                                     = render(request,"profiledashboard.html",self.context)
                        cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
                        return cookie_
                
            except Exception as e:
                print(e)
    
        return redirect(reverse("signup"))

                
    def search_result(self,request):
        ''' search view for perform search in a post method and show the data in get method '''
        
        self.session_id = request.session.get('name')
        if request.user.is_authenticated:

            c_h                          = request.POST.get("search")
            if c_h == None:
                data                     = self.g_data
            else:
                data                     = c_h
    
            ap_obj                       =  Apointment.objects.filter(user= request.user)
            self.ap_objs                 = ap_obj.all().filter(contact_number = data)
            self.context["dialouge"]     = "Search Result"
            self.context["invoice_data"] = Invoice.objects.filter(vendor_name= request.user)
            self.context["ap_data"]      = self.ap_objs

            cookie_                      = redirect(reverse("search_data"))
            cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
            return cookie_
                #return render(request,"profiledashboard.html",self.context)
        return redirect(reverse("login"))
    

    def show_search(self,request):
        ''' here the search data show '''
        if request.user.is_authenticated:
            self.session_id             = request.session.get('name')
            if "@" in self.session_id:
                    user_obj            =  User_data.objects.get(email=self.session_id)
            else:
                    user_obj            = User_data.objects.get(MobileNo=self.session_id)
            self.context["users"]       = user_obj.Name
            cookie_                     =  render(request,"profiledashboard.html",self.context)
            cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
            return cookie_
        return redirect(reverse("login"))


    def nav(self,request,navs=None):
        ''' for bottom nav bar '''
        if navs                         ==  "profiledashboard":
            return redirect(reverse("dashboard"))

        elif navs                       == "index":
            return redirect(reverse("index"))
        elif navs                       == "generatebill":
            return redirect(reverse("generate_bill"))
        elif navs                       == "appointment":
            return redirect(reverse("appointment"))
        elif navs                       == "search":
           self.g_data                   = request.POST.get("search")
           return redirect(reverse("search"))
           
        elif navs                       == "/":
            return redirect(reverse("dashboard"))

        else:
            pass



''' invoice generate '''
class generate_bill(APIView):      # invoice generator class
    ''' render and recieve bill data and show invoice'''
    def __init__(self):
        self.invoice_obj            = None
        self.context:dict           = {} 
        self.billno                 = None
        self.count:int              = 0
        self.inner_context:dict     = {}
    def get(self,request):   # rendering bill
        ''' render the billing form '''
        if request.user.is_authenticated:
            service_datas           = Service_data.objects.all()
            context = {}
            context['service_list'] = service_datas
            if request.method == 'POST':
                return redirect("/invoice")
            cookie_                 = render(request,"bill_index.html",context)
            cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
            return cookie_
        return redirect(reverse("login"))
        
    def post_bill(self,request,vendor_name=None):   # retrive data and save method
        ''' taking post request and save the data to db and redirect to invoice with get method'''
        if request.user.is_authenticated:
            
            if request.method == 'POST':
                user                         = request.session.get('name')
                if "@" in user:
                    self.user_obj            = User_data.objects.get(email=user)
                else:
                    self.user_obj            = User_data.objects.get(MobileNo=user)
                self.user_obj.invoice_number = self.user_obj.invoice_number + 1
                self.user_obj.save()
                seri                         = dt.datetime.now()
                m_                           = seri.strftime("%m")
                y_                           = seri.strftime("%y")
                data                         = request.POST
                def validate(data=data):  
                        
                    
                    if len(data.get("mobile")) < 10:
                        messages.info(request,"MobileNo: 10digit Required")
                        return True
                    if len(data.get("mobile")) > 10:
                        messages.info(request,"MobileNo: 10digit Required")
                        return True
                    if type(data.get("mobile")) == "str":
                        messages.info(request,"Invalid Mobile No")
                        return True
                    
                    else:
                        return False
                v = validate()
                
                if v:
                    return redirect(reverse("generate_bill"))
                else:
                    self.invoice_obj                    = Invoice()
                    self.invoice_obj.Name               = request.POST.get("f_name")
                    self.invoice_obj.Address            = request.POST.get("address")
                    self.invoice_obj.Mobileno           = request.POST.get("mobile")
                    self.invoice_obj.email              = request.POST.get("email")
                    self.invoice_obj.service_catg_name  = request.POST.getlist("select")
                    self.invoice_obj.service_by         = request.POST.get("served_by")
                    self.invoice_obj.date_time          = dt.datetime.today()
                    self.invoice_obj.vendor_name        = request.user
                    v_id                                = str(self.user_obj.vendor_id)
                    slno                                = v_id.lower() + str(self.user_obj.invoice_number) + str(m_) + str(y_)
                    self.invoice_obj.slno               = slno
                    data_list                           = request.POST.getlist("select")
                    self.invoice_obj.total              = 0
                    i                                   = 0
                    for j in data_list:
                        serv_obj                        = store_invoice_data_service()
                        serv_obj.service                = j
                        serv_obj.slnoo                  = i + 1
                        self.serv                       = Service_data.objects.get(service=j)
                        serv_obj.prise                  = self.serv.service_prise
                        serv_obj.slno                   = self.invoice_obj.slno
                        
                        serv_obj.discount               = (int(serv_obj.prise)*int(request.POST.get('discount')))/100
                        
                        serv_obj.total                  = int(serv_obj.prise) - int(serv_obj.discount)
                        serv_obj.save()
                        self.invoice_obj.total          = int(self.invoice_obj.total) + int(serv_obj.total)
                        i                               = i+1 
                    self.invoice_obj.Discont            = request.POST.get('discount')
                    if request.POST.get("gst"):
                        self.invoice_obj.c_gst          = int(self.invoice_obj.total*9)/100
                        self.invoice_obj.s_gst          = self.invoice_obj.c_gst    
                    else:
                        self.invoice_obj.c_gst          = 0
                        self.invoice_obj.s_gst          = 0       
                    self.invoice_obj.grand_total        = self.invoice_obj.total+self.invoice_obj.c_gst
                    self.invoice_obj.grand_total        = self.invoice_obj.grand_total + self.invoice_obj.s_gst
                    self.invoice_obj.prise              = self.invoice_obj.grand_total
                    self.invoice_obj.save()
                    s_obj                               = store_invoice_data_service.objects.filter(slno=self.invoice_obj.slno)
                    self.context["service_obj"]         =  s_obj
                    self.context["invoice_data"]        = Invoice.objects.get(slno=self.invoice_obj.slno)
                    return redirect(reverse("invoice_"))
        
    def show_invoice(self,request):
        ''' showing  the created invoice '''
        cookie_                                         =  render(request,"invoice.html",self.context)
        cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
        return cookie_
    

''' appointment '''        
class appointmnet(APIView):
    ''' Appointment class render and featch data '''
    def __init__(self):
        pass          

    def post(self,request):
        if request.user.is_authenticated:
     
            data = request.POST
            def validate(data=data):  
                if len(data.get("l_name")) < 10:
                        messages.info(request,"MobileNo: 10digit Required")
                        return True
                if len(data.get("l_name")) > 10:
                        messages.info(request,"MobileNo: 10digit Required")
                        return True
                else:
                    return False
            v = validate()
            if v:
                return redirect(reverse("appointment"))
            else:
                ap_obj                = Apointment()
                ap_obj.user           = request.user
                ap_obj.customer_name  = request.POST.get('f_name')
                ap_obj.contact_number = request.POST.get('l_name')
                ap_obj.booking_date   = request.POST.get('datetime')
                hrs                   = request.POST.get('hrs')
                mins                  = request.POST.get('mins')
                meridian              = request.POST.get('meridian')
                time_                 = hrs+mins+meridian
                ap_obj.booking_time   = time_

                
                a                     = r.randint(0,9) # generating random int for users
                b                     = r.randint(0,9)
                c                     = r.randint(0,9)
                uniquee               = str(a) + str(b) + str(c)
                data_list             = request.POST.getlist('select')
        
                for j in data_list:
                    serv_obj          = store_app_service_data()
                    serv_obj.service  = j
                    serv_obj.slnoo    = ap_obj.contact_number + uniquee
                    serv_obj.save()
                    
                ap_obj.email          = request.POST.get('email')
                dst                   = store_app_service_data.objects.filter(slnoo=ap_obj.contact_number+uniquee)
                ap_obj.services       = []
                for i in dst:
                    ap_obj.services.append(i.service)
                ap_obj.save()
                return redirect(reverse("dashboard"))
    
    def get(self,request):
        if request.user.is_authenticated:
            service_datas = Service_data.objects.all()
            context = {}
            context['service_data'] = service_datas
            cookie_ =  render(request,"appointment.html",context)
            cookie_.set_cookie("device_id",value=request.COOKIES.get("device_id"),max_age=315360000 * 5)
            return cookie_
        return redirect(reverse("signup"))


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer]) 
def show_landing_page(request):      # showing index page
    ''' showing index page'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            pass
        return Response(template_name="index.html")



''' pdf '''            
class GeneratePdf(APIView):
    ''' generate the invoice pdf '''
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # getting the template
            inv_obj                      =  Invoice.objects.last()
            data                         = inv_obj.service_catg_name
            data                         = inv_obj.service_catg_name.removeprefix("[")
            data                         = inv_obj.service_catg_name.removesuffix("]")
            service                      = data
            stri_data                    = ""
                    
            for j in service:
                if j == "'":
                    pass
                elif j == ",":
                    pass
                else:
                    stri_data            = stri_data+j
            data                         = stri_data
            inv_obj.service_catg_name    = data
            inv_obj.save()
            wkhtml_path                  = p.configuration(wkhtmltopdf=settings.WKHTML2PDF_PATH)   # wkhtml path              
            p_df                         = p.from_url('127.0.0.1:8000/invoice/',output_path= BASE_DIR / 'media/pdf/invoice{}.pdf'.format(inv_obj.slno),configuration=wkhtml_path)
            
            context_dict                 = {}
            context_dict["invoice_data"] =  inv_obj
    
            pdf                          = render_to_pdf('invoice_pdf.html',context_dict)
            
                # rendering the template
            return HttpResponse(pdf, content_type='application/pdf')
            
        return redirect(reverse("signup"))

''' share pdf'''            
def share_pdf(request):
    ''' sharing the pdf '''
    return HttpResponse("<h1>Under Construction</h1>")
    

''' user manager '''
class set_session_admin:
    # it is a view from where admin can handle the user login devcie limit
    def show_session_page(self,request):
        if request.user.is_authenticated:
            user_obj             = User.objects.get(username=str(request.user))
            if user_obj.is_staff:
                sess_ion_obj     = User_data.objects.all()
                return render(request,"user_manager.html",{'data':sess_ion_obj})
        return HttpResponse("<h1> You Are Not Authorized for this page</h1>")


    def save_device_limit(self,request,user):
        if "@" in user:
            token_obj                   = User_data.objects.get(email=user)
            if int(request.POST.get('devicelimit')) < int(token_obj.dev_limit):
                if int(token_obj.dev_limit) - int(request.POST.get('devicelimit')) == 1:
                    token_obj.dev_limit = int(request.POST.get('devicelimit'))
                    messages.info(request,"{} Device Limit is Updated To {}".format(token_obj.email,token_obj.dev_limit))
                else:
                    messages.info(request,"only one device can be add or remove at a time")
                    return redirect(reverse("user"))

            else:
                if int(request.POST.get('devicelimit'))-int(token_obj.dev_limit) == 1:
                    token_obj.dev_limit = request.POST.get('devicelimit')
                    messages.info(request,"{} Device Limit is Updated To {}".format(token_obj.email,token_obj.dev_limit))

                else:
                    messages.info(request,"only one device can be add or remove at a time")
                    return redirect(reverse("user"))

            token_obj.save()
            return redirect(reverse("user"))
        else:
            token_obj                   = User_data.objects.get(MobileNo=user)
            if int(request.POST.get('devicelimit')) < int(token_obj.dev_limit):
                if int(token_obj.dev_limit) - int(request.POST.get('devicelimit')) == 1:
                    token_obj.dev_limit = int(request.POST.get('devicelimit'))
                    messages.info(request,"{} Device Limit is Updated To {}".format(token_obj.MobileNo,token_obj.dev_limit))
                else:
                    messages.info(request,"only one device can be add or remove at a time")
                    return redirect(reverse("user"))

            else:
                if int(request.POST.get('devicelimit'))-int(token_obj.dev_limit) == 1:
                    token_obj.dev_limit = request.POST.get('devicelimit')
                    messages.info(request,"{} Device Limit is Updated To {}".format(token_obj.MobileNo,token_obj.dev_limit))
                else:

                    messages.info(request,"only one device can be add or remove at a time")
                    return redirect(reverse("user"))

            token_obj.save()
            return redirect(reverse("user"))



''' password change '''
class change_password:
    def __init__(self):
        self.otp  = None
        self.name = None

    def forgot_password(self,request):
        if request.user.is_authenticated:
            return redirect("/")
        if request.method == 'POST':
            data                      = request.POST
            User.objects.get(username = data.get('f_pass'))
            if "@" in data.get('f_pass'):
                    pass
            else:
                self.otp              = data.get('f_pass')
                self.name             = self.otp
                url                   = "https://verificationapi-v1.sinch.com/verification/v1/verifications"
                payload               ="{\n  \"identity\": {\n  \"type\": \"number\",\n  \"endpoint\": \"+91%s\"\n  },\n  \"method\": \"sms\"\n}" % data.get('f_pass')
                headers               = {
                    'Content-Type': 'application/json',
                    'Authorization': settings.API_SINCH_KEY,
                }
                response              = requests.request("POST", url, headers=headers, data=payload)
                return redirect(reverse("otp_get"))
        return render(request,"forgot_password.html")


    def get_otp(self,request):
        if request.method == 'POST':
            data     = request.POST
            url      = "https://verificationapi-v1.sinch.com/verification/v1/verifications/number/+91%s" % self.otp
            payload  ="{ \"method\": \"sms\", \"sms\":{ \"code\": \"%s\" }}" % str(data.get('otp'))
            headers  = {
            'Content-Type': 'application/json',
            'Authorization': settings.API_SINCH_KEY,
            }
            response = requests.request("PUT", url, headers=headers, data=payload)
            datas    = response.json()
            if datas.get('status') == 'SUCCESSFUL':
                return redirect(reverse("reset_password"))
            else:
                return redirect(reverse("otp_get"))
        return render(request,"token.html")

    def get(self,request):
        if request.user.is_authenticated:
            return redirect(reverse("dashboard"))
        return render(request,"new_password.html")


    def post(self,request):
        if request.user.is_authenticated:
            return redirect(reverse("dashboard"))
        data  = request.POST
        pwd   = data.get("pwd")
        c_pwd = data.get("pwd2")
       
        if pwd == c_pwd:
                
            if "@" in self.name:
                sign_up = User_data.objects.get(email=self.name)
                   
            else:
                sign_up = User_data.objects.get(MobileNo=self.name)
                 
            sign_up.Password = make_password(c_pwd)
            sign_up.save()  
            user_obj         = User.objects.get(username=self.name)
            user_obj.set_password(c_pwd)
            user_obj.save()
            
            return HttpResponse("<h1>Password Change Sucessfully</h1>")
            
        else:
            return redirect(reverse("reset_password"))

class geo_locate:
    def __init__(self):
        self.lati             = None
        self.longi            = None
        self.ip               = None


    def get_ip(self,request):
        get_ip                = request.META.get('HTTP_X_FORWARDED_FOR')
        if get_ip:
            self.ip           = get_ip.split(',')[0]
        else:
            self.ip           = request.META.get('REMOTE_ADDR')
        return self.ip


    def get_lat_long(self,request,ip=get_ip):
        get_ip                 = ip(self,request)
        api_key                = settings.GEO_LOCATION_KEY
        response               = requests.get("https://ipgeolocation.abstractapi.com/v1/?api_key="+api_key+"&ip_address="+get_ip)
        return redirect(reverse("dashboard"))


       
class vendor_service_add(APIView):
    def post(self,request,vendor_id=None):
       
        data                   =  request.POST
        serv_ice               = Service_data()
        serv_ice.service       = data.get("service")
        serv_ice.service_prise = data.get("price")
        serv_ice.save()
        return redirect(reverse("dashboard"))

    def get(self,request):
        if request.META.get("CONTENT_TYPE") == "application/json":
            service_data        = Service_data.objects.filter(user=str(request.user))
            serializer          = vendor_service_serializer(service_data,many=True)
            data                = JSONRenderer().render(serializer.data)
            return Response({
                "status":True,
                "data":data

            })
        return render(request,"addService.html")

