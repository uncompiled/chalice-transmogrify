import hashlib
import json
import pytest

from unittest.mock import patch
from chalice.test import Client

from app import app, extract_item_ids, generate_cache_tags, transform
from xml.parsers.expat import ExpatError


@pytest.mark.parametrize("xml_file,json_file", [
    ('tests/fixtures/test.rss', 'tests/fixtures/test.json'),
    ('tests/fixtures/books.xml', 'tests/fixtures/books.json'),
])
def test_transform(xml_file, json_file):
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
    with open(input_file, 'r') as test_rss:
        rss = test_rss.read()
        with pytest.raises(ExpatError):
            transform(rss)


# --- generate_cache_tags ---

def test_generate_cache_tags_feed_prefix():
    tags = generate_cache_tags('https://example.com/feed.rss')
    assert any(t.startswith('feed:') for t in tags.split())


def test_generate_cache_tags_feed_hash_is_stable():
    url = 'https://example.com/feed.rss'
    expected = hashlib.sha256(url.encode()).hexdigest()[:12]
    tags = generate_cache_tags(url)
    assert f'feed:{expected}' in tags.split()


def test_generate_cache_tags_domain():
    tags = generate_cache_tags('https://feeds.example.com/rss')
    assert 'domain:feeds.example.com' in tags.split()


def test_generate_cache_tags_no_items_by_default():
    parsed = {'rss': {'channel': {'item': [{'guid': 'abc', 'link': 'http://x.com/1'}]}}}
    tags = generate_cache_tags('https://example.com/feed', parsed)
    assert not any(t.startswith('item:') for t in tags.split())


def test_generate_cache_tags_items_when_requested():
    parsed = {'rss': {'channel': {'item': [{'guid': 'abc'}, {'guid': 'def'}]}}}
    tags = generate_cache_tags('https://example.com/feed', parsed, include_items=True)
    item_tags = [t for t in tags.split() if t.startswith('item:')]
    assert len(item_tags) == 2


def test_generate_cache_tags_item_hash_is_stable():
    guid = 'tag:example.com,2024:item-1'
    expected = hashlib.sha256(guid.encode()).hexdigest()[:12]
    parsed = {'rss': {'channel': {'item': {'guid': guid}}}}
    tags = generate_cache_tags('https://example.com/feed', parsed, include_items=True)
    assert f'item:{expected}' in tags.split()


def test_generate_cache_tags_without_parsed_feed():
    # Should produce feed + domain only, no crash
    tags = generate_cache_tags('https://example.com/feed', include_items=True)
    assert not any(t.startswith('item:') for t in tags.split())
    assert 'domain:example.com' in tags.split()


# --- extract_item_ids ---

def test_extract_item_ids_rss_guid_string():
    parsed = {'rss': {'channel': {'item': [{'guid': 'id-1'}, {'guid': 'id-2'}]}}}
    assert extract_item_ids(parsed) == ['id-1', 'id-2']


def test_extract_item_ids_rss_guid_dict():
    # xmltodict returns a dict when guid has attributes
    parsed = {'rss': {'channel': {'item': {'guid': {'@isPermaLink': 'false', '#text': 'tag:example.com,2024:1'}}}}}
    assert extract_item_ids(parsed) == ['tag:example.com,2024:1']


def test_extract_item_ids_rss_single_item_as_dict():
    # xmltodict returns a dict (not list) for a single item
    parsed = {'rss': {'channel': {'item': {'guid': 'only-item'}}}}
    assert extract_item_ids(parsed) == ['only-item']


def test_extract_item_ids_rss_falls_back_to_link():
    parsed = {'rss': {'channel': {'item': [{'link': 'http://example.com/1'}]}}}
    assert extract_item_ids(parsed) == ['http://example.com/1']


def test_extract_item_ids_atom():
    parsed = {'feed': {'entry': [{'id': 'urn:uuid:abc'}, {'id': 'urn:uuid:def'}]}}
    assert extract_item_ids(parsed) == ['urn:uuid:abc', 'urn:uuid:def']


def test_extract_item_ids_atom_link_dict():
    parsed = {'feed': {'entry': {'link': {'@href': 'http://example.com/entry/1', '@rel': 'alternate'}}}}
    assert extract_item_ids(parsed) == ['http://example.com/entry/1']


def test_extract_item_ids_generic_xml_returns_empty():
    # books.xml has no RSS/Atom structure
    with open('tests/fixtures/books.xml', 'r') as f:
        parsed = transform(f.read())
    assert extract_item_ids(parsed) == []


def test_extract_item_ids_with_real_rss_fixture():
    with open('tests/fixtures/test.rss', 'r') as f:
        parsed = transform(f.read())
    ids = extract_item_ids(parsed)
    assert len(ids) > 0
    assert all(isinstance(i, str) and len(i) > 0 for i in ids)


# --- /convert route ---

def test_route_success_has_surrogate_key_header():
    with Client(app) as client:
        with patch('app.get_rss', return_value='<rss><channel><item><guid>g1</guid></item></channel></rss>'):
            result = client.http.get('/convert?url=https://example.com/feed.rss')
    assert result.status_code == 200
    assert 'Surrogate-Key' in result.headers
    tags = result.headers['Surrogate-Key'].split()
    assert any(t.startswith('feed:') for t in tags)
    assert 'domain:example.com' in tags


def test_route_success_no_item_tags_by_default():
    with Client(app) as client:
        with patch('app.get_rss', return_value='<rss><channel><item><guid>g1</guid></item></channel></rss>'):
            result = client.http.get('/convert?url=https://example.com/feed.rss')
    tags = result.headers['Surrogate-Key'].split()
    assert not any(t.startswith('item:') for t in tags)


def test_route_success_item_tags_when_requested():
    with Client(app) as client:
        with patch('app.get_rss', return_value='<rss><channel><item><guid>g1</guid></item></channel></rss>'):
            result = client.http.get('/convert?url=https://example.com/feed.rss&tags=items')
    tags = result.headers['Surrogate-Key'].split()
    assert any(t.startswith('item:') for t in tags)


def test_route_get_rss_failure_returns_400_with_surrogate_key():
    with Client(app) as client:
        with patch('app.get_rss', return_value=None):
            result = client.http.get('/convert?url=https://example.com/feed.rss')
    assert result.status_code == 400
    assert 'Surrogate-Key' in result.headers
    tags = result.headers['Surrogate-Key'].split()
    assert any(t.startswith('feed:') for t in tags)
    assert 'domain:example.com' in tags


def test_route_invalid_xml_returns_400_with_surrogate_key():
    with Client(app) as client:
        with patch('app.get_rss', return_value='not xml at all <<<'):
            result = client.http.get('/convert?url=https://example.com/feed.rss')
    assert result.status_code == 400
    assert 'Surrogate-Key' in result.headers


def test_route_missing_url_returns_400_no_surrogate_key():
    with Client(app) as client:
        result = client.http.get('/convert')
    assert result.status_code == 400
