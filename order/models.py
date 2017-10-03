from django.db import models

# Create your models here.
class Customers(models.Model):
    username = models.CharField(max_length=128)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    class Meta:
    	db_table = 'customer'

class Orders(models.Model):
    status = models.CharField(max_length=100)
    sold_date = models.DateField()
    customer_id = models.ForeignKey(Customers, db_column='customer_id')

    class Meta:
    	db_table = 'orders'

class Products(models.Model):
    name = models.CharField(max_length=128)
    quantity = models.IntegerField()

    class Meta:
    	db_table = 'product'

class OrdersProduct(models.Model):
    order_id = models.ForeignKey(Orders, db_column='order_id')
    product_id = models.ForeignKey(Products, db_column='product_id')
    quantity = models.IntegerField()

    class Meta:
    	db_table = 'orders_product'

