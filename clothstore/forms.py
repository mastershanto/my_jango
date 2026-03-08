from django import forms


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=120)
    customer_email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=120)
    address = forms.CharField(max_length=255, widget=forms.Textarea(attrs={"rows": 3}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))


class OrderLookupForm(forms.Form):
    email = forms.EmailField(label="Customer email")
