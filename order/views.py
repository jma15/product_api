from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from order.serializers import UserSerializer, GroupSerializer, CustomerSerializer, OrderSerializer
from order.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connections
import datetime
import json

class CustomersViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Customers.objects.all()
    serializer_class = CustomerSerializer

class OrdersViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer

###############################################################
## Testing api with data
@csrf_exempt
@api_view(['GET','POST'])
def customer_list(request):
    print("get parameter is")
    print(request.query_params)
    print("data is")
    print(request.data)
    if request.method == 'GET':
        print("we are in get")

        queryset = Customers.objects.all()
        serializer_class = CustomerSerializer(queryset, many=True)
        # This returns the django rest
        return Response(serializer_class.data)

    elif request.method == 'POST':
        print("we are in post")

    return HttpResponse("test")

@csrf_exempt
def customer_detail(request, pk):
    if request.method == 'GET':
        print("we are in get")
    elif request.method == 'POST':
        print("we are in post")

    return HttpResponse(pk)

###############################################################
# Main functions
# Given customer id, return all the orders
@api_view(['GET','POST'])
@csrf_exempt
def product_sold(request):
    if request.method == 'GET':
        data = request.query_params
    elif request.method == 'POST':
        data = request.data

    # make sure the data is here
    if 'from' not in data or 'to' not in data or 'duration' not in data:
        return Response()

    num_days = 1
    if data['duration'] == 'week':
        num_days = 7
    elif data['duration'] == 'month':
        num_days = 30
    elif data['duration'] == 'day':
        num_days = 1

    # get all the data between the ranges
    sql = '''
            SELECT p.id, p.name, op.quantity, o.sold_date
            FROM orders as o 
                join orders_product as op on o.id = op.order_id
                join product as p on op.product_id = p.id
            WHERE o.sold_date between '%s' and '%s'
            Order by o.sold_date
          ''' % (data['from'], data['to'])

    cursor = connections['default'].cursor()
    cursor.execute(sql)
    results = dictfetchall(cursor)

    # Need to put the data into dictionary format
    date_dict = {}
    d = datetime.datetime.strptime(data['from'], "%Y/%m/%d")
    end_date = datetime.datetime.strptime(data['to'], "%Y/%m/%d")
    delta = datetime.timedelta(days=num_days)
    # where we are at the loop of product
    loop_counter = 0

    # Go through all the date by the increments selected
    while d <= end_date:
        current_day_string = d.strftime("%Y-%m-%d")
        new_date = d + delta
        # Loop through results and pop along the way
        for i in range(loop_counter, len(results)):
            # the date belongs in this range
            sold_date = datetime.datetime.combine(results[i]['sold_date'], datetime.time.min)
            sold_date_string = sold_date.strftime("%Y-%m-%d")

            # found something in the correct date range
            if sold_date < new_date and sold_date >= d:
                # need to add to dict
                if current_day_string in date_dict:
                    date_dict[current_day_string]['products_list'].append(results[i])
                else:
                    date_dict[current_day_string] = {}
                    date_dict[current_day_string]['products_list'] = [results[i]]
                    # create this new dict
                    if 'products_quantity' not in date_dict[current_day_string]:
                        date_dict[current_day_string]['products_quantity'] = {}
                
                # insert in the dict
                name = results[i]['name']
                if name in date_dict[current_day_string]['products_quantity']:
                    date_dict[current_day_string]['products_quantity'][name] += results[i]['quantity']
                else:
                    date_dict[current_day_string]['products_quantity'][name] = results[i]['quantity']

                # skip the first few once that is appended
                loop_counter += 1

            # the date is greater than the new date we are finished 
            elif sold_date > new_date:
                break;

        # put into the final dict for display
        if current_day_string not in date_dict:
            date_dict[d.strftime("%Y-%m-%d")] = {}

        # increment the date
        d += delta

    return Response(date_dict)

# Given customer id, return all the orders
@api_view(['GET','POST'])
@csrf_exempt
def order_detail(request, pk):
    ''' Function to return the order data
    '''
    try:
        cust = Customers.objects.get(pk=pk)
    except Customers.DoesNotExist:
        return HttpResponse('Customer id not found', status=404)

    # Get the order
    order = Orders.objects.filter(customer_id=cust)
    # serialize the data
    serializer_class = OrderSerializer(order, many=True)
    return Response(serializer_class.data)

def customers_category():
    ''' Function to obtain all customers data
    '''
    sql = '''
            SELECT c.id, c.first_name, cat.id, cat.name, count(*)
            FROM customer as c 
                join orders as o on c.id = o.customer_id
                join orders_product as op on order_id = o.id
                join product as p on op.product_id = p.id
                join category_products as cp on cp.product_id = p.id
                join category as cat on cat.id = cp.category_id
                GROUP BY c.id, c.first_name, cat.id, cat.name
          '''
    cursor = connections['default'].cursor()
    cursor.execute(sql)
    results = dictfetchall(cursor)
    return results

def dictfetchall(cursor):
    ''' Helper function to map the data back to dictionary format
    '''
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]