from typing import Iterable

from django import forms
from django.forms import Form
from django.utils.translation import gettext_lazy as _t
from asgiref.sync import sync_to_async

from common.django_utils import AsyncModelFormMixin
from .models import PlanChoice


class UpdateSubscriptionForm(Form, AsyncModelFormMixin):
    plan_choices = forms.ChoiceField(
        label=_t("Update Plan Choices"),
    )

    def __init__(self,
                 exclude: Iterable[str] | None,
                 *args,
                 **kwargs
    ):
        super().__init__(*args, **kwargs)
        
        plan_choices_available = PlanChoice.objects.filter(is_active=True)
        
        if exclude:
            plan_choices_available = plan_choices_available.exclude(plan_code__in=exclude)

        self.fields["plan_choices"].choices = (
            (plan_choice.plan_code, plan_choice.name) for plan_choice in plan_choices_available
        )
        
    @classmethod
    async def ainit(cls, *args, **kwargs)-> "UpdateSubscriptionForm":
        @sync_to_async
        def call_init() -> UpdateSubscriptionForm:
            return UpdateSubscriptionForm(*args, **kwargs)
        
        return await call_init()