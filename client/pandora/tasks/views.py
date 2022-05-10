import logging

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.urls.base import get_script_prefix
from pandora.tasks.forms import ArticleForm
from pandora.tasks.models import Article

logger = logging.getLogger("tasker")


def raise_errors(request, form):

    errors = form.errors.as_data()
    errors = {
        form.Meta.model._meta.get_field(k).verbose_name: ", ".join(
            [str(x.message) for x in v]
        )
        for k, v in errors.items()
    }
    response = HttpResponse(
        render(request, "tasks/alert.html", context={'errors': errors})
    )
    return response

def article_list_view(request):

    form = ArticleForm(request.POST or None)

    if request.method == "POST":
        logger.debug(request.POST)
        if form.is_valid():
            try:
                article = form.save(commit=False)
                article.author = form.cleaned_data['author']
                article.filename = form.cleaned_data['filename']
                article.name = form.cleaned_data['name']
                article = form.save()
                context = {'article': article}
                return render(request, "tasks/article_detail.html", context)
            except ValidationError:
                return raise_errors(request, form)
        else:
            return raise_errors(request, form)

    context = {
        'articles': Article.objects.all().order_by('-created_at'),
        'form': form,
        'script_prefix': get_script_prefix(),
    }

    return render(request, "tasks/article_list.html", context)
