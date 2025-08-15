from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect
from django.contrib import messages

from .forms import SignUpForm, EmailAuthenticationForm
from .forms_profile import ProfileForm
from .models import Profile

class SignUpView(SuccessMessageMixin, CreateView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:profile_edit")
    success_message = "حساب شما با موفقیت ساخته شد. لطفاً پروفایل را تکمیل کنید."

    def dispatch(self, request, *args, **kwargs):
        """
        if user is logged in, redirect to login page
        """
        if request.user.is_authenticated:
            return redirect("site:home")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        messages.info(self.request, "خوش آمدید ✨")
        return redirect(self.get_success_url())


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        return next_url or reverse_lazy("site:home")



class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy("site:home")


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "accounts/profile_form.html"
    form_class = ProfileForm
    success_url = reverse_lazy("site:home")

    success_message = "پروفایل با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile











