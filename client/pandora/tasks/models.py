from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from pandora.tasks.imports import get_article_from_url


class Author(models.Model):

    name = models.CharField(_("Author Name"), max_length=255)
    articles: QuerySet["Article"]


class Article(models.Model):

    author = models.ForeignKey(
        Author,
        related_name="articles",
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("Article Name"), max_length=255)
    url = models.URLField(_("Article URL"))
    filename = models.CharField(_("Article Filename"), max_length=255)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Modified At"), auto_now=True)

    def save(self, *args, **kwargs) -> None:

        article_data = get_article_from_url(self.url)
        self.name = article_data["name"]
        self.filename = article_data["filename"]
        author = article_data["author"]
        self.author = Author.objects.get_or_create(name=author)[0]
        super().save(*args, **kwargs)
