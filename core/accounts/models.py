from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models.functions import Lower

class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the primary key.
    """
    use_in_migrations = True
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a new user with the given email and password and extra data
        """
        if not email:
            raise ValueError(_('The email must be set'))
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        if not password:
            raise ValueError(_('Password must be set'))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
         Create and save a new superuser with the given email and password and extra data
         """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if not password:
            raise ValueError(_('Password must be set for superuser'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='uniq_user_email_lower'
            )
        ]

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل باید با 09 شروع شده و دقیقاً ۱۱ رقم باشد."
            )
        ]
    )
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        help_text="عکس پروفایل (jpg یا png)"
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



