from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from .managers import CustomUserManager

FIRST_NAME_MAXLEN = 100
LAST_NAME_MAXLEN = 160


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name= _t("email adress"))
    username = models.CharField(max_length=FIRST_NAME_MAXLEN, verbose_name= _t("username"))
    first_name = models.CharField(max_length=FIRST_NAME_MAXLEN, verbose_name= _t("first name"))
    last_name = models.CharField(max_length=LAST_NAME_MAXLEN, verbose_name= _t("last name"))
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    is_writer = models.BooleanField(default=False, verbose_name= _t("user is a writer?"))
    
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Evita conflito com o auth.User
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',  # Evita conflito com o auth.User
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email
