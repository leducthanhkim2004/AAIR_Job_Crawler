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
        processed_cards = set()  # store hashes of processed cards

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            self.logger.info(f"🌐 Navigating to {base_url}")
            await page.goto(base_url, wait_until="domcontentloaded", timeout=timeout)
            await asyncio.sleep(4)

            self.logger.info("🌀 Begin infinite scroll + carousel extraction...")
            last_height = 0
            stable_rounds = 0
            scroll_round = 0

            # === Infinite scroll main loop ===
            while stable_rounds < 3:
                scroll_round += 1
                self.logger.info(f"🌀 Scroll round {scroll_round}")
                await page.evaluate("window.scrollBy(0, window.innerHeight * 0.9)")
                await asyncio.sleep(2.0)

                # wait for new DOM growth
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    stable_rounds += 1
                else:
                    stable_rounds = 0
                last_height = new_height

                # === Collect job cards after each scroll ===
                company_cards = await page.query_selector_all(
                    "div.infinite-scroll-component div.grid > div.relative"
                )
                self.logger.info(f"📦 Found {len(company_cards)} cards on screen")

                for idx, card in enumerate(company_cards, start=1):
                    # avoid reprocessing same DOM elements
                    card_html = await card.inner_html()
                    card_hash = hashlib.md5(card_html.encode("utf-8")).hexdigest()
                    if card_hash in processed_cards:
                        continue
                    processed_cards.add(card_hash)

                    async def extract_links_from_card():
                        anchors = await card.query_selector_all("a[href*='/viewjob/']")
                        links = []
                        for a in anchors:
                            href = await a.get_attribute("href")
                            if href:
                                links.append(urljoin(base_url, href))
                        return links

                    # Step 1: visible job(s)
                    new_links = await extract_links_from_card()
                    added = 0
                    for l in new_links:
                        if l not in all_jobs:
                            all_jobs.add(l)
                            added += 1
                    if added > 0:
                        self.logger.info(f"🔗 Added {added} visible jobs (total {len(all_jobs)})")

                    # Step 2: click “>” to reveal hidden jobs
                    prev_hash = ""
                    for click_idx in range(1, 25):  # safety cap
                        try:
                            next_btn = await card.query_selector(
                                "button:not([disabled]):has(svg path[d*='7.5 7.5-7.5'])"
                            )
                            if not next_btn:
                                break

                            html_before = await card.inner_html()
                            prev_hash = hashlib.md5(html_before.encode("utf-8")).hexdigest()

                            await next_btn.click(force=True)
                            await asyncio.sleep(1.3)

                            html_after = await card.inner_html()
                            after_hash = hashlib.md5(html_after.encode("utf-8")).hexdigest()
                            if after_hash == prev_hash:
                                break  # no content change

                            links_after = await extract_links_from_card()
                            fresh = sum(1 for l in links_after if l not in all_jobs)
                            for l in links_after:
                                all_jobs.add(l)
                            if fresh > 0:
                                self.logger.info(f"➡️ Click {click_idx}: +{fresh} new jobs (total {len(all_jobs)})")

                        except Exception as e:
                            self.logger.warning(f"⚠️ Click {click_idx} failed: {e}")
                            break

                self.logger.info(f"🔽 Round {scroll_round} done — total links so far: {len(all_jobs)}")

            # === Finished infinite scrolling ===
            self.logger.info(f"✅ Infinite scroll finished — {len(all_jobs)} total job URLs")

            # === Save ===
            output_file = os.path.join(self.res_dir, "job_links_all_safe_dynamic.json")
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

