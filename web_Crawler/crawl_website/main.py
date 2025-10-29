import sys
from pathlib import Path
import asyncio

from playwright.async_api import async_playwright

from web_Crawler.crawl_website._crawler_base import CrawlerBase
from web_Crawler.crawl_website._hiring_caffe_IT_crawl import HiringCaffeITCrawler
from web_Crawler.utils.utils import load_config, prepare_folder, prepare_log
from web_Crawler.crawl_website.crawl_utils import crawl_full_job_with_tabs

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    config = load_config("C:\\Users\\leduc\\aair_lab\\web_Crawler\\config\\hiring_caffe_config.yaml")

    crawler = HiringCaffeITCrawler(config)
    asyncio.run(crawler.extract_all_job_links_safely())