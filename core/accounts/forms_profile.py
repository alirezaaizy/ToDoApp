from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    """
    for edit or complete profile form
    """
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "phone_number", "birth_date", "bio", "avatar"]
        widgets = {
            "first_name":  forms.TextInput(attrs={"placeholder": "علی"}),
            "last_name":   forms.TextInput(attrs={"placeholder": "رضایی"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "09xxxxxxxxx"}),
            "birth_date":  forms.DateInput(attrs={"type": "date"}),
            "bio":         forms.Textarea(attrs={"rows": 3, "placeholder": "درباره من..."}),
        }
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "phone_number": "شماره موبایل",
            "birth_date": "تاریخ تولد",
            "avatar": "عکس پروفایل",
            "bio": "بیوگرافی",
        }
        help_texts = {
            "avatar": "jpg یا png",
        }
