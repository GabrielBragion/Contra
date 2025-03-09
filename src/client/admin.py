from django.contrib import admin

from .models import Subscription, PlanChoice

admin.site.register(Subscription)
admin.site.register(PlanChoice)
