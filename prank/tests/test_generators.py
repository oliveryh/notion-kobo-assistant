from prank.generators import *
from prank.ptypes import Medium

def test_title_generator():
    url = "https://www.youtube.com/watch?v=UWnNjn1pki4"
    title = "Africa by Kayak - 2000km around the southern tip of Africa - YouTube"
    assert TitleGenerator().get_title(url, Medium.VIDEO) == title

def test_medium_generator():
    url = "https://www.youtube.com/watch?v=UWnNjn1pki4"
    medium = Medium.VIDEO
    assert MediumGenerator().get_medium(url) == medium
