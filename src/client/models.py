from tabnanny import verbose
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _t
from django.utils.translation import gettext as _t2
from django.utils import timezone

from asgiref.sync import sync_to_async

from accounts.models import CustomUser

PLAN_CHOICE_NAME_MAX_LEN = 30
EXTERNAL_ID_MAX_LEN = 256
SUBSCRIPTION_COST_MAX_DIGITS = 3
PLAN_CHOICE_DESC_MAX_LEN = 300
EXTERNAL_API_URL_MAX_LEN = 2000
EXTERNAL_STYLE_MAX_LEN = 2000


class PlanChoice(models.Model):
    plan_code = models.CharField(
        max_length=2,
        unique=True,
        blank=False,
        verbose_name=_t("Plan Code"),
    )
    name = models.CharField(
        max_length=PLAN_CHOICE_NAME_MAX_LEN,
        unique=True,
        blank=False,
        verbose_name=_t("Plan Name"),
    )
    cost = models.DecimalField(
        max_digits=SUBSCRIPTION_COST_MAX_DIGITS,
        decimal_places=2,
        verbose_name=_t("Plan Cost"),
    )
    is_active = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    date_changed = models.DateTimeField(default=timezone.now)
    description1 = models.CharField(
        max_length=PLAN_CHOICE_DESC_MAX_LEN, verbose_name=_t("Plan description 1")
    )
    description2 = models.CharField(
        max_length=PLAN_CHOICE_DESC_MAX_LEN, verbose_name=_t("Plan description 2")
    )
    external_plan_id = models.CharField(
        max_length=EXTERNAL_ID_MAX_LEN, unique=True, verbose_name=_t("External plan id")
    )
    external_api_url = models.CharField(
        max_length=EXTERNAL_API_URL_MAX_LEN, verbose_name=_t("External API URL")
    )
    external_style_json = models.CharField(
        max_length=EXTERNAL_STYLE_MAX_LEN, verbose_name=_t("External Style(json)")
    )

    def __str__(self) -> str:
        return f"{str(self.name)} subscription"

    @classmethod
    async def afrom_plan_code(cls, plan_code: str) -> "PlanChoice":
        return await PlanChoice.objects.aget(plan_code=plan_code)

    @classmethod
    def from_plan_code(cls, plan_code: str) -> "PlanChoice":
        return PlanChoice.objects.get(plan_code=plan_code)


class Subscription(models.Model):

    cost = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_t("Subscription Cost")
    )
    external_subscription_id = models.CharField(
        max_length=EXTERNAL_ID_MAX_LEN, unique=True,
        verbose_name=_t("External Subscription ID"),
    )
    is_active = models.BooleanField(default=False)

    date_added = models.DateTimeField(default=timezone.now)
    plan_choice = models.ForeignKey(PlanChoice, on_delete=models.CASCADE)

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self) -> str:
        plan_choice = self.plan_choice
        subscription_text = _t2("subscription")
        return f"{self.user.first_name} {self.user.last_name}: {plan_choice.name} {subscription_text}"

    async def aplan_choice(self) -> PlanChoice:
        @sync_to_async
        def call_sync_fk() -> PlanChoice:
            return self.plan_choice

        return await call_sync_fk()

    async def ais_premium(self) -> bool:
        return (await self.aplan_choice()).plan_code == "PR"
    
    @staticmethod
    async def afor_user(user: CustomUser, status="") -> "Subscription | None":
        kargs: dict = {"user": user}
        if status in ("A", "I"):
            kargs.update(is_active = status == "A")
        try:
            return await Subscription.objects.aget(**kargs)
        except ObjectDoesNotExist:
            return None
