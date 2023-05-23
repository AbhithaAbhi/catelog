from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from . models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
# Create your views here.

def _cart_id(request):
    cart=request.session.session_key

    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request,product_id):
    product=Product.objects.get(id=product_id)

    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart=Cart.objects.create(
                cart_id=_cart_id(request)
        )
        cart.save(),
    try:
        cart_item=CartItem.objects.get(product=product,cart=cart)
        if cart_item.quantity <  cart_item.product.stock:
            cart_item.quantity +=1
        cart_item.save(),

    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    return redirect('cart:cart_detail')


def cart_detail(request,total=0,counter=0,cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity

        total_quantity = sum(item.quantity for item in cart_items)
        total_amount = Decimal(total)

        # Apply discounts
        discount_name = None
        discount_amount = Decimal(0)

        if total_amount > 200:
            discount_name = "flat_10_discount"
            discount_amount = 10
        if any(item.quantity > 10 for item in cart_items):
            discount_name = "bulk_5_discount"
            discount_amount = total_amount * Decimal('0.05')  # 5% discount on total price
        if total_quantity > 20:
            discount_name = "bulk_10_discount"
            discount_amount = total_amount * Decimal('0.1')  # 10% discount on total price
        if total_quantity > 30 and any(item.quantity > 15 for item in cart_items):
            discount_name = "tiered_50_discount"
            discounted_items_price = sum(item.product.price * min(item.quantity, 15) for item in cart_items)
            discount_amount = (total_amount - Decimal(discounted_items_price)) * Decimal(
                '0.5')  # 50% discount on remaining price

        total_amount -= discount_amount

        shipping_fee = (total_quantity // 10) * 5

        gift_wrap_fee = 0
        if request.method == 'POST' and request.POST.get('gift_wrap') == 'on':
            gift_wrap_fee = total_quantity
        total_quantity = sum(item.quantity for item in cart_items)

        grand_total = total_amount + shipping_fee + gift_wrap_fee

        context = {
            'cart_items': cart_items,
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'discount_name': discount_name,
            'discount_amount': discount_amount,
            'shipping_fee': shipping_fee,
            'gift_wrap_fee': gift_wrap_fee,
            'grand_total': grand_total,
            'total': total,
            'counter': counter,
        }
    except ObjectDoesNotExist:
        context = {}
    return render(request, 'cart.html', context)


def cart_remove(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart_detail')

def full_remove(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(cart=cart,product=product)
    cart_item.delete()
    return redirect('cart:cart_detail')


