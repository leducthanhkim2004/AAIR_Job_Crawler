from web_Crawler.crawl_website._crawler_base import CrawlerBase
from web_Crawler.utils.utils import *
import requests
from urllib.parse import urljoin
# replaced incorrect import: from crawl_utils import *
from web_Crawler.crawl_website.crawl_utils import *
import os
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
from web_Crawler.crawl_website._hiring_caffe_crawl import HiringCafeCrawler
if __name__ == "__main__":
    config = load_config("web_Crawler/config/hiring_caffe_config.yaml")
    crawler = HiringCafeCrawler(config)
    crawler.extract_url_sitemap()
    crawler.extract_location_links_from_page()
    crawler.extract_job_links_from_level2_urls()
    crawler.crawl_website()