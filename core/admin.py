from django.contrib import admin
from .models import Address, Coupon, Item, OrderItem, Order, Payment, Refund

# Register your models here.


def make_refund_granted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_granted.short_description = "Update orders to refund granted"


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'reference_code', 'being_delivered', 'received',
                    'refund_requested', 'refund_granted', 'billing_address', 'shipping_address', 'payment', 'coupon']
    list_display_links = ['billing_address',
                          'shipping_address', 'payment', 'coupon']
    list_filter = ['ordered', 'being_delivered',
                   'received', 'refund_requested', 'refund_granted']
    search_fields = ['user__username', 'reference_code']

    actions = [make_refund_granted]


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'apartment_address',
                    'zip', 'country', 'address_type', 'default', ]
    list_filter = ['user', 'street_address', 'apartment_address',
                    'zip', 'country', 'address_type', 'default', ]
    search_fields = ['user', 'country',
                     'street_address', 'apartment_address', 'default']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
