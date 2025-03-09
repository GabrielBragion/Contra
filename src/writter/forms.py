from django.forms import ModelForm

from accounts.models import CustomUser
from common.django_utils import AsyncModelFormMixin
from writter.models import Article

class ArticleForm(ModelForm, AsyncModelFormMixin):
    class Meta:
        model = Article
        fields=(
            "title",
            "content",
            "is_premium",
        )
        
class UpdateUserForm(ModelForm, AsyncModelFormMixin):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
        )