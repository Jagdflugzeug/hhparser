from django.contrib import admin
from app.models import Hub, HubArticle


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    pass


@admin.register(HubArticle)
class HubArticles(admin.ModelAdmin):
   pass
