import requests
import xmltodict

from chalice import Chalice, BadRequestError
from xml.parsers.expat import ExpatError

app = Chalice(app_name='chalice-transmogrify')
app.debug = True


@app.route('/convert')
def index():
    """
    /convert endpoint accepts a URL and converts it to json
    :param url: url to resource containing xml/rss document
    :return: json representation of the xml/rss document
    """
    request = app.current_request
    if 'url' not in request.query_params:
        raise BadRequestError("Missing url parameter")
    else:
        url = request.query_params['url']

        try:
            response = transform(get_rss(url))
        except ExpatError:
            raise BadRequestError("Input is not XML")
        else:
            return response


def get_rss(url):
    """
    get rss feed from a given url
    :param url: url to resource containing rss feed
    :return: text of the response, otherwise None
    """
    try:
        response = requests.get(url, timeout=1.0).text
    except (requests.RequestException, ValueError):
        response = None
    return response


def transform(rss):
    """
    transform rss to json
    :param rss: xml document containing rss feed
    :return: json formatted output
    """
    return xmltodict.parse(rss)
