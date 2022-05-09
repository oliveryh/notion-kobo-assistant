import pytest
from pandora.tasks.forms import ArticleForm

class TestArticleForm:

    @pytest.mark.django_db()
    def test_invalid_url_throws_exception(self):

        form = ArticleForm(data={
            'url': 'www.abcdefawodkaowdkaow.com'
        })
        form.is_valid()
        assert form.errors == {'url': ['Invalid URL']}

    @pytest.mark.django_db()
    def test_unreachable_url_throws_exception(self):

        form = ArticleForm(data={
            'url': 'www.thiswebsitedoesntexistxyz.com'
        })
        form.is_valid()
        assert form.errors == {'url': ['Invalid URL']}

    @pytest.mark.django_db()
    def test_duplicate_url_throws_exception(self):

        # TODO: Mock response from get_soup
        url = "https://docs.djangoproject.com/en/4.0/ref/exceptions/"

        form = ArticleForm(data={
            'url': url
        })
        form.is_valid()
        article = form.save(commit=False)
        article.author = form.cleaned_data['author']
        article.filename = form.cleaned_data['filename']
        article.name = form.cleaned_data['name']
        article = form.save()

        form_two = ArticleForm(data={
            'url': url
        })
        form_two.is_valid()
        assert form_two.errors == {'url': ['URL already exists']}
