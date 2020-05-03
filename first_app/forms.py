'''
Created on Nov 5, 2017

@author: LAP11401-local
'''
from django.db import models
from django import forms
from .models import Contact
from .models import Order, Input
class FormContact(forms.ModelForm):
    name=forms.CharField(max_length=100)
    phone=forms.CharField(max_length=20)
    email=forms.EmailField()
    message=forms.Textarea()
    class Meta:
        model=Contact
        fields=['name','phone','email','message']
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 10)]

class CardAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(label= 'Số lượng', choices = PRODUCT_QUANTITY_CHOICES, coerce=int)
    update = forms.BooleanField(required = False, widget = forms.HiddenInput)
class OrderCreateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Tên'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Họ'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':'username@email.com'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Địa chỉ'}))
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Số tài khoản'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Thành phố'}))
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address','postal_code','city'] 
class FormInput(forms.ModelForm):
    message=forms.Textarea()
    class Meta:
        model=Input
        fields=['message']
