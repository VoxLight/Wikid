from __future__ import annotations
import requests
import html.parser
import pathlib
import urllib.parse
from typing import Callable


class UrlFilterer:
    def __init__(
            self,
            allowed_domains: set[str] | None = None,
            allowed_schemes: set[str] | None = None,
            allowed_filetypes: set[str] | None = None,
            additional_filters: set[Callable[[str], bool]] | None = None,
            _freedom_mode = False
    ):
        self.allowed_domains = allowed_domains
        self.allowed_schemes = allowed_schemes
        self.allowed_filetypes = allowed_filetypes
        self.additional_filters = additional_filters

        self._freedom_mode = _freedom_mode


    def filter_url(self, base: str, url: str) -> str | None:
        url = urllib.parse.urljoin(base, url)
        url, _frag = urllib.parse.urldefrag(url)
        parsed = urllib.parse.urlparse(url)
        if self._freedom_mode:
            return url

        if (self.additional_filters is not None 
            and not all(map(lambda x: x(url), self.additional_filters))):
            return None
        if (self.allowed_schemes is not None
                and parsed.scheme not in self.allowed_schemes):
            return None
        if (self.allowed_domains is not None
                and parsed.netloc not in self.allowed_domains):
            return None
        ext = pathlib.Path(parsed.path).suffix
        if (self.allowed_filetypes is not None
                and ext not in self.allowed_filetypes):
            return None
        return url

class UrlParser(html.parser.HTMLParser):
    def __init__(
            self,
            base: str,
            filter_url: Callable[[str, str], str | None]
    ):
        super().__init__()
        self.base = base
        self.filter_url = filter_url
        self.found_links = set()
        self.tags = ["a", "img"]
        self.attrs = ["href", "src"]


    def handle_starttag(self, tag: str, attrs):
        # look for <a href="...">
        if tag not in self.tags:
            return

        for attr, url in attrs:
            if attr not in self.attrs:
                continue

            if (url := self.filter_url(self.base, url)) is not None:
                self.found_links.add(url)

class Crawler:
    def __init__(
            self,
            filter_url: Callable[[str, str], str | None],
    ):
        self.seen = set()

        self.filter_url = filter_url

    def crawl(self, url: str):
        # rate limit here...
        response = requests.get(url)

        found_links = self.parse_links(
            base=str(response.url),
            text=response.text,
        )

        return found_links

    def parse_links(self, base: str, text: str) -> set[str]:
        parser = UrlParser(base, self.filter_url)
        parser.feed(text)
        return parser.found_links


def main():
    crawler = Crawler(
        filter_url=UrlFilterer(
            allowed_domains={"en.wikipedia.org"},
            allowed_schemes={"https"},
            allowed_filetypes={""},
        ).filter_url,
    )