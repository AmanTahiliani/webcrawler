__author__ = "Aman Tahiliani"

import requests
import lxml
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import argparse


class WebCrawler:
    def __init__(self):
        self.title_keyword_frequency = {}
        self.word_frequency = {}
        self.url_queue = [seed_url]
        self.visited_urls = set()
        self.counter = 0

        self.h1_word_frequency = {}

    def extract_page_info(self, url):
        print(f"Extracting information from Url {url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"
            }
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(response.text)

            soup = bs(response.content, "html.parser")
            all_page_links = soup.find_all("a", href=True)
            print(f"Found {len(all_page_links)} links in the current page")
            for page_link in all_page_links:
                self.url_queue.append(urljoin(url, page_link["href"]))

            filtered_elements = soup.find_all(
                lambda tag: tag.name in ["h1", "h2", "h3"]
                and not tag.find_parents(["header", "footer", "nav"])
            )

            for tags in filtered_elements:
                current_sentence = tags.text
                for current_word in current_sentence.split():
                    current_word = current_word.lower()

                    current_word_dict = self.h1_word_frequency.get(
                        current_word, {url: 0}
                    )
                    current_word_dict[url] = current_word_dict.get(url, 0) + 1
                    self.h1_word_frequency[current_word] = current_word_dict

            # for tags in h2_tags:
            #     current_sentence = tags.text
            #     for current_word in current_sentence.split():
            #         self.h2_word_frequency[current_word] = (
            #             self.h2_word_frequency.get(current_word, 0) + 1
            #         )
            return True

        except Exception as e:
            print(
                "Exception occured while crawling page {url}. Exception -> {e}".format(
                    url=url, e=e
                )
            )
            return False

    def crawler(self, seed_url, pages_to_parse):
        # Clearning the frequency Dictionaries
        self.title_keyword_frequency.clear()
        self.word_frequency.clear()

        self.url_queue = [seed_url]
        self.visited_urls = set()
        self.counter = 0

        while len(self.url_queue) and self.counter < pages_to_parse:
            new_url = self.url_queue.pop(0)

            if new_url not in self.visited_urls:
                self.counter += 1
                print(f"Page Numeber {self.counter}")
                visited = self.extract_page_info(new_url)
                if visited:
                    self.visited_urls.add(new_url)

        print("Done Parsing Pages")
        print(f"Pages Parsed {len(self.visited_urls)}/{pages_to_parse}")
        print(f"Words found in h1 {len(self.h1_word_frequency)}")
        print(self.h1_word_frequency)
        # print(f'Words found in h2 {len(self.h2_word_frequency)}')
        # print(self.h2_word_frequency)


parser = argparse.ArgumentParser(description="Crawler to crawl forward from a seed URL")
parser.add_argument("seed_url", help="URL to start the crawling from")
parser.add_argument(
    "--pages_to_parse",
    help="Upper limit of how many pages that need to be parsed",
    default=1000,
)
args = parser.parse_args()
seed_url = args.seed_url
pages_to_parse = args.pages_to_parse


if type(pages_to_parse == str):
    pages_to_parse = int(pages_to_parse)

web_crawler = WebCrawler()
print(f"Seed Url: {seed_url} \n Number of Pages to Parse {pages_to_parse}")
print("Initiating Crawler....")
web_crawler.crawler(seed_url, pages_to_parse)
