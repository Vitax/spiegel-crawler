from pprint import pprint

import requests
import json
from numpy.lib.recfunctions import recursive_fill_fields
from bs4 import BeautifulSoup


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


class Scrape:
    site = 'http://www.spiegel.de'
    json = []

    def extract_information_to_json(self):
        for teaser_article in self.teaser_content():
            author = teaser_article.find_next('span', {'class': 'author'}).string
            title = teaser_article.find_next('a', title=True).get('title')
            link = teaser_article.find_next('a', href=True).get('href')
            content = self.scrape_article_content(link)

            self.json.append(
                {
                    'title': title,
                    'author': author,
                    'link': link,
                    'content': content
                }
            )

            #pprint(self.json)

    def teaser_content(self):
        req = requests.get(self.site + '/spiegelplus/')
        if req.status_code == 200:
            text = req.text

        return BeautifulSoup(text, "html.parser").find_all('p', {'class': ['article-intro']})

    def scrape_article_content(self, link):
        article_content = []
        article_req = requests.get(self.site + link)
        if article_req.status_code == 200:
            article_text = article_req.text

        soup = BeautifulSoup(article_text, "html.parser")
        content = soup.find_all(True, {'class': 'article-section'})

        for parts in content:
            clear_text = parts.find_all('p', recursive=False)
            obfuscated_text = parts.find_all('p', {'class': 'obfuscated'})

            article_content.extend(self.strip_clear_text(clear_text))
            article_content.extend(self.undo_caeser(obfuscated_text))

        return article_content

    def strip_clear_text(self, clear_text):
        return (''.join(s.strings).strip() for s in clear_text)

    def undo_caeser(self, obfuscated_text):
        for ciph in obfuscated_text:
            s = " ".join(ciph.strings).strip()
            yield ''.join([chr(ord(c) - 1) if c != ' ' else ' ' for c in s])
