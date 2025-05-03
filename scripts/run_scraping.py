from environment.config import CONFIG
from environment.database import MongoDatabase
from tools.scraping import ScrapingTool
from tools.url_cleaner import UrlCleaner
import re
import time
import random
from collections import deque

def is_article_url(url):
    return re.search(r'-\d+$', url) is not None


def collect_all_urls(urls):
    article_urls = []
    subsection_urls = []
    for url in urls:
        if is_article_url(url):
            article_urls.append(url)
        else:
            subsection_urls.append(url)

    return article_urls, subsection_urls

def scrape_article(url):
    soup = scraper.get_page_content(url)
    if soup is not None:
        metadata = scraper.extract_article_metadata(soup)
        article = scraper.extract_main_article(soup)
        database.insert_document_entry(metadata, article)

def collect_urls_from_subsection(url):
    soup = scraper.get_page_content(url)
    if not soup:
        return []
    subsection_urls = scraper.get_subsections_urls(soup)
    return url_cleaner.clean_urls(subsection_urls) if subsection_urls else []

def perform_scraping(base_url):
    queue = deque([base_url])
    visited = set()

    while queue:
        current_url = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)

        soup = scraper.get_page_content(current_url)
        if not soup:
            continue

        urls = scraper.get_subsections_urls(soup)
        clean_urls = url_cleaner.clean_urls(urls)
        article_urls, subsection_urls = collect_all_urls(clean_urls)

        # Scrape articles
        for article_url in article_urls:
            if article_url not in visited:
                time.sleep(1 + random.uniform(1, 3))
                scrape_article(article_url)
                visited.add(article_url)
        # Add new subsections to the queue
        for subsection_url in subsection_urls:
            if subsection_url not in visited:
                queue.append(subsection_url)

        print('QUEUE: ', queue)

if __name__ == '__main__':
    scraper = ScrapingTool()
    url_cleaner = UrlCleaner()
    database = MongoDatabase(CONFIG)
    base_url = 'https://www.delfi.lt/'
    #soup = scraper.get_page_content(base_url)
    #urls = scraper.get_subsections_urls(soup)
    #clean_urls = url_cleaner.clean_urls(urls)
    #scrape_articles(clean_urls[:2], set(), set())
    perform_scraping(base_url)
