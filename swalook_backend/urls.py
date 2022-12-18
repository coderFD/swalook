"""swalook_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from pathlib import Path
from django.contrib import admin
from django.urls import path

from swalook.views import *
from django.conf import settings
from django.conf.urls.static import static

bill_invoice = generate_bill()
user_ver = user_verify()
dashboards = dashboard()
appointments = appointmnet()
v_service = vendor_service_add()

#token = generate_token()
#token_verify = verify_token()
session_admin = set_session_admin()
change_pwd = change_password()
geo_loc= geo_locate()
urlpatterns = [
    # api urls
   #path("api/",Route.as_view()),
   #path("api/user/signup/",user_verify.as_view()),
   #path("api/user/login/",api_login.as_view()),
   
   #path("api/user/login/<_token_>/",api_login.as_view()),
   #path("api/user/user_data/<vendor_id>/<device_ids>",dashboards.as_view()),
   
   #path("api/user/add/appointment/<vendor_name>/",appointments.as_view()),
   #path("api/user/add/invoice/<vendor_name>/",bill_invoice.post_bill),
   
   #path("api/user/appointment/search/<contact_number>",search_appointment.as_view()),
   path('admin/', admin.site.urls),

   # application urls

   # signup & login urls
   path("signup/",signup_page, name= "signup"),
   path("signup/login/",login_view_Create, name= "signup-login"),
   path("login/",login_view_Create, name= "login"),
   path("createnew/",user_verify.as_view(), name= "create_account"), # private_url
   path("signup/createnew/",user_verify.as_view(), name= "signup/create-new"), # private_url
   
  
   # dashboard & serviceadd urls
   path("",dashboards.as_view(), name= "dashboard"),
   path("add/service/",vendor_service_add.as_view(), name= "add_service"),
   path("add/service/service_data/",v_service.post, name= "add_data"), # private url
   path("add/service/<navs>/",dashboards.nav, name= "add_service_nav"), # private url
 
   # login verification & forgot password urls & otp sent urls
   path("login/verify/password",change_pwd.forgot_password, name= "for_got_password"), 
   path("signup/login/verify/password",change_pwd.forgot_password, name="signup_forgot_password"),
   path("forgot_password",change_pwd.forgot_password, name="forgot"),
   path("reset_password",change_pwd.get, name= "reset_password"),
   path("set_password/",change_pwd.post, name= "set_password"), # private url
   path("otp-sent/",change_pwd.forgot_password, name= "otp_password"), # private url
   path("enter_otp/",change_pwd.get_otp, name= "otp_get"),
   path("verify/",change_pwd.get_otp,name= "otp_verify"), # private url
   
   # appointments and search urls and add service urls
   path("appointment/",appointments.as_view(), name= "appointment"),
   path("appointment/save/",appointments.as_view(), name= "ap_save"), # private_url
   path("appointment/<navs>/",dashboards.nav, name= "appointment_nav"), # private url
   path("search/",dashboards.search_result, name= "search"), # private_url
   path("data/",dashboards.show_search, name= "search_data") ,
   path("data/add/service/",vendor_service_add.as_view(), name= "search_data_page_nav") ,
   path("data/<navs>/",dashboards.nav, name= "search_nav"), # private_url
   
   # bill generate & invoice & pdf urls
   path("generatebill/invoice/",bill_invoice.post_bill, name= "invoice"), # private url
   path("invoice/",bill_invoice.show_invoice, name= "invoice_"),
   path("generatebill/",bill_invoice.as_view(), name= "generate_bill"),
   path("generatebill/<navs>/",dashboards.nav, name= "generate_bill_nav"), # private url
   path("invoice/invoice_/<slno>/",GeneratePdf.as_view(), name= "pdf"),  # private url
   path("invoice/send_msg/",share_pdf, name= "share_pdf"), # private url
   
   # index & device manage & ip geo location urls

   #path("generate_token/",token.get), # private url
   #path("token/",token_verify.show_token), 
   path("index/",show_landing_page, name= "index"),
   path("index/<navs>",dashboards.nav, name= "index_nav"), # private url
   path("user_manager/",session_admin.show_session_page, name= "user"), # user device limit setting url
   path("user_manager/update/<user>/",session_admin.save_device_limit, name= "update_user"), # private url
   path("ip/",geo_loc.get_lat_long, name= "ip"), # private url

   

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
