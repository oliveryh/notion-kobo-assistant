from django.urls import path

from pandora.tasks.views import (
    article_filter_view,
    article_detail_view,
    article_list_view,
)

urlpatterns = [
    path("", article_list_view, name="article-list"),
    path("article/<int:pk>/", article_detail_view, name="article-detail"),
    path("filter/", article_filter_view, name="article-filter"),
]
