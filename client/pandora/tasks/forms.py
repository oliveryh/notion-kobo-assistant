from crispy_forms.helper import FormHelper
from django import forms

from pandora.tasks.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("url",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
