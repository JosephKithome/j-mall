from django.db import models
from django.conf import Settings, settings
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.fields import EmailField
from django.shortcuts import reverse
from django_countries.fields import CountryField

# Create your models here.

CATEGORY_CHOICES=(
    ('S','Shirt'),
    ('SW','Sport Wear'),
    ('OW', 'OutWear'),
    ('LP', 'Laptops'),
    ('SS', 'SmatScreens'),
    ('P', 'Phones'),
    (('E'),'Electronics'),
)
LABEL_CHOICES=(
    ('P','primary'),
    ('S','secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES=(
    ('B','Billing'),
    ('S','Shipping'),
)
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=2)
    label=models.CharField(choices=LABEL_CHOICES,max_length=2)
    slug = models.SlugField()
    description= models.TextField()
    imageUrl=models.ImageField(blank=True,null=True,upload_to='media')
  
    
    
    def __str__(self):
        return self.title

    @property
    def imageURL(self):
        try:
            url = self.imageUrl.url
        except:
            url = ''
        return url    

    def get_discount_percent(self):
        return (self.price -self.discount_price)/self.price*(100)

    def item_price(self):
        return self.price -self.discount_price    

    def get_absolute_url(self):
        return reverse("core:product",kwargs={'slug':self.slug})  

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart",kwargs={'slug':self.slug}) 
    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart",kwargs={'slug':self.slug}) 



class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE) 
    ordered =models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
            return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price     

    def get_amount_saved(self):
        return self.get_total_item_price()-self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        else:
            return self.get_total_item_price()        
             




class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reference_code = models.CharField(max_length=10)
    items= models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    order_date=models.DateTimeField()
    ordered =models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name="billing_address",on_delete=SET_NULL,null=True,blank=True)
    shipping_address = models.ForeignKey('Address', related_name="shipping_address",on_delete=SET_NULL,null=True,blank=True)
    payment = models.ForeignKey('Payment',on_delete=SET_NULL,null=True,blank=True)
    coupon = models.ForeignKey("Coupon",on_delete=models.SET_NULL,blank=True,null=True)

    """
    ORDER LIFECYCLE

    1.Add item to cart.
    2.Adding a Billing Address.
      (CHECKOUT FAILED)
    3.Payment
    (Preprocessiing,processing,Packaging etc)  
    4.Being Delivered 
    5.Received
    6.Refunds
    """
    being_delivered =models.BooleanField(default=False)
    received =models.BooleanField(default=False)
    refund_requested =models.BooleanField(default=False)
    refund_granted =models.BooleanField(default=False)

    def __str__(self):
            return self.user.email
            
    def get_order_total(self):
        total = 0 
        for order_item in self.items.all():
            total +=order_item.get_final_price()
        if self.coupon:
            total -=self.coupon.amount   
        return total    


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=CASCADE,help_text="Attached user for this address")
    street_address =models.CharField(max_length=200,help_text="Street Address")
    apartment_address =models.CharField(max_length=200,help_text="Where you stay")
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100,help_text="Zip e.g 00100")
    address_type = models.CharField(max_length=1,choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username
    class Meta:
        verbose_name = 'Address'  
        verbose_name_plural = "Addresses"  

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        verbose_name ="Payment"
        verbose_name_plural = "Payments"    

class Coupon(models.Model):

    code = models.CharField(max_length=15)
    amount = models.FloatField()


    def __str__(self) -> str:
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    reason = models.TextField()
    accepted =models.BooleanField(default=False)
    #TODO figure out how to use the user email
    email =models.EmailField()

    def __str__(self) -> str:
        return f"{self.pk}"    
        
    class Meta:
        verbose_name ="Refund"
        verbose_name_plural = "Refunds"     