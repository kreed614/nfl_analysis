#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
from json import dump, load


class GetData:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        result = get(self.url).text
        return BeautifulSoup(result, 'html.parser')

    def query(self):
        request = get(self.url)
        if request.status_code == 200:
            return get(self.url).json()
        else:
            return {}


class ReadWrite:
    def __init__(self, destination, file=None):
        self.destination = destination
        self.file = file

    def read(self):
        with open(self.destination) as jf:
            return load(jf)

    def write(self):
        with open(self.destination, 'w', encoding='utf8') as jf:
            dump(self.file, jf, ensure_ascii=False)
