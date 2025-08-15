from django.db import models
from django.utils import timezone

class Priority(models.IntegerChoices):
    HIGH = 1, 'بالا'
    MEDIUM = 2, 'متوسط'
    LOW = 3, 'پایین'

class Tag(models.Model):
    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=30)

    class Meta:
        unique_together = ('profile', 'name')
        ordering = ('name',)
        indexes = [
            models.Index(fields=['profile', 'name']),
        ]

    def __str__(self):
        return self.name


class Todo(models.Model):
    # مالک تسک: پروفایل
    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='todos')

    # محتوا
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # وضعیت/اولویت/سررسید
    priority = models.PositiveSmallIntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    is_done = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # تگ‌ها (به تگ‌های همان پروفایل لینک می‌شود)
    tags = models.ManyToManyField(Tag, blank=True, related_name='todos')

    archived = models.BooleanField(default=False)

    # زمان‌ها
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('is_done', 'priority', '-created_at')
        indexes = [
            models.Index(fields=['profile', 'is_done', 'archived']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return self.title

    # properties

    @property
    def user(self):
        return self.profile.user

    @property
    def owner_full_name(self):
        """نام کامل مالک؛ اگر خالی بود، ایمیل کاربر را برگردان."""
        fn = (self.profile.first_name or '').strip()
        ln = (self.profile.last_name or '').strip()
        full = f"{fn} {ln}".strip()
        return full or self.profile.user.email

    @property
    def is_overdue(self):
        """آیا سررسید گذشته؟ (فقط اگر done نیست و due_date دارد)"""
        return bool(self.due_date and not self.is_done and self.due_date < timezone.now())


    def save(self, *args, **kwargs):
        # وقتی تسک done شد، completed_at را ست کن؛ وقتی از done خارج شد، پاک کن
        if self.is_done and self.completed_at is None:
            self.completed_at = timezone.now()
        if not self.is_done and self.completed_at is not None:
            self.completed_at = None

        # عنوان را تمیز نگه داریم (ترایم)
        if self.title:
            self.title = self.title.strip()

        super().save(*args, **kwargs)


class Attachment(models.Model):
    # فایل‌های ضمیمهٔ هر تسک
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='todo_attachments/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment #{self.pk} for Todo #{self.todo_id}"










