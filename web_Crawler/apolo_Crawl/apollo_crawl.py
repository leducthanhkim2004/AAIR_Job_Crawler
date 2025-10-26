from playwright.sync_api import sync_playwright
import json, os, time, random

def load_cookies(context, cookies_path):
    """Load cookies exported from your logged-in Apollo session."""
    with open(cookies_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    for cookie in cookies:
        if "sameSite" in cookie and cookie["sameSite"] not in ["Lax", "Strict", "None"]:
            cookie["sameSite"] = "Lax"
    context.add_cookies(cookies)

def download_apollo_html():
    save_dir = "apollo_html"
    os.makedirs(save_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        load_cookies(context, "apollo_cookies.json")

        page = context.new_page()
        page.goto("https://app.apollo.io/#/companies?organizationLocations[]=Vietnam&page=1&sortAscending=false&sortByField=recommendations_score", timeout=120000)
        time.sleep(15)  # Wait for React to load

        for page_num in range(1, 11):
            try:
                print(f"\n🔹 Saving page {page_num} ...")
                # Save HTML
                html = page.content()
                print("Read html file content")
                file_path = os.path.join(save_dir, f"apollo_page_{page_num}.html")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"✅ Saved {file_path}")

                if page_num < 10:
                    # Click the "Next" button using the class you provided
                    next_button = page.query_selector('button[aria-label="Next"], button.zp_NbJqo.zp_hgBYR[aria-label="Next"]')
                    print(f"➡️ Navigating to page {page_num + 1} ...")
                    if next_button:
                        next_button.click()
                        # Wait for the page number to update in the pagination control
                        page.wait_for_selector(f'span.zp_CsEot:has-text("{page_num + 1}")', timeout=60000)
                        # Wait for company list to update (optional: wait for a short time)
                        time.sleep(5)
                    else:
                        print("❌ Next button not found.")
                        break

                # random delay between pages (to look human)
                delay = random.uniform(8, 14)
                print(f"⏳ Waiting {delay:.1f}s before next page...")
                time.sleep(delay)

            except Exception as e:
                print(f"❌ Error on page {page_num}: {e}")
                time.sleep(10)

        browser.close()
        print("\n🎉 Done — all 10 pages downloaded.")

if __name__ == "__main__":
    download_apollo_html()