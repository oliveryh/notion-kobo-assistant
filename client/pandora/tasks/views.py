import logging

import markdown
from django.core.exceptions import ValidationError
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.urls.base import get_script_prefix
from pandora.tasks.filters import ArticleListFilter

from pandora.tasks.forms import ArticleForm
from pandora.tasks.models import Article

logger = logging.getLogger("tasker")


def article_filter_view(request):

    filter = ArticleListFilter(request.GET, queryset=Article.objects.all())
    object_list = filter.qs.annotate(
        is_highlighted=ExpressionWrapper(
            ~Q(highlights__exact=''), output_field=BooleanField()
        )
    ).order_by('-created_at')
    return render(
        request,
        "tasks/article_filter.html",
        {'filter': filter, 'object_list': object_list},
    )


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
    filter = ArticleListFilter

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
                return render(request, "tasks/article_table_detail.html", context)
            except ValidationError:
                return raise_errors(request, form)
        else:
            return raise_errors(request, form)

    context = {
        'object_list': Article.objects.all()
        .annotate(
            is_highlighted=ExpressionWrapper(
                ~Q(highlights__exact=''), output_field=BooleanField()
            )
        )
        .order_by('-created_at'),
        'filter': filter,
        'form': form,
        'script_prefix': get_script_prefix(),
    }

    return render(request, "tasks/article_list.html", context)


def article_detail_view(request, pk):

    article = Article.objects.get(pk=pk)
    context = {'article': article}

    article_highlights_html = markdown.markdown(article.highlights)
    context['article_highlights_html'] = article_highlights_html

    return render(request, "tasks/article_detail.html", context)
