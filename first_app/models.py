from django.db import models

# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=264, blank=False)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=False)
    message = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = u'Contact'


class Product(models.Model):
    name = models.CharField(max_length=264, unique=True)
    fee = models.TextField()
    description = models.TextField()
    content = models.TextField(default='DEFAULT VALUE')
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return str(self.name)
# Create your models here.


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now=True)
    updateted = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order{}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.PROTECT)
    product = models.ForeignKey(
        Product, related_name='items', on_delete=models.PROTECT)
    price = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity


class Input(models.Model):
    message = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = u'Input'
    