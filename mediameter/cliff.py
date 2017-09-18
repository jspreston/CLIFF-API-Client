import logging, json
import requests

def get_url(host, port=None):

    if ':' in host:
        if port is not None:
            raise ValueError('cannot specify port in host and separate port')
        url = host
    elif port is not None:
        url =  host + ':' + port

    if not url.startswith('http'):
        url = 'http://' + url

    return url

class Cliff():
    """Make requests to a CLIFF geo-parsing / NER server"""

    CLIFF_BASE_PATH = "/cliff-2.4.0"

    JSON_PATH_TO_ABOUT_COUNTRIES = 'results.places.about.countries'

    def __init__(self, host, port=None, text_replacements={}, base_path=CLIFF_BASE_PATH):
        self._log = logging.getLogger(__name__)
        self._base_url = get_url(host, port) + base_path
        self._replacements = text_replacements
        self._log.info("initialized CLIFF @ %s", self._base_url)
        self._endpoint_text = self.getEndpoint('/parse/text')
        self._endpoint_sentences = self.getEndpoint('/parse/sentences')
        self._endpoint_nlp_json = self.getEndpoint('/parse/json')
        self._endpoint_locations_json = self.getEndpoint('/parse/locations')
        self._endpoint_geonames = self.getEndpoint('/geonames')

    def getEndpoint(self, path):
        return self._base_url + path

    def parseText(self, text, demonyms=False):
        cleaned_text = self._getReplacedText(text)
        return self._parseQuery(self._endpoint_text, cleaned_text , demonyms)

    def parseSentences(self, json_object, demonyms=False):
        return self._parseQuery(self._endpoint_sentences, json.dumps(json_object), demonyms)

    def parseNlpJson(self, json_object, demonyms=False):
        return self._parseQuery(self._endpoint_nlp_json, json.dumps(json_object), demonyms)

    def parseLocationsJson(self, json_object, demonyms=False):
        return self._parseQuery(self._endpoint_locations_json, json.dumps(json_object), demonyms)

    def geonamesLookup(self, geonames_id):
        return self._query(self._endpoint_geonames, {'id': geonames_id})['results']

    def _demonymsText(self, demonyms=False):
        return "true" if demonyms else "false"

    def _getReplacedText(self, text):
        replaced_text = text
        for replace, find in self._replacements.iteritems():
            replaced_text = text.replace(find, replace)
        return replaced_text

    def _parseQuery(self, path, text, demonyms=False):
        payload = {'q': text, 'replaceAllDemonyms': self._demonymsText(demonyms)}
        self._log.debug("Querying %r (demonyms=%r)", path, demonyms)
        return self._query(path,payload)

    def _query(self, url, args):
        try:
            r = requests.post(url, data=args)
            self._log.debug('CLIFF says %r', r.content)
            return r.json()
        except requests.exceptions.RequestException as e:
            self._log.exception(e)
        return ""
