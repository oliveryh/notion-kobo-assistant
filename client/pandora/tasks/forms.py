from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from pandora.tasks.imports import get_article_from_url
from pandora.tasks.models import Article, Author


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("url",)

    def clean(self):

        super(ArticleForm, self).clean()

        url = self.cleaned_data.get("url")
        cleaned_data = self.cleaned_data.copy()

        url_exists = Article.objects.filter(url=url).exists()
        if url_exists:
            raise ValidationError({
                "url": _("URL already exists"),
            })

        cleaned_data.update(
            get_article_from_url(url)
        )

        author = cleaned_data['author']
        cleaned_data['author'] = Author.objects.get_or_create(name=author)[0]

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
