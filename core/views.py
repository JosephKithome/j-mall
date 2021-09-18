import string
import random
from django.http import request
from core.forms import CheckoutForm, CouponForm, RefundForm
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.detail import DetailView
from .models import Address, Coupon, Item, Order, OrderItem, Payment, Refund
from django.views.generic import ListView
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# restricting access
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import stripe
stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'

# Create your views here.


class HomeView(View):
    def get(self, *args, **kwargs):
        try:
            items = Item.objects.all()
            order = Order.objects.get(user=self.request.user, ordered=False)

            context = {
                'object_list': items,
                'object': order,
            }
            # print(order.items.count)
            return render(self.request, "index.html", context)
        except ObjectDoesNotExist:
            return render(self.request, "index.html")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class OrderSummary(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            context = {
                'object': order
            }
            return render(request, "shopping-cart.html", context)
        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order.")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is  in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "existing item quantity was updated")
            return redirect("core:home")
        else:
            order.items.add(order_item)
            messages.success(request, "This item was added to your cart.")
            return redirect("core:home")
    else:
        # Creating the order if it doesn't exist for the user
        ordered_date = timezone.now()
        newoder = Order.objects.create(
            user=request.user, order_date=ordered_date)
        newoder.items.add(order_item)
        messages.success(request, "This item was added to cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order:
                order.items.remove(order_item)
                messages.success(request, "This item was removed from cart.")
                # import pdb
                # pdb.set_trace()        
                return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:order-summary")

    else:
        messages.info(request, "You do not have an active order.")
        return redirect("core:order-summary")


@login_required
def remove_single_item_from_order(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        # check if
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:product", slug=slug)

    else:
        messages.info(request, "You do not have an active order.")
        return redirect("core:product", slug=slug)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


class CheckoutView(View):

    def get(self, request, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=request.user, ordered=False)

            context = {
                'form': form,
                'couponform': CouponForm(),
                'object': order,
                'DISPLAY_COUPON_FORM': True
            }
            # getting default shipping address
            shipping_address_qs = Address.objects.filter(
                user=request.user,
                address_type="S",
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            # getting default shipping address
            billing_address_qs = Address.objects.filter(
                user=request.user,
                address_type="B",
                default=True
            )
            # updating the context
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, 'checkout.html', context)

        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order")
            return redirect('core:checkout')

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST or None)
        # get the order based on the user
        
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            
            if form.is_valid():
                print(self.request.POST)
                # collect formdata
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                
                if use_default_shipping:
                    print("Using default shipping address...")
                    # getting default shipping address
                    address_qs = Address.objects.filter(
                        user=request.user,
                        address_type="S",
                        default=True
                    )
                    if address_qs.exists():
                        # setting address to the default address available in the database.
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                              
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect("core:checkout")
                else:
                    print("User is entering address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    # checking validity of user inputs:

                    if is_valid_form([shipping_address1, shipping_address2, shipping_country, shipping_zip]):

                        # initialize the billing address for saving
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type="S"
                           
                            )
                        # saving billing address
                        shipping_address.save()

                        # take the order if exists  and save
                        order.shipping_address = shipping_address
                        order.save()

                        # Setting default shipping address
                        set_default_shipping = form.cleaned_data.get(
                            "set_default_shipping")

                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in  the required shipping address")
            # collect formdata                   
                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = "B"
                    billing_address.save()
                    order.billing_address=billing_address
                    order.save()
                   

                elif use_default_billing:
                    print("Using default billing address...")
                    # getting default shipping address
                    address_qs = Address.objects.filter(
                        user=request.user,
                        address_type="B",
                        default=True
                    )
                    if address_qs.exists():
                        # setting address to the default address available in the database.
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect("core:checkout")
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    # checking validity of user inputs:
                    if is_valid_form([billing_address1, billing_address2, billing_country, billing_zip]):

                        # initialize the billing address for saving
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type="B"

                        )
                        # saving billing address
                        billing_address.save()

                        # take the order if exists  and save
                        order.billing_address = billing_address
                        order.save()

                        # Setting default shipping address
                        set_default_billing = form.cleaned_data.get(
                            "set_default_billing")

                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in  the required billing address fields!")
                        
                payment_option = form.cleaned_data.get('payment_option')
                print(payment_option)

                if payment_option == "S":
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == "P":
                    return redirect('core:payment', payment_option='paypal')
                elif payment_option == "P":
                    return redirect('core:payment', payment_option='cheque')
                elif payment_option == "P":
                    return redirect('core:payment', payment_option='mpesa')
                else:
                    messages.warning(request, "Invalid payment option.")
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order")
            return redirect('core:order-summary')


def generate_ref_code():
    return "".join(random.choice(string.ascii_uppercase + string.digits) for __ in range(10))


class PaymentView(View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)
        if order.billing_address:
            context = {
                'object': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(request, 'payment.html', context)
        else:
            messages.warning(request, 'You have not added a billing address')
            return redirect('core:checkout')

    def post(self, request, *args, **kwargs):
        # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
        order = Order.objects.get(user=request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        print("My token", token)
        amount = int(order.get_order_total()*100)
        print("My order", amount)

        try:
            # Use Stripe's library to make requests...
            charge_id = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            # create payment
            payment = Payment()

            payment.stripe_charge_id = charge_id['id']
            payment.user = request.user
            payment.amount = int(order.get_order_total())
            payment.save()

            # Updating The order(Handles a bug i had)
            order_items = order.items.all()
            order_items.update(ordered=True)

            for item in order_items:
                item.save()

            # Assign the payment to the order
            # now set the order to ordered
            order.ordered = True
            order.payment = payment
            order.reference_code = generate_ref_code()
            order.save()
            messages.success(request, "Your order was successful")
            return redirect('/')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('err', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error!")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters!")
            return redirect('/')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Api authentication error!")
            return redirect('/')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error!")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(
                self.request, "Something went wrong, You were not charged please try again!")
            return redirect('/')
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(
                self.request, "A serious error has occurred,We've been notified!")
            return redirect('/')


# Coupon Class

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist!")
        return redirect("core:checkout")


class AddCoupon(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                # coupon = get_coupon(request,code)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")

            except ObjectDoesNotExist:
                messages.info(
                    self.request, "You don not have an active order!")
                return redirect("core:checkout")
        # #TODO raise error
        # return None


class RequestRefundView(View):
    def get(self, *rgs, **kwargs):
        refundform = RefundForm()
        context = {
            "refundform": refundform,
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)

        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            # edit the order

            try:
                order = Order.objects.get(reference_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the Refund
                refund = Refund()
                refund.reason = message
                refund.order = order
                refund.email = email
                refund.save()
                messages.success(
                    self.request, "Your refund request was received!")
                return redirect('/')

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist!")
                return redirect('core:request-refund')
