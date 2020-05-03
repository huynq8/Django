'''
Created on Oct 8, 2017

@author: KTPHUONG
'''
from django.conf import settings
from mystore.models import Product

class Cart(object):
    def __init__(self, request):
        """
        initialize the session
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
    # moi lan co thay doi trong gio hang deu phai luu lai    
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified =True
    
    def add(self, product, quantity= 1, update_quantity = False):
        """
        add the product to the card or update its quantity
        """
        product_id = str(product.pk)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity' :0, 'fee': str(product.fee)}
        if update_quantity:
            self.cart[product_id]['quantity']= quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()
    
    def remove(self, product):
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def clear(self):
        self.cart = {}
        self.save()    
    
    def __iter__(self):
        """
        interate over the items in card and get the product from the database
        tra ve doi tuong cua chinh Cart
        yield: là phuong thuc tao mot doi tuong, o bai nay la mot ietm
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in = product_ids)
        for product in products:
            self.cart[str(product.pk)]['product'] = product
        for item in self.cart.values():
            item['fee'] = item['fee']
            item['total_fee'] = int(item['fee'])  * item['quantity']
            yield item
    
    def __len__(self):
        """
        count all items in the cart
        """
        return sum(int(item['quantity']) for item in self.cart.values())
    
    def get_total_fee(self):
        """
        get total fee of product
        """
        return sum((int(item['fee'])) * int(item['quantity']) for item in self.cart.values())
    
      
        
            
