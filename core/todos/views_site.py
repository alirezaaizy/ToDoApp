# todos/views_site.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django import forms

class HomeView(TemplateView):
    template_name = "site/home.html"

class AboutView(TemplateView):
    template_name = "site/about.html"

class ContactForm(forms.Form):
    name = forms.CharField(label="نام", max_length=120)
    email = forms.EmailField(label="ایمیل")
    message = forms.CharField(label="پیام", widget=forms.Textarea(attrs={"rows": 4}))

class ContactView(FormView):
    template_name = "site/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("site:contact")

    def form_valid(self, form):
        # فعلاً به کنسول—بعداً SMTP می‌تونی بذاری
        from django.core.mail import send_mail
        body = f"From: {form.cleaned_data['name']} <{form.cleaned_data['email']}>\n\n{form.cleaned_data['message']}"
        send_mail("[ToDoApp] پیام جدید", body, None, ["admin@example.com"], fail_silently=True)
        messages.success(self.request, "پیام شما ارسال شد. 🙏")
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "site/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.request.user.profile
        todos = p.todos.select_related("profile").prefetch_related("tags")
        ctx["open_count"] = todos.filter(is_done=False, archived=False).count()
        ctx["done_count"] = todos.filter(is_done=True, archived=False).count()
        ctx["archived_count"] = todos.filter(archived=True).count()
        ctx["recent"] = todos.order_by("-created_at")[:5]
        return ctx
