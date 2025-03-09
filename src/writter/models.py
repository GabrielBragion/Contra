from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from accounts.models import CustomUser

TITLE_MAXLEN = 100
CONTENT_MAXLEN = 500

class Article(models.Model):
    title = models.CharField(max_length=TITLE_MAXLEN, verbose_name=_t("Title"))
    content = models.TextField(max_length=CONTENT_MAXLEN, verbose_name=_t("Content"))
    data_posted = models.DateTimeField(default = timezone.now)
    is_premium = models.BooleanField(default=False, verbose_name=_t("Is this a premium article?"))
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)