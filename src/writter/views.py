from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import aget_user  # type: ignore
from django.contrib import messages


from common.django_utils import async_render
from common.auth import awriter_required, ensure_for_current_user

from .forms import ArticleForm, UpdateUserForm
from .models import Article


@awriter_required
async def dashboard(request: HttpRequest) -> HttpResponse:
    """
    This is the writter dashboard
    """
    return await async_render(request, "writter/dashboard.html")


@awriter_required
async def create_article(request: HttpRequest) -> HttpResponse:
    """
    This is the create article view
    """

    if request.method == "POST":
        form = ArticleForm(request.POST)
        if await form.async_is_valid():
            article = await form.async_save(commit=False)
            article.user = await aget_user(request)
            await article.asave()
            return redirect("my-articles")
    else:
        form = ArticleForm()

    context = {"create_article_form": form}

    return await async_render(request, "writter/create_article.html", context)


@awriter_required
async def my_articles(request: HttpRequest) -> HttpResponse:

    current_user = await aget_user(request)
    articles = Article.objects.filter(user=current_user)
    context = {"articles": articles}

    return await async_render(request, "writter/my_articles.html", context)


@awriter_required
@ensure_for_current_user(Article, redirect_if_missing="my-articles")
async def update_article(request: HttpRequest, article: Article) -> HttpResponse:
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if await form.async_is_valid():
            await form.async_save()
            messages.success(request, "Your information was successfully updated!", extra_tags='writer_update')
            return redirect(request.path)
    else:
        form = ArticleForm(instance=article)

    context = {"update_article_form": form}

    return await async_render(request, "writter/update_article.html", context)


@awriter_required
@ensure_for_current_user(Article, redirect_if_missing="my-articles")
async def delete_article(request: HttpRequest, article: Article) -> HttpResponse:
    if request.method == "POST":
        await article.adelete()
        return redirect("my-articles")

    context = {"article": article}

    return await async_render(request, "writter/delete_article.html", context)


@awriter_required
async def update_user(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=current_user)
        if await form.async_is_valid():
            await form.async_save()
            messages.success(request, "Your information was successfully updated!")
            return redirect(request.path)
    else:
        form = UpdateUserForm(instance=current_user)

    context = {"update_user_form": form}

    return await async_render(request, "writter/update_user.html", context)


@awriter_required
async def delete_account(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    if request.method == "POST":
        await current_user.adelete()
        return redirect("home")

    return await async_render(request, "writter/delete_account.html")
