from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
class Signup_Serializer(serializers.ModelSerializer):  # serializer for signup
    class Meta:
        model  = User_data
        fields = ["Name","MobileNo","Password"]
    def validate_MobileNo(self, request):
        _m_num = request     
        if len(str(_m_num)) < 10:
            raise serializers.ValidationError("Mobile Number MustBe 10 Digit")
        return request
    def validate_Password(self, request):
        _pwd   = request       
        if len(_pwd) < 8:
            raise serializers.ValidationError("Required 8 Digit")
        return request

class Invoice_serializers(serializers.ModelSerializer): # serializer for invoice
        class Meta:
            model     = Invoice
            fields    = '__all__'
        def validate_Mobileno(self, request):
            try:
                m_num = request
                if len(str(m_num)) < 10:
                    raise serializers.ValidationError("10 digit required")
                return request
            except Exception as e:
                print(e)
        def validate_email(self, request):
            try:
                email = request
                if "@" not in email:
                    raise serializers.ValidationError("invalid email-id")
                return request
            except Exception as e:
                print(e)
class appointment_serializer(serializers.ModelSerializer): # serializer for appointments

    class Meta:
        model         = Apointment
        fields        = ["customer_name","contact_number",'email','services',"booking_date","booking_time"]
        def validate_contact_number(self, request):
            try:
                m_num = request
                
                if len(str(m_num)) < 10:
                    raise serializers.ValidationError("10 digit required")
                    
                return request
            except Exception as e:
                print(e)
        
        def validate_email(self, request):
            try:
                email = request
                
                if "@" not in email:
                    raise serializers.ValidationError("invalid email-id")
                
                return request
            except Exception as e:
                print(e)
        def validate_booking_time(self, request):
            time_s    = request
            if time_s   != "15":
                raise serializers.ValidationError("invalid Time")    
            elif time_s != "30":
                raise serializers.ValidationError("invalid Time")   
            elif time_s != "45":
                
                raise serializers.ValidationError("invalid Time")
            elif time_s != "00":
                raise serializers.ValidationError("invalid Time")
            else:
                return time_s

class billgen_serializer(serializers.ModelSerializer): # serializer for generate invoice
        class Meta:
            model    = Invoice
            exclude  = ["date_time", "prise", "vendor_name", "Discont", "total", "c_gst", "s_gst", "grand_total", "slno"]

        def validate_Mobileno(self, request):
            try:
                m_num = request
                if len(str(m_num)) < 10:
                    raise serializers.ValidationError("10 digit required")
                return request
            except Exception as e:
                print(e)
        def validate_email(self, request):
            try:
                email = request
                if "@" not in email:
                    raise serializers.ValidationError("invalid email-id")
                return request
            except Exception as e:
                print(e)
        
class vendor_service_serializer(serializers.ModelSerializer):
        class Meta:
            model  = Service_data
            fields = '__all__'

