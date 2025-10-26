from pathlib import Path
import os
import pytest
from ._crawler_base import CrawlerBase
from ..utils.utils import prepare_folder
from ..utils.prepare_log import prepare_log


def make_config(tmp_path: Path):
    return {
        "SITEMAP_URL": "http://example.com/sitemap.xml",
        "HEADERS": {},
        "TIMEOUT": 10,
        "SAVE_ROOT_DIR": str(tmp_path),
    }

SAMPLE_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://hiring.cafe/job/1</loc></url>
  <url><loc>https://hiring.cafe/job/2</loc></url>
  <url><loc>https://hiring.cafe/job/3</loc></url>
</urlset>
"""

def test_init_creates_dirs(tmp_path):
    cfg = make_config(tmp_path)
    crawler = HiringCafeCrawler(cfg)
    # expected folder paths
    assert os.path.isdir(os.path.join(cfg["SAVE_ROOT_DIR"], "result"))
    assert os.path.isdir(os.path.join(cfg["SAVE_ROOT_DIR"], "logs"))
    # attributes exist
    assert hasattr(crawler, "res_dir")
    assert hasattr(crawler, "log_dir")
    assert hasattr(crawler, "job_titles_urls")

def test_extract_url_sitemap_from_string(tmp_path):
    cfg = make_config(tmp_path)
    crawler = HiringCafeCrawler(cfg)
    urls = crawler.extract_url_sitemap(xml_text=SAMPLE_SITEMAP)
    assert isinstance(urls, list)
    assert len(urls) == 3
    assert "https://hiring.cafe/job/1" in urls
    assert "https://hiring.cafe/job/3" in urls

def test_extract_url_sitemap_fetch_monkeypatch(tmp_path, monkeypatch):
    cfg = make_config(tmp_path)
    crawler = HiringCafeCrawler(cfg)


    class DummyResp:
        def __init__(self, text):
            self.text = text
        def raise_for_status(self):
            return None

    def fake_get(url, headers=None, timeout=None):
        assert url == cfg["SITEMAP_URL"]
        return DummyResp(SAMPLE_SITEMAP)

    monkeypatch.setattr(
        "web_Crawler.crawl_website._hiring_caffe_crawl.requests.get",
        fake_get,
    )

    urls = crawler.extract_url_sitemap()  # will use patched requests.get
    assert isinstance(urls, list)
    assert len(urls) == 3