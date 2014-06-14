import requests
import re
from urlparse import urljoin

from .exceptions import Not200Error


class Crawler(object):
    def __init__(self, domain):
        self.domain = domain

    def _catch_url(self, url):
        """
        Whether the given url links to a different page
        of the same domain or not
        """
        starts_with_http = url.startswith('http')
        internal_domain = url.startswith(self.domain)
        new_page = not url.startswith('#')
        return not (starts_with_http and not internal_domain) and new_page

    def _absolute_url(self, url):
        """
        Take an url (e.g. about or /about or http://www.google.com/about)
        and return the absolute version of that url
        (e.g. http://www.google.com/about)
        """
        if url.startswith('http'):
            return url
        return urljoin(self.domain, url)

    def parse(self, url):
        """
        Fetch the given url and return all the links inside the <a> tags.
        Links to other domains or to subdomains other than www
        are excluded.
        """
        response = requests.get(url)
        regex = '<a [^>]*href="?\'?([^"\'>]+)"?\'?[^>]*>(?:.*?)</a>'
        regex_result = re.findall(regex, response.content, re.IGNORECASE)
        sanitizied_results = {
            self._absolute_url(each) for each in regex_result
            if self._catch_url(each)
        }
        return sanitizied_results
