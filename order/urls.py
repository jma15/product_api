from django.conf.urls import url
from order import views

urlpatterns = [
    url(r'^customer/$', views.customer_list),
    url(r'^customer/(?P<pk>[0-9]+)/$', views.customer_detail),
    url(r'^order/(?P<pk>[0-9]+)/$', views.order_detail),
    url(r'^product_sold/$', views.product_sold),
]
