from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('C', 'Cheque Payment'),
    ('P', 'PayPal'),
    ('M', 'MPESA')
)

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': '123 Main St',
        'class': 'input'
    }))
    shipping_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or Suite',
        'class': 'input'
    }))
    shipping_country = CountryField(blank_label='(Select Country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'input',
            'id': 'country'
        })
    )
    shipping_zip = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Zipcode',
        'class': 'input'
    }))
    telephone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': '+254717064...',
        'class': 'input'
    }))

    # Billing Address
    billing_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': '123 Main St',
        'class': 'input'
    }))
    billing_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or Suite',
        'class': 'input'
    }))
    billing_country = CountryField(blank_label='(Select Country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'input',
            'id': 'country'
        })
    )
    billing_zip = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Zipcode',
        'class': 'input'
    }))

    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    set_default_shipping = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    set_default_billing = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    use_default_shipping = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    use_default_billing = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': "Recipient's username",
        'aria-describedby': 'basic-addon2'
    }))

class RefundForm(forms.Form):
    ref_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Reference Code',
        'class': 'input'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'input',
        'placeholder': 'Refund Reason...',
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'placeholder': 'Your email Address',
        'class': 'input'
    }))
