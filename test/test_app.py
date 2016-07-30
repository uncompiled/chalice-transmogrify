import json
import pytest

from app import transform
from xml.parsers.expat import ExpatError


@pytest.mark.parametrize("xml_file,json_file", [
    ('test/fixtures/test.rss', 'test/fixtures/test.json'),
    ('test/fixtures/books.xml', 'test/fixtures/books.json'),
])
def test_transform(xml_file, json_file):
    # Tests whether the input is correctly transformed
    with open(xml_file, 'r') as test_rss:
        rss = test_rss.read()
        with open(json_file, 'r') as test_json:
            expected_json = test_json.read()
            output = json.dumps(transform(rss))
            assert output == expected_json


@pytest.mark.parametrize("input_file", [
    'test/fixtures/missing_opening_tag.xml',
    'test/fixtures/missing_closing_tag.xml',
    'test/fixtures/google.html',
])
def test_invalid(input_file):
    # Tests whether invalid XML files throw ExpatError
    with open(input_file, 'r') as test_rss:
        rss = test_rss.read()
        with pytest.raises(ExpatError):
            # Invalid XML should throw ExpatError
            transform(rss)
