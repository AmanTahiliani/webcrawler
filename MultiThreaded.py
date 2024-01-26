__author__= "Aman Tahiliani"

import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import argparse
import multiprocessing

class WebCrawler:
    def __init__(self, seed_url):
        manager = multiprocessing.Manager()

        self.url_queue = manager.list()
        self.url_queue.append(seed_url)
        self.visited_urls = manager.list()
        self.counter = manager.Value('i', 0)
        self.h1_word_frequency = manager.dict()

        # Using manager to create locks
        self.url_queue_lock = manager.Lock()
        self.visited_lock = manager.Lock()
        self.freq_lock = manager.Lock()

    def extract_page_info(self, url):
        # print(f"Extracting information from Url {url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"
            }
            try:
                response = requests.get(url, headers=headers)
            except:
                return

            if response.status_code != 200:
                raise Exception(response.text)

            soup = bs(response.content, "html.parser")
            all_page_links = soup.find_all("a", href=True)
            # print(f"Found {len(set(all_page_links))} links in the current page")
            for page_link in all_page_links:
                with self.url_queue_lock:
                    self.url_queue.append(urljoin(url, page_link["href"]))

            filtered_elements = soup.find_all(lambda tag: tag.name in ["h1", "h2", "h3"] and not tag.find_parents(["header", "footer", "nav"]))

            for tags in filtered_elements:
                current_sentence = tags.text
                for current_word in current_sentence.split():
                    current_word = current_word.lower()

                    with self.freq_lock:
                        current_word_dict = self.h1_word_frequency.get(current_word, {url: 0})
                        current_word_dict[url] = current_word_dict.get(url, 0) + 1
                        self.h1_word_frequency[current_word] = current_word_dict

            return True

        except Exception as e:
            print(
                f"Exception occurred while crawling page {url}. Exception -> {e}"
            )
            return False

    def process_url(self, new_url):
        shouldVisit = False
        with self.visited_lock:
            if new_url not in self.visited_urls:
                shouldVisit = True
                self.visited_urls.append(new_url)
                self.counter.value += 1
                print(f"Page Number {self.counter.value}")
        if shouldVisit:
            visited = self.extract_page_info(new_url)

    def crawler(self, pages_to_parse):
        with multiprocessing.Pool() as pool:
            while True:
                with self.url_queue_lock:
                    if not self.url_queue:
                        break  
                    chunk_size = min(len(self.url_queue), multiprocessing.cpu_count())
                    chunks = [self.url_queue.pop(0) for chunk in range(chunk_size)]
                pool.starmap(self.process_url, [(url,) for url in chunks])

                with self.visited_lock:
                    counter_val = self.counter.value
                    if counter_val >= pages_to_parse:
                        break

        print("Done Parsing Pages")
        print(f"Pages Parsed {self.counter.value}/{pages_to_parse}")
        print(f'Links left to parse {len(self.url_queue)}')
        print(f'Words found in h1 {len(self.h1_word_frequency)}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawler to crawl forward from a seed URL")
    parser.add_argument("seed_url", help="URL to start the crawling from")
    parser.add_argument(
        "--pages_to_parse",
        help="Upper limit of how many pages that need to be parsed",
        default=1000,
    )
    args = parser.parse_args()
    seed_url = args.seed_url
    pages_to_parse = int(args.pages_to_parse)

    web_crawler = WebCrawler(seed_url)
    print(f"Seed Url: {seed_url} \nNumber of Pages to Parse {pages_to_parse}")
    print("Initiating Crawler....")
    web_crawler.crawler(pages_to_parse)