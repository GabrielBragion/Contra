from client.forms import UpdateSubscriptionForm
from .models import Subscription, PlanChoice
from writter.models import Article
from writter.forms import UpdateUserForm

from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import aget_user  # type: ignore
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from common.django_utils import async_render
from common.auth import aclient_required, ensure_for_current_user

from asgiref.sync import sync_to_async


from . import paypal as pp


@aclient_required
async def dashboard(request: HttpRequest) -> HttpResponse:
    """
    This is the writter dashboard
    """

    current_user = await aget_user(request)
    subscription_plan = "No subscription yet"
    if subscription := await Subscription.afor_user(current_user):
        subscription_plan = (await subscription.aplan_choice()).name
        if not subscription.is_active:
            subscription_plan += " (Inactive)"

    context = {
        "subscription_plan": subscription_plan,
        "has_subscription": subscription is not None,
    }

    return await async_render(request, "client/dashboard.html", context)


@aclient_required
async def browse_articles(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    articles = []
    if subscription := await Subscription.afor_user(current_user):
        if await subscription.ais_premium():
            articles = Article.objects.all()
        else:
            articles = Article.objects.filter(is_premium=False)

    context = {"has_subscription": subscription is not None, "articles": articles}

    return await async_render(request, "client/browse-articles.html", context)


@aclient_required
async def subscribe_plan(request: HttpRequest) -> HttpResponse:

    context = {"plan_choices": PlanChoice.objects.filter(is_active=True)}

    return await async_render(request, "client/subscribe-plan.html", context)


@aclient_required
async def update_user(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)

    subscription_plan = ""
    if subscription := await Subscription.afor_user(current_user):
        subscription_plan = (await subscription.aplan_choice()).name

    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=current_user)
        if await form.async_is_valid():
            await form.async_save()
            # Adicionando uma mensagem com um identificador
            messages.success(
                request,
                "Your information was successfully updated!",
                extra_tags="user_update",
            )

            return redirect(request.path)
    else:
        form = UpdateUserForm(instance=current_user)

    context = {
        "has_subscription": bool(subscription),
        "subscription": subscription,
        "subscription_plan": subscription_plan,
        "update_user_form": form,
    }

    return await async_render(request, "client/update-user.html", context)


@aclient_required
async def create_subscription(
    request: HttpRequest, sub_id: str, plan_code: str
) -> HttpResponse:
    current_user = await aget_user(request)

    if await Subscription.afor_user(current_user):
        return redirect("client-dashboard")

    plan_choice = await PlanChoice.afrom_plan_code(plan_code)
    await Subscription.objects.acreate(
        plan_choice=plan_choice,
        cost=plan_choice.cost,
        external_subscription_id=sub_id,
        is_active=True,
        user=current_user,
    )

    context = {"subscription_plan": plan_choice.name}

    return await async_render(request, "client/create-subscription.html", context)


@aclient_required
@ensure_for_current_user(Subscription, redirect_if_missing="client-dashboard")
async def cancel_subscription(
    request: HttpRequest, subscription: Subscription
) -> HttpResponse:

    if request.method == "POST":
        # Primeiro cancela no paypal
        access_token = await pp.get_access_token()
        sub_id = subscription.external_subscription_id

        await pp.cancel_subscription_pp(access_token, sub_id)

        # Depois na DB
        await subscription.adelete()

        context = {}
        template = "client/cancel-subscription-result.html"

    else:
        context = {"subscription_plan": (await subscription.aplan_choice()).name}
        template = "client/cancel-subscription.html"

    return await async_render(request, template, context)


@aclient_required
@ensure_for_current_user(Subscription, redirect_if_missing="client-dashboard")
async def update_subscription(
    request: HttpRequest, subscription: Subscription
) -> HttpResponse:

    user_plan_choice = await subscription.aplan_choice()

    if request.method == "POST":
        # Primeiro atualiza no paypal
        new_plan_code = request.POST["plan_choices"]
        new_plan_choice = await PlanChoice.afrom_plan_code(new_plan_code)
        new_plan_id = new_plan_choice.external_plan_id

        access_token = await pp.get_access_token()
        approval_url = await pp.update_subscription_pp(
            access_token,
            subscription_id=subscription.external_subscription_id,
            new_plan_id=new_plan_id,
            return_url=request.build_absolute_uri(
                reverse("update-subscription-result")
            ),
            cancel_url=request.build_absolute_uri(reverse("client-update-user")),
        )

        if approval_url:
            http_response = redirect(approval_url)
            request.session["subscription.id"] = subscription.id  # type: ignore
            request.session["new_plan_id"] = new_plan_id  # type: ignore
        else:
            error_msg = "An error occurred while updating your subscription. Please try again later."
            http_response = HttpResponse(error_msg)
            http_response = redirect("client-dashboard")

    else:
        form = await UpdateSubscriptionForm.ainit(exclude=[user_plan_choice.plan_code])

        context = {
            "plan_choices": PlanChoice.objects.filter(is_active=True).exclude(
                plan_code=user_plan_choice.plan_code
            ),
            "update_subscription_form": form,
        }

        http_response = await async_render(
            request, "client/update-subscription.html", context
        )

    return http_response


@aclient_required
async def update_subscription_result(request: HttpRequest) -> HttpResponse:

    session = request.session
    try:
        subscription_db_id = session["subscription.id"]
        new_plan_id = session["new_plan_id"]
    except KeyError:
        error_msg = "An error occurred while updating your subscription. Please try again later."
        return HttpResponse(error_msg)
    else:
        del session["subscription.id"]
        del session["new_plan_id"]

    subscription = await Subscription.objects.aget(id=int(subscription_db_id))
    subscription_id = subscription.external_subscription_id

    access_token = await pp.get_access_token()

    subscription_details = await pp.get_subscription_details(
        access_token, subscription_id
    )

    if not (
        subscription_details["status"] == "ACTIVE"
        and subscription_details["plan_id"] == new_plan_id
    ):
        error_msg = "An error occurred while updating your subscription. Please try again later."
        return HttpResponse(error_msg)

    new_plan_choice = await PlanChoice.objects.aget(external_plan_id=new_plan_id)
    subscription.plan_choice = new_plan_choice
    await subscription.asave()

    return await async_render(request, "client/update-subscription-result.html")


@aclient_required
async def delete_account(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    if request.method == "POST":
        await current_user.adelete()
        return redirect("home")

    return await async_render(request, "client/client-delete-account.html")


""" @aclient_required
async def change_password(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    
    if request.method == "POST":
        form = PasswordChangeForm(user=current_user, data=request.POST) #FIZ ALTERACOES DIRETAS NA CLASSE PasswordChangeForm
        if await form.async_is_valid(): #type: ignore
            await form.async_save() #type: ignore

            # Executa update_session_auth_hash de forma assíncrona
            await sync_to_async(update_session_auth_hash, thread_sensitive=True)(request, form.user)

            messages.success(request, "Your password was successfully updated!")
            return redirect("client-update-user")
    else:
        form = PasswordChangeForm(user=current_user)

    return await async_render(request, "client/change-password.html", {"change_password_form": form}) """

