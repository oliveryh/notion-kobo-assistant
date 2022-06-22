import django_filters

from pandora.tasks.models import Article


class ArticleListFilter(django_filters.FilterSet):
    class Meta:
        model = Article
        fields = ['completed_at']
