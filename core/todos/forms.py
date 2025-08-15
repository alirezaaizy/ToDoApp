from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Todo, Tag, Priority


class TailwindFormMixin:
    """
    هر ویجت متنی/انتخابی رو با کلاس‌های پایهٔ Tailwind تزئین می‌کند.
    """
    base_input_classes = (
        "w-full rounded-xl border border-slate-200 px-3 py-2 "
        "focus:outline-none focus:ring focus:ring-slate-200"
    )

    def _tweak_widget(self, field):
        w = self.fields[field].widget
        if isinstance(w, (forms.TextInput, forms.EmailInput, forms.URLInput,
                          forms.PasswordInput, forms.NumberInput, forms.Textarea,
                          forms.Select, forms.SelectMultiple, forms.DateInput,
                          forms.DateTimeInput, forms.TimeInput)):
            css = w.attrs.get("class", "")
            w.attrs["class"] = (css + " " + self.base_input_classes).strip()

    def apply_tailwind(self):
        for name in self.fields:
            self._tweak_widget(name)


class TodoForm(TailwindFormMixin, forms.ModelForm):
    new_tags = forms.CharField(
        label="تگ‌های جدید (با , جدا کنید)",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "کار، خرید، پروژه"})
    )

    class Meta:
        model = Todo
        fields = ["title", "description", "priority", "due_date", "is_done", "tags"]
        labels = {
            "title": "عنوان",
            "description": "توضیحات",
            "priority": "اولویت",
            "due_date": "سررسید",
            "is_done": "انجام شد",
            "tags": "تگ‌ها",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "عنوان تسک"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "توضیحات اختیاری"}),
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        help_texts = {
            "tags": "می‌توانید از لیست انتخاب کنید یا بالا تگ جدید بسازید.",
        }
        error_messages = {
            "title": {"required": "عنوان لازم است."}
        }

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)

        if self.profile is not None:
            self.fields["tags"].queryset = Tag.objects.filter(profile=self.profile).order_by("name")

        # ظاهر Tailwind
        self.apply_tailwind()

        # فرمت ورودی تاریخ برای datetime-local
        self.fields["due_date"].input_formats = ["%Y-%m-%dT%H:%M"]

        # مقدار پیش‌فرض UI برای اولویت
        self.fields["priority"].initial = self.instance.priority or Priority.MEDIUM

    # ——— اعتبارسنجی‌ها ———
    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise ValidationError("عنوان لازم است.")
        return title

    def clean_due_date(self):
        due = self.cleaned_data.get("due_date")
        if not due:
            return due
        # اگر naive بود، به منطقهٔ زمانی پروژه آگاهش کن
        if timezone.is_naive(due):
            due = timezone.make_aware(due, timezone.get_current_timezone())
        if due < timezone.now():
            raise ValidationError("تاریخ سررسید نمی‌تواند در گذشته باشد.")
        return due

    # ——— ذخیره‌سازی و ساخت تگ‌های جدید ———
    def save(self, commit=True):
        obj = super().save(commit=False)

        # مالکیت را تضمین کن
        if self.profile and (obj.profile_id is None):
            obj.profile = self.profile

        if commit:
            obj.save()
            self.save_m2m()  # ذخیره many-to-many انتخاب‌شده‌ها

            # ساخت تگ‌های جدید
            raw = (self.cleaned_data.get("new_tags") or "")
            names = list({n.strip() for n in raw.split(",") if n.strip()})
            for name in names:
                if len(name) > 30:
                    raise ValidationError("نام هر تگ حداکثر باید ۳۰ کاراکتر باشد.")
                tag, _ = Tag.objects.get_or_create(
                    profile=self.profile,
                    name__iexact=name,
                    defaults={"name": name}
                )
                obj.tags.add(tag)

        return obj


class TagForm(TailwindFormMixin, forms.ModelForm):
    """
    اگر بخواهید صفحهٔ جدا برای مدیریت تگ‌ها داشته باشید.
    """
    class Meta:
        model = Tag
        fields = ["name"]
        labels = {"name": "نام تگ"}

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)
        self.apply_tailwind()

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise ValidationError("نام تگ لازم است.")
        if len(name) > 30:
            raise ValidationError("نام تگ حداکثر باید ۳۰ کاراکتر باشد.")
        if self.profile and Tag.objects.filter(profile=self.profile, name__iexact=name).exists():
            raise ValidationError("تگی با این نام از قبل وجود دارد.")
        return name

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.profile and obj.profile_id is None:
            obj.profile = self.profile
        if commit:
            obj.save()
        return obj
