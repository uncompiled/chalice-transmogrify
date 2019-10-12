import json
import pytest

from app import transform
from xml.parsers.expat import ExpatError


@pytest.mark.parametrize("xml_file,json_file", [
    ('tests/fixtures/test.rss', 'tests/fixtures/test.json'),
    ('tests/fixtures/books.xml', 'tests/fixtures/books.json'),
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
    'tests/fixtures/missing_opening_tag.xml',
    'tests/fixtures/missing_closing_tag.xml',
])
def test_invalid(input_file):
    # Tests whether invalid XML files throw ExpatError
    with open(input_file, 'r') as test_rss:
        rss = test_rss.read()
        with pytest.raises(ExpatError):
            # Invalid XML should throw ExpatError
            transform(rss)
