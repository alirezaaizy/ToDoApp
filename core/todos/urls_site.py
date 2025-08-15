# todos/urls_site.py
from django.urls import path
from .views_site import HomeView, AboutView, ContactView, DashboardView

app_name = "site"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
