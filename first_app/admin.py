from django.contrib import admin

# Register your models here.
from first_app.models import Contact, Product, Order, OrderItem

admin.site.register(Contact)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)