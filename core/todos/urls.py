from django.urls import path
from .views import (
    TodoListView, TodoDetailView, TodoCreateView, TodoUpdateView, TodoDeleteView,
    ToggleDoneView, ArchiveView, TagListCreateView, TagDeleteView
)

app_name = 'todos'
urlpatterns = [
    path('', TodoListView.as_view(), name='list'),
    path('create/', TodoCreateView.as_view(), name='create'),
    path('<int:pk>/', TodoDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', TodoUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', TodoDeleteView.as_view(), name='delete'),
    path('<int:pk>/toggle/', ToggleDoneView.as_view(), name='toggle'),
    path('<int:pk>/archive/', ArchiveView.as_view(), name='archive'),

    path('tags/', TagListCreateView.as_view(), name='tags'),
    path('tags/<int:pk>/delete/', TagDeleteView.as_view(), name='tag_delete'),
]
