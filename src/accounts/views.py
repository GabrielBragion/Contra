from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import aget_user #type: ignore

from common.auth import aanonymous_required 

from .forms import CustomUserCreationForm,CustomAuthenticationForm
from .models import CustomUser
from common.django_utils import async_render, async_logout

@aanonymous_required
async def home(request: HttpRequest) -> HttpResponse:
    return await async_render(request, "accounts/home.html")

@aanonymous_required
async def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if await form.async_is_valid(): #funcao criada no AsyncFormMixin
            await form.async_save() #funcao criada no AsyncFormMixin
            return redirect("login")
    else:
        form = CustomUserCreationForm()
        
    context = {"register_form": form}
    return await async_render(request, "accounts/register.html", context)

@aanonymous_required
async def login(request: HttpRequest) -> HttpResponse:
    
    current_user = await aget_user(request)
    
    if current_user.is_authenticated:
        redirect("writter-dashboard" if current_user.is_writer else "client-dashboard")
    
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data = request.POST)
        if await form.async_is_valid(): #funcao criada no AsyncFormMixin
            email = request.POST["username"]
            password = request.POST["password"]
            user: CustomUser | None = await auth.aauthenticate(
                request,
                username = email,
                password = password
            ) # type: ignore
            
            if user:
                await auth.alogin(request, user)
                return redirect("writter-dashboard" if user.is_writer else "client-dashboard")
    else:
        form = CustomAuthenticationForm()
        
    context = {"login_form": form}
    return await async_render(request, "accounts/login.html",context)

@login_required(login_url="login") #type: ignore
async def logout(request: HttpRequest) -> HttpResponse:
    await async_logout(request)
    return redirect("/")