
# use package absolute imports so module is importable when project root is on sys.path
from web_Crawler.crawl_website._crawler_base import CrawlerBase
from web_Crawler.utils.utils import *
import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
class HiringCafeCrawler(CrawlerBase):
    def __init__(self, config):
        super().__init__(config,total_crawled = 0 )
        self.config = config
        self.total_crawled = 0
        save_root = str(self.config.get("SAVE_ROOT_DIR", "."))
        self.extracted_urls = []
        self.list_level2_urls =[]
        # ensure folders exist (prepare_folder creates directories)
        prepare_folder(save_root, "result")
        prepare_folder(save_root, "logs")
        self.res_dir = os.path.join(save_root, "result")
        self.log_dir = os.path.join(save_root, "logs")

        # prepare_log expects named argument for log_dir
        self.logger = prepare_log(__name__, log_dir=self.log_dir)
        self.job_titles_urls = []
    def extract_url_sitemap(self, sitemap_url=None):
        if sitemap_url is None:
            sitemap_url = self.config["SITEMAP_URL"]

        try:
            self.logger.info(f"Fetching sitemap: {sitemap_url}")
            response = requests.get(sitemap_url, headers=self.config["HEADERS"], timeout=self.config["TIMEOUT"])
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except Exception as e:
            self.logger.error(f"Error fetching sitemap {sitemap_url}: {e}")
            return

        tag = root.tag.lower()
        if "sitemapindex" in tag:
            # 🔁 Recurse into each child sitemap
            for loc in root.findall(".//{*}loc"):
                child_url = loc.text.strip()
                self.logger.info(f"📂 Found sub-sitemap: {child_url}")
                self.extract_url_sitemap(child_url)
        elif "urlset" in tag:
            # 🧩 Collect actual URLs
            for loc in root.findall(".//{*}loc"):
                job_url = loc.text.strip()
                self.extracted_urls.append(job_url)
                self.logger.info(f"🧩 Extracted job URL: {job_url}")
        else:
            self.logger.warning(f"⚠️ Unknown XML root tag in {sitemap_url}: {root.tag}")

        return self.extracted_urls
    def crawl_website(self):
        pass
    def extract_location_links_from_page(self):
        """Extract all job_urls from extracted sitemap urls"""
        for url in self.extracted_urls:
            try:
                self.logger.info(f"Fetching page: {url}")
                response = requests.get(url, headers=self.config["HEADERS"], timeout=self.config["TIMEOUT"])
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                tags = soup.find_all(class_="text-blue-600 hover:text-blue-800 underline text-sm")
                for tag in tags:
                        href = tag.get('href')
                        location = tag.get_text().strip().replace(' ', "_")
                        if not href:
                            continue
                        full_url = urljoin(url, href)
                        self.logger.info(f"Found job title URL: {full_url} at location: {location}")
                        level2_url = {}
                        level2_url.update({
                            "job_location_url": full_url,
                            "location": location,
                            "extracted_sitemap_url": url
                        })
                        self.job_titles_urls.append(level2_url)
                        self.logger.info(f"Extracted job title URL: {full_url} at location: {location} from extracted sitemap URL: {url}")
            except Exception as e:
                self.logger.error(f"Error fetching page {url}: {e}")
                continue
            return self.list_level2_urls
if __name__ == "__main__":
    config_path = "C:\\Users\\leduc\\aair_lab\\web_Crawler\\config\\hiring_caffe_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    crawler = HiringCafeCrawler(config)
    sitemap_urls = crawler.extract_url_sitemap()
    crawler.extract_location_links_from_page()
    df = pd.DataFrame(crawler.job_titles_urls)
    df.to_csv(os.path.join(crawler.res_dir, "hiring_caffe_job_titles_urls.csv"), index=False, encoding="utf-8-sig")
    print(df.head(5))