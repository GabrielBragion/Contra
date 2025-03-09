from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import CustomUser
from common.django_utils import AsyncFormMixin, AsyncModelFormMixin

class CustomUserCreationForm(UserCreationForm, AsyncModelFormMixin):

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "is_writer",
        )
    
class CustomAuthenticationForm(AuthenticationForm,AsyncFormMixin):
    pass
        