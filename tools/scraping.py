from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

ua = UserAgent()


class ScrapingTool:
    def __init__(self):
        pass

    def get_page_content(self, url):
        headers = {
            'User-Agent': ua.random
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.RequestException as e:
            print(f'Failed to get content from {url} — {e}')
            return None

    def get_subsections_urls(self, soup):
        urls = []
        for tag in soup.find_all('a', href=True):
            url = tag['href']
            urls.append(url)
        return urls

    def extract_article_metadata(self, soup):
        headline_header = soup.find('h1', class_="article-info__title")
        headline = headline_header.text.strip('\'" ') if headline_header else None
        date_div = soup.find('div', class_="article-info__publish-date")
        publication_date = date_div.text.strip('\'" ') if date_div else None
        category_span = soup.find('span', itemprop="name")
        category = category_span.text.strip('\'" ') if category_span else None

        metadata = {
            'headline': headline,
            'publication_date': publication_date,
            'category': category
        }

        return metadata

    def extract_main_article(self, soup):
        article_div = soup.find('div', class_=lambda c: c and "article-info__lead" in c)
        article = article_div.text.strip() if article_div else None
        body_container = soup.find('div', class_="col col-article article__body-fs-1")
        if body_container:
            paragraphs = body_container.find_all('div', class_="fragment fragment-html fragment-html--paragraph")
            body = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())
        else:
            body = ""

        full_article = f"{article}\n\n{body}".strip()
        return full_article if full_article else None
