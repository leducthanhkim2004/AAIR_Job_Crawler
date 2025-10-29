import asyncio
import json
import os
import hashlib
from urllib.parse import urljoin
from playwright.async_api import async_playwright

SAVE_DIR = "./data/result_it_vn"
os.makedirs(SAVE_DIR, exist_ok=True)

async def crawl_hiringcafe_all_jobs():
    base_url = "https://hiring.cafe/jobs/it"
    timeout = 60000
    all_jobs = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        print("🌐 Navigating to HiringCafe…")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=timeout)
        await asyncio.sleep(4)

        # ---- Phase 1: scroll to load all company cards ----
        print("🌀 Scrolling to load all company cards…")
        last_height = 0
        stable_rounds = 0
        while stable_rounds < 3:
            await page.evaluate("window.scrollBy(0, window.innerHeight * 0.9)")
            await asyncio.sleep(1.5)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                stable_rounds += 1
            else:
                stable_rounds = 0
            last_height = new_height
        print("✅ Scrolling complete.\n")

        # ---- Phase 2: collect all company cards ----
        company_cards = await page.query_selector_all("div.infinite-scroll-component div.grid > div.relative")
        print(f"🏢 Found {len(company_cards)} company cards\n")

        # ---- Phase 3: extract visible & hidden jobs ----
        for idx, card in enumerate(company_cards, start=1):
            print(f"🏷️ Company {idx}/{len(company_cards)}")

            # helper function to extract job links inside this card
            async def extract_links_from_card():
                anchors = await card.query_selector_all("a[href*='/viewjob/']")
                links = []
                for a in anchors:
                    href = await a.get_attribute("href")
                    if href:
                        links.append(urljoin(base_url, href))
                return links

            # collect first job
            new_links = await extract_links_from_card()
            added = 0
            for link in new_links:
                if link not in all_jobs:
                    all_jobs.add(link)
                    added += 1
            print(f"🔗 Added {added} new jobs (visible)")

            # now click ">" to reveal more
            prev_hash = ""
            for click_idx in range(1, 25):  # safety cap: 25 clicks max
                try:
                    next_btn = await card.query_selector("button:not([disabled]):has(svg path[d*='7.5 7.5-7.5'])")
                    if not next_btn:
                        print("🚫 No more next button (disabled or missing).")
                        break

                    # hash HTML before click
                    html_before = await card.inner_html()
                    prev_hash = hashlib.md5(html_before.encode("utf-8")).hexdigest()

                    print(f"➡️ Clicking next ({click_idx}) …")
                    await next_btn.click(force=True)
                    await asyncio.sleep(1.2)

                    # check if content changed
                    html_after = await card.inner_html()
                    after_hash = hashlib.md5(html_after.encode("utf-8")).hexdigest()
                    if after_hash == prev_hash:
                        print("⚠️ No content change — stopping.")
                        break

                    # extract new job(s)
                    links_after = await extract_links_from_card()
                    fresh = sum(1 for l in links_after if l not in all_jobs)
                    for l in links_after:
                        all_jobs.add(l)
                    print(f"🔗 Added {fresh} new jobs (total {len(all_jobs)})")

                except Exception as e:
                    print(f"⚠️ Click {click_idx} failed: {e}")
                    break

            print(f"🏁 Company {idx} done — total jobs: {len(all_jobs)}\n")

        # ---- Save ----
        output_file = os.path.join(SAVE_DIR, "job_links_all_safe.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sorted(all_jobs), f, ensure_ascii=False, indent=2)
        print(f"🎯 Done — {len(all_jobs)} total job URLs saved → {output_file}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_hiringcafe_all_jobs())
