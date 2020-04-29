def test_book_creation():
    from prank.converters.epub import EpubConverter
    ep = EpubConverter("https://neilkakkar.com/things-I-learnt-from-a-senior-dev.html#writing-code")
    ep.generate_epub("/home/oliveryh/Documents/notion-kobo-assistant/books")
    assert len(ep.epub.chapters) > 1

def test_book_creation_2():
    from prank.converters.epub import EpubConverter
    ep = EpubConverter("http://smyachenkov.com/posts/cognitive-biases-software-development/")
    ep.generate_epub("/home/oliveryh/Documents/notion-kobo-assistant/books")
    assert len(ep.epub.chapters) > 1
