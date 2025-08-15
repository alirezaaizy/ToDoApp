from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Todo, Tag
from .forms import TodoForm, TagForm


# ---------- Mixins ----------

class ProfileScopedQuerysetMixin:
    """
    for scoped queryset
    """
    def get_profile(self):
        return self.request.user.profile

    def base_queryset(self):
        return (Todo.objects
                    .select_related('profile', 'profile__user')
                    .prefetch_related('tags')
                    .filter(profile=self.get_profile()))

    def get_queryset(self):
        return self.base_queryset()


class SuccessUrlToListMixin:
    success_url = None

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        try:
            return reverse('todos:list')
        except Exception:
            return reverse('accounts:profile_edit')


# ---------- Todos ----------

class TodoListView(LoginRequiredMixin, ProfileScopedQuerysetMixin, ListView):
    template_name = 'todos/list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()

        # --- فیلتر/جست‌وجوی ساده از طریق GET ---
        q = (self.request.GET.get('q') or '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        status = (self.request.GET.get('status') or '').strip()  # open | done | archived
        if status == 'open':
            qs = qs.filter(is_done=False, archived=False)
        elif status == 'done':
            qs = qs.filter(is_done=True, archived=False)
        elif status == 'archived':
            qs = qs.filter(archived=True)

        priority = (self.request.GET.get('priority') or '').strip()
        if priority.isdigit():
            qs = qs.filter(priority=int(priority))

        tag_id = (self.request.GET.get('tag') or '').strip()
        if tag_id.isdigit():
            qs = qs.filter(tags__id=int(tag_id), tags__profile=self.get_profile()).distinct()

        # due_after / due_before به فرمت YYYY-MM-DDTHH:MM (datetime-local)
        due_after = self.request.GET.get('due_after')
        due_before = self.request.GET.get('due_before')
        def _parse(dt):
            if not dt:
                return None
            # 2025-08-13T17:45
            try:
                from datetime import datetime
                naive = datetime.strptime(dt, '%Y-%m-%dT%H:%M')
                from django.utils import timezone
                return timezone.make_aware(naive, timezone.get_current_timezone())
            except Exception:
                return None

        da = _parse(due_after)
        db = _parse(due_before)
        if da:
            qs = qs.filter(due_date__gte=da)
        if db:
            qs = qs.filter(due_date__lte=db)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # برای ساخت فیلتر تگ‌ها در تمپلیت
        ctx['tags'] = Tag.objects.filter(profile=self.get_profile()).order_by('name')
        return ctx


class TodoDetailView(LoginRequiredMixin, ProfileScopedQuerysetMixin, DetailView):
    template_name = 'todos/detail.html'


class TodoCreateView(LoginRequiredMixin, SuccessUrlToListMixin, CreateView):
    template_name = 'todos/form.html'
    form_class = TodoForm
    success_url = reverse_lazy('todos:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['profile'] = self.request.user.profile
        return kwargs

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, 'تسک با موفقیت ایجاد شد.')
        return resp


class TodoUpdateView(LoginRequiredMixin, ProfileScopedQuerysetMixin, SuccessUrlToListMixin, UpdateView):
    template_name = 'todos/form.html'
    form_class = TodoForm
    success_url = reverse_lazy('todos:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['profile'] = self.request.user.profile
        return kwargs

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, 'تسک با موفقیت بروزرسانی شد.')
        return resp


class TodoDeleteView(LoginRequiredMixin, ProfileScopedQuerysetMixin, SuccessUrlToListMixin, DeleteView):
    template_name = 'todos/confirm_delete.html'
    success_url = reverse_lazy('todos:list')

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, 'تسک حذف شد.')
        return super().delete(request, *args, **kwargs)


class ToggleDoneView(LoginRequiredMixin, ProfileScopedQuerysetMixin, View):
    """
    تغییر وضعیت انجام/برگشت.
    """
    def post(self, request, *args, **kwargs):
        obj = self.get_queryset().get(pk=kwargs['pk'])
        obj.is_done = not obj.is_done
        obj.save()
        messages.success(request, 'وضعیت انجام تغییر کرد.')
        try:
            return_url = request.META.get('HTTP_REFERER') or reverse('todos:list')
        except Exception:
            return_url = reverse('accounts:profile_edit')
        return redirect(return_url)


class ArchiveView(LoginRequiredMixin, ProfileScopedQuerysetMixin, View):
    """
    انتقال تسک به آرشیو.
    """
    def post(self, request, *args, **kwargs):
        obj = self.get_queryset().get(pk=kwargs['pk'])
        obj.archived = True
        obj.save()
        messages.info(request, 'تسک به آرشیو منتقل شد.')
        try:
            return redirect('todos:list')
        except Exception:
            return redirect('accounts:profile_edit')


# ---------- (اختیاری) مدیریت تگ‌ها ----------

class TagListCreateView(LoginRequiredMixin, ListView, CreateView):
    """
    یک صفحهٔ ساده برای:
      - نمایش تگ‌های پروفایل
      - ساخت تگ جدید
    """
    template_name = 'todos/tags.html'
    paginate_by = 20
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('todos:tags')

    def get_queryset(self):
        return Tag.objects.filter(profile=self.request.user.profile).order_by('name')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['profile'] = self.request.user.profile
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if 'form' not in ctx:
            ctx['form'] = self.get_form()
        return ctx

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, 'تگ جدید ایجاد شد.')
        return resp


class TagDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'todos/confirm_delete_tag.html'
    model = Tag
    success_url = reverse_lazy('todos:tags')

    def get_queryset(self):
        # فقط تگ‌های همین پروفایل
        return Tag.objects.filter(profile=self.request.user.profile)

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, 'تگ حذف شد.')
        return super().delete(request, *args, **kwargs)
