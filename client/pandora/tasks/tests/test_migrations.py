import pytest


@pytest.mark.django_db()
def test_0003_make_completed_at_datetime(migrator):
    """Ensures that the initial migration works."""
    old_state = migrator.apply_initial_migration(
        ('tasks', '0002_article_highlight_fields')
    )
    Article = old_state.apps.get_model('tasks', 'Article')
    Author = old_state.apps.get_model('tasks', 'Author')

    # Let's create a model with just a single field specified:
    author = Author.objects.create(name='Author 1')
    article_1 = Article.objects.create(
        author=author,
        name='Article 1',
        url='article.com',
        filename='book.epub',
        is_complete=True,
    )
    article_2 = Article.objects.create(
        author=author,
        name='Article 1',
        url='article.com',
        filename='book.epub',
        is_complete=False,
    )

    new_state = migrator.apply_tested_migration(
        ('tasks', '0003_make_completed_at_datetime')
    )
    # After the initial migration is done, we can use the model state:
    Article = new_state.apps.get_model('tasks', 'Article')
    assert (
        Article.objects.get(pk=article_1.id).completed_at
        == Article.objects.get(pk=article_1.id).created_at
    )
    assert Article.objects.get(pk=article_2.id).completed_at == None
