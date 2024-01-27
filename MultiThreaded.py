__author__ = "Aman Tahiliani"

import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import argparse
import multiprocessing
import time
import matplotlib.pyplot as plt
import pandas as pd
import json


class WebCrawler:
    def __init__(self, seed_url):
        manager = multiprocessing.Manager()

        self.url_queue = manager.list()
        self.url_queue.append(seed_url)
        self.visited_urls = manager.list()
        self.counter = manager.Value("i", 0)
        self.h1_word_frequency = manager.dict()

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

            filtered_elements = soup.find_all(
                lambda tag: tag.name in ["h1", "h2", "h3"]
                and not tag.find_parents(["header", "footer", "nav"])
            )

            for tags in filtered_elements:
                current_sentence = tags.text
                for current_word in current_sentence.split():
                    current_word = current_word.lower()

                    with self.freq_lock:
                        current_word_dict = self.h1_word_frequency.get(
                            current_word, {url: 0}
                        )
                        current_word_dict[url] = current_word_dict.get(url, 0) + 1
                        self.h1_word_frequency[current_word] = current_word_dict

            return True

        except Exception as e:
            print(f"Exception occurred while crawling page {url}. Exception -> {e}")
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
        crawl_start_time = time.time()
        pages_per_second_list = []
        total_pages_processed = 0
        with multiprocessing.Pool() as pool:
            while True:
                with self.url_queue_lock:
                    if not self.url_queue:
                        break
                    chunk_size = min(len(self.url_queue), multiprocessing.cpu_count())
                    chunks = [self.url_queue.pop(0) for chunk in range(chunk_size)]
                batch_start_time = time.time()
                pool.starmap(self.process_url, [(url,) for url in chunks])
                batch_end_time = time.time()

                pages_processed = len(chunks)
                total_pages_processed += pages_processed
                time_taken = batch_end_time - batch_start_time
                pages_per_second = pages_processed / time_taken

                for _ in range(pages_processed):
                    pages_per_second_list.append(pages_per_second)

                with self.visited_lock:
                    counter_val = self.counter.value
                    if counter_val >= pages_to_parse:
                        break

        crawl_end_time = time.time()
        total_crawl_time = crawl_end_time - crawl_start_time
        total_pages_crawled = self.counter.value
        pages_per_minute = total_pages_crawled / (total_crawl_time / 60)

        print("Done Parsing Pages")
        print(f"Pages Parsed {self.counter.value}/{pages_to_parse}")
        print(f"Links left to parse {len(self.url_queue)}")
        print(f"Words found in h1 {len(self.h1_word_frequency)}")

        with open("Keywords_Output.json", "w") as json_file:
            json.dump(dict(self.h1_word_frequency), json_file, indent=4)

        print(
            f"Number of pages crawled vs left to be crawled -> {self.counter.value}/{len(self.url_queue)} = {self.counter.value / len(self.url_queue)} "
        )

        plt.plot(range(1, total_pages_processed + 1), pages_per_second_list)
        plt.xlabel("Pages")
        plt.ylabel("Pages per Second")
        plt.title("Pages per Second for each page")
        plt.savefig("pages_per_second.png")

        speed_table = pd.DataFrame(
            {
                "Total Pages Crawled": [total_pages_crawled],
                "Total Crawl Time (seconds)": [total_crawl_time],
                "Pages per Minute": [pages_per_minute],
            }
        )
        print("\nCrawl Speed in terms of Pages per Minute:")
        print(speed_table)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis("tight")
        ax.axis("off")
        ax.table(
            cellText=speed_table.values,
            colLabels=speed_table.columns,
            cellLoc="center",
            loc="center",
        )
        plt.savefig("crawlspeed.png")

        crawl_ratio_table = pd.DataFrame(
            {
                "Total Pages Crawled": [total_pages_crawled],
                "Pages Left to Crawl": [len(self.url_queue)],
                "Crawl Ratio": [{self.counter.value / len(self.url_queue)}],
            }
        )

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis("tight")
        ax.axis("off")
        ax.table(
            cellText=crawl_ratio_table.values,
            colLabels=crawl_ratio_table.columns,
            cellLoc="center",
            loc="center",
        )
        plt.savefig("crawl_ratio_table.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawler to crawl forward from a seed URL"
    )
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
