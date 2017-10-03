from django.contrib.auth.models import User, Group
from rest_framework import serializers
from order.models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ('username', 'first_name', 'last_name')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ('status', 'sold_date', 'customer_id')