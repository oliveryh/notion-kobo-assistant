from datetime import datetime

import pytz
from django.core.exceptions import ValidationError
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
    highlights = models.TextField(_("Article Highlights"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Modified At"), auto_now=True)
    completed_at = models.DateTimeField(_("Completed At"), blank=True, null=True)
    time_read_minutes = models.IntegerField(_("Time Read Seconds"), default=0)

    @property
    def completed_at_days_since(self):
        if self.completed_at:
            now = datetime.utcnow().replace(tzinfo=pytz.utc)
            delta = now - self.completed_at
            d = delta.days
            if d == 0:
                return 'Today'
            elif d == 1:
                return '1 day ago'
            else:
                return f'{d} days ago'
