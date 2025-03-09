from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _t


class CustomUserManager(BaseUserManager):

    def create_user(self, email: str, password: str, **kargs):
        if not email.strip():
            raise ValueError(_t("Empty email. The email must be set."))

        user = self.model(
            email=self.normalize_email(email),
            **kargs,
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str, **kargs):
        must_be_true_fiels = ("is_staff", "is_superuser", "is_active")

        for field in must_be_true_fiels:
            if field in kargs and not kargs[field]:
                raise ValueError(_t(f"Field {field} must be True or left alone"))
            kargs[field] = True
        user = self.create_user(email, password, **kargs)
        user.is_admin = True

        return user
