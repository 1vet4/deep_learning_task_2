from urllib.parse import urljoin

class UrlCleaner:

    def __init__(self):
        pass

    def remove_duplicate_urls(self, urls):
        return list(set(urls))

    def append_https_prefix(self, urls):
        prefix = 'https://www.delfi.lt'
        return [url if url.startswith(prefix) else urljoin(prefix, url) for url in urls]

    def remove_diskusija_from_url(self, urls):
        return [url for url in urls if 'diskusija' not in url]

    def clean_urls(self, urls):
        deduplicated_urls = self.remove_duplicate_urls(urls)
        removed_diskusija = self.remove_diskusija_from_url(deduplicated_urls)
        full_urls = self.append_https_prefix(removed_diskusija)

        return full_urls