from django.contrib import admin

from pandora.tasks.models import Article, Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
