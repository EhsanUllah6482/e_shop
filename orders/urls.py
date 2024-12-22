from django.urls import path

from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('make_payment/', views.make_payment, name='make_payment'),
    path('order_success/', views.order_success, name='order_success'),
    path('process-payment/', views.process_payment, name='process_payment'),
]
