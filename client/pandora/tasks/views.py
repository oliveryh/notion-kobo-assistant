import logging

from django.http import HttpResponse
from django.shortcuts import render
from pandora.tasks.forms import ArticleForm
from pandora.tasks.models import Article

logger = logging.getLogger("tasker")


def article_list_view(request):

    form = ArticleForm(request.POST or None)

    if request.method == "POST":
        logger.debug(request.POST)
        if form.is_valid():
            article = form.save()
            context = {'article': article}
            return render(request, "tasks/article_detail.html", context)
        else:
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

    context = {
        'articles': Article.objects.all().order_by('-created_at'),
        'form': form,
    }

    return render(request, "tasks/article_list.html", context)
