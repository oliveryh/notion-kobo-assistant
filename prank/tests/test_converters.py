def test_book_creation_h2_tags():
    from prank.converters.epub import EpubConverter
    ep = EpubConverter("https://neilkakkar.com/things-I-learnt-from-a-senior-dev.html#writing-code")
    ep.generate_epub("/home/oliveryh/Documents/notion-kobo-assistant/books")
    assert len(ep.epub.chapters) > 1

def test_book_creation_h1_tags():
    from prank.converters.epub import EpubConverter
    ep = EpubConverter("http://smyachenkov.com/posts/cognitive-biases-software-development/")
    ep.generate_epub("/home/oliveryh/Documents/notion-kobo-assistant/books")
    assert len(ep.epub.chapters) > 1

def test_book_creation_h1_tags():
    from prank.converters.epub import EpubConverter
    ep = EpubConverter("https://newrepublic.com/article/156800/hollow-politics-minimalism")
    ep.generate_epub("/home/oliveryh/Documents/notion-kobo-assistant/books")