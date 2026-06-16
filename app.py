import hashlib
import re
import requests
import xmltodict

from chalice import Chalice, BadRequestError, Response
from urllib.parse import urlparse
from xml.parsers.expat import ExpatError

app = Chalice(app_name='chalice-transmogrify')
app.debug = True

# Characters outside [a-zA-Z0-9_-] are rejected by Akamai (and the most
# restrictive of Fastly / CloudFlare / CloudFront as a group).
_UNSAFE_TAG_CHARS = re.compile(r'[^a-zA-Z0-9_-]+')


def _sanitize(value):
    return _UNSAFE_TAG_CHARS.sub('-', value).strip('-')


def _sha256_tag(value):
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def extract_item_ids(parsed_feed):
    ids = []
    # RSS 2.0
    try:
        items = parsed_feed['rss']['channel']['item']
        if isinstance(items, dict):
            items = [items]
        for item in items:
            guid = item.get('guid') or item.get('link')
            if isinstance(guid, dict):
                guid = guid.get('#text') or guid.get('@href')
            if guid:
                ids.append(str(guid))
    except (KeyError, TypeError):
        pass
    # Atom
    try:
        entries = parsed_feed['feed']['entry']
        if isinstance(entries, dict):
            entries = [entries]
        for entry in entries:
            eid = entry.get('id') or entry.get('link')
            if isinstance(eid, dict):
                eid = eid.get('#text') or eid.get('@href')
            if eid:
                ids.append(str(eid))
    except (KeyError, TypeError):
        pass
    return ids


def generate_cache_tags(url, parsed_feed=None, include_items=False):
    tags = [f'feed-{_sha256_tag(url)}']
    netloc = urlparse(url).netloc
    if netloc:
        tags.append(f'domain-{_sanitize(netloc)}')
    if include_items and parsed_feed is not None:
        for item_id in extract_item_ids(parsed_feed):
            tags.append(f'item-{_sha256_tag(item_id)}')
    return ' '.join(tags)


@app.route('/convert')
def index():
    request = app.current_request
    params = request.query_params or {}

    if 'url' not in params:
        raise BadRequestError("Missing url parameter")

    url = params['url']
    include_items = params.get('tags') == 'items'
    base_tags = generate_cache_tags(url)

    rss = get_rss(url)
    if rss is None:
        return Response(
            body={'Code': 'BadRequestError', 'Message': 'Unable to fetch URL'},
            status_code=400,
            headers={'Surrogate-Key': base_tags},
        )

    try:
        parsed = transform(rss)
    except ExpatError:
        return Response(
            body={'Code': 'BadRequestError', 'Message': 'Input is not XML'},
            status_code=400,
            headers={'Surrogate-Key': base_tags},
        )

    tags = generate_cache_tags(url, parsed, include_items)
    return Response(body=parsed, headers={'Surrogate-Key': tags})


def get_rss(url):
    try:
        response = requests.get(url, timeout=1.0).text
    except (requests.RequestException, ValueError):
        response = None
    return response


def transform(rss):
    return xmltodict.parse(rss)
