import asyncio
import json
import os
import sys
import hashlib
from urllib.parse import urljoin
from playwright.async_api import async_playwright

from web_Crawler.crawl_website._crawler_base import CrawlerBase
from web_Crawler.utils.utils import load_config, prepare_folder, prepare_log
from web_Crawler.crawl_website.crawl_utils import crawl_full_job_with_tabs


class HiringCaffeITCrawler(CrawlerBase):
    def __init__(self, config, total_crawled: int = 0):
        super().__init__(config, total_crawled)
        self.config = config
        save_root = str(self.config.get("SAVE_ROOT_DIR", "."))
        prepare_folder(save_root, "result_it_vn")
        prepare_folder(save_root, "logs_it_vn")
        self.res_dir = os.path.join(save_root, "result_it_vn")
        self.log_dir = os.path.join(save_root, "logs_it_vn")
        self.logger = prepare_log(__name__, log_dir=self.log_dir)

    # =========================================================
    # ✅ New integrated safe function
    # =========================================================
async def extract_all_job_links_safely(self):
    base_url = self.config["BASE_URL"]
    timeout = self.config.get("TIMEOUT", 60000)
    all_jobs = set()
    processed_cards = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(base_url, wait_until="domcontentloaded", timeout=timeout)
        await asyncio.sleep(5)

        self.logger.info("🌀 Begin zig-zag scroll crawling (React virtualization bypass)")

        async def extract_from_visible_cards():
            """Extract visible + carousel job links from currently rendered cards."""
            new_added = 0
            cards = await page.query_selector_all("div.infinite-scroll-component div.grid > div.relative")
            self.logger.info(f"📦 {len(cards)} visible cards")
            for card in cards:
                try:
                    card_html = await card.inner_html()
                    card_hash = hashlib.md5(card_html.encode("utf-8")).hexdigest()
                    if card_hash in processed_cards:
                        continue
                    processed_cards.add(card_hash)

                    # --- visible job(s)
                    anchors = await card.query_selector_all("a[href*='/viewjob/']")
                    for a in anchors:
                        href = await a.get_attribute("href")
                        if href:
                            full = urljoin(base_url, href)
                            if full not in all_jobs:
                                all_jobs.add(full)
                                new_added += 1
                                self.logger.info(f"➕ Job link: {full}")

                    # --- carousel jobs (“>” button)
                    for click_idx in range(1, 10):
                        try:
                            next_btn = await card.query_selector(
                                "button:not([disabled]):has(svg path[d*='7.5 7.5-7.5'])"
                            )
                            if not next_btn:
                                break
                            html_before = await card.inner_html()
                            prev_hash = hashlib.md5(html_before.encode("utf-8")).hexdigest()

                            await next_btn.click(force=True)
                            await asyncio.sleep(1.8)

                            html_after = await card.inner_html()
                            after_hash = hashlib.md5(html_after.encode("utf-8")).hexdigest()
                            if after_hash == prev_hash:
                                break

                            anchors2 = await card.query_selector_all("a[href*='/viewjob/']")
                            for a2 in anchors2:
                                href2 = await a2.get_attribute("href")
                                if href2:
                                    full2 = urljoin(base_url, href2)
                                    if full2 not in all_jobs:
                                        all_jobs.add(full2)
                                        new_added += 1
                                        self.logger.info(f"➡️ Hidden job link: {full2}")
                        except Exception:
                            break
                except Exception as e:
                    self.logger.debug(f"Card extract error: {e}")
            return new_added

        # === Multi-pass zig-zag scroll ===
        total_passes = 4          # You can raise this to 5–6 for 600 + jobs
        scroll_steps = 40         # Number of downward scrolls per pass
        for pass_idx in range(total_passes):
            self.logger.info(f"🔁 Pass {pass_idx+1}/{total_passes} — scrolling ↓↓")
            # Scroll top→bottom
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(2)

            for i in range(scroll_steps):
                await page.evaluate("window.scrollBy(0, window.innerHeight * 0.9)")
                await asyncio.sleep(2.5)
                await extract_from_visible_cards()

            # Wait for any new cards (spinner)
            try:
                await page.wait_for_function(
                    "() => !document.querySelector('div[role=\"status\"], div[class*=\"loading\"], div[class*=\"spinner\"]')",
                    timeout=10000,
                )
            except Exception:
                pass

            self.logger.info(f"🔁 Pass {pass_idx+1}: scrolling ↑↑ to re-render old cards")
            # Scroll bottom→top
            for i in range(scroll_steps):
                await page.evaluate("window.scrollBy(0, -window.innerHeight * 0.9)")
                await asyncio.sleep(1.8)
                await extract_from_visible_cards()

        # === Final double-check ===
        await asyncio.sleep(3)
        added_final = await extract_from_visible_cards()
        self.logger.info(f"✅ Final check added {added_final} new jobs")

        self.logger.info(f"🎯 Crawl complete — {len(all_jobs)} unique job URLs found")

        # === Save results ===
        os.makedirs(self.res_dir, exist_ok=True)
        output_file = os.path.join(self.res_dir, "job_links_zigzag_full.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sorted(all_jobs), f, ensure_ascii=False, indent=2)
        self.logger.info(f"💾 Saved job links → {output_file}")

        await browser.close()

    return list(all_jobs)



        

    # =========================================================
    # ✅ Main crawl pipeline
    # =========================================================
    async def crawl_website(self):
        job_links = await self.extract_all_job_links_safely()
        for job_url in job_links:
            try:
                data = await crawl_full_job_with_tabs(job_url)
                os.makedirs(self.res_dir, exist_ok=True)
                url_hash = hashlib.md5(job_url.encode("utf-8")).hexdigest()
                filename = f"{url_hash}.json"
                filepath = os.path.join(self.res_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.logger.info(f"💾 Saved job data for {job_url}")
            except Exception as e:
                self.logger.exception(f"❌ Failed to crawl {job_url}: {e}")