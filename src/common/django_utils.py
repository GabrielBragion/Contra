"""
Funções e outras coisas que são usadas nos apps dentro do projeto
"""

__all__ = (
    "AsyncFormMixin",
    "AsyncModelFormMixin",
    "AsyncViewT",
    "async_render",
    "async_logout",
)

from typing import Protocol

from django import forms
import django.contrib.auth as auth
from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

class AsyncViewT(Protocol):
    async def __call__(self, request: HttpRequest, *args, **kargs) -> HttpResponse:
        ...


class AsyncFormMixin:

    @sync_to_async
    def async_is_valid(self: forms.BaseForm):  # type: ignore
        return self.is_valid()

    @sync_to_async
    def async_render(self: forms.BaseForm):  # type: ignore
        return self.render()


class AsyncModelFormMixin(AsyncFormMixin):

    async def async_save(self: forms.ModelForm, *args, **kargs):  # type: ignore
        @sync_to_async
        def sync_call_save():
            return self.save(*args, **kargs)
        return await sync_call_save()


async def async_render(*render_args, **render_kargs) -> HttpResponse:

    @sync_to_async
    def sync_call_render() -> HttpResponse:
        return render(*render_args, **render_kargs)

    return await sync_call_render()


async def async_logout(*render_args, **render_kargs):
   
    @sync_to_async
    def sync_call_logout():
        auth.logout(*render_args, **render_kargs)
    
    await sync_call_logout()
    