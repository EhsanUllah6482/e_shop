from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from django.http import JsonResponse
from django.contrib import messages
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.


def make_payment(request):
    return render(request, "orders/credit_card.html")


def order_success(request):
    return render(request, "orders/order_success.html")

def process_payment(request):
    if request.method == "POST":
        try:
            order = Order.objects.filter(user=request.user, is_ordered=False).latest(
                "created_at"
            )
        except Order.DoesNotExist:
            messages.error(request, "No pending order found.")
            return redirect("cart")

        card_holder_name = request.POST["cardHolderName"]
        card_number = request.POST["cardNumber"]
        expiry_date = request.POST["expiryDate"]
        cvv = request.POST["cvv"]

        payment = Payment(
            user=request.user,
            payment_id=f"DUMMY-{order.id}",
            payment_method="Credit Card",
            amount_paid=order.order_total,
            status="Completed",
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            order_product = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
            order_product.variations.set(item.variations.all())
            order_product.save()

            item.product.stock -= item.quantity
            item.product.save()
            

            
        cart_items.delete()

        # Send order recieved email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        messages.success(request, "Payment successful! Order placed.")

        return redirect("order_success") 

    return JsonResponse({"error": "Invalid request"}, status=400)


def place_order(
    request,
    total=0,
    quantity=0,
):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )
            context = {
                "order": order,
                "cart_items": cart_items,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
            }
            return render(request, "orders/credit_card.html", context)
    else:
        return redirect("checkout")

