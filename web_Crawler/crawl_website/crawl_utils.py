from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def parse_posted_date_text(text: str, now: datetime | None = None) -> str | None:
    """Convert strings like 'Posted 1d ago' or 'Posted 2 hours ago' to a datetime string.
    Returns ISO-like datetime string 'YYYY-MM-DD HH:MM:SS' or the original text if unknown.
    """
    if not text:
        return None
    s = text.strip()
    # remove leading 'Posted' or similar
    s = re.sub(r'^[Pp]osted[:\s]*', '', s).strip()

    now = now or datetime.now()

    # common relative formats: "1d ago", "2 hours ago", "5m ago", "30 mins ago"
    m = re.match(r'(?P<num>\d+)\s*(?P<unit>(?:mins?|minutes?|m|hrs?|hours?|h|days?|d|weeks?|w))', s, flags=re.I)
    if m:
        n = int(m.group('num'))
        unit = m.group('unit').lower()
        if unit.startswith('m') and not unit.startswith('mo'):       # minutes
            delta = timedelta(minutes=n)
        elif unit.startswith('h'):                                   # hours
            delta = timedelta(hours=n)
        elif unit.startswith('d'):                                   # days
            delta = timedelta(days=n)
        elif unit.startswith('w'):                                   # weeks
            delta = timedelta(weeks=n)
        else:
            delta = timedelta(minutes=n)
        dt = now - delta
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    # single-word cases
    if re.search(r'\byesterday\b', s, flags=re.I):
        dt = now - timedelta(days=1)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    if re.search(r'\btoday\b', s, flags=re.I):
        return now.strftime("%Y-%m-%d %H:%M:%S")

    # try common absolute date formats
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%d %b %Y"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    # fallback: return original text
    return s

def extract_text_after_button(soup, header_text):
    """Finds a section following a header span with specific text (for fallback parsing)."""
    header = soup.find("span", string=lambda t: t and header_text.lower() in t.lower())
    if header:
        next_span = header.find_next("span")
        return next_span.get_text(strip=True) if next_span else "N/A"
    return "N/A"

def parse_job_sections(html):
    """Parse job info, company info, and job description from rendered HTML."""
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    # --- Basic Job Info ---
    title = soup.find("h2", class_="font-extrabold")
    #EXTRACT COMPANY NAME 
    company = soup.find(
        "span",
        class_=lambda c: c and "text-xl" in c and "font-semibold" in c and "text-gray-700" in c
    )
    company_name = "N/A"
    if company:
        # Extract text safely and remove leading '@' and artifacts
        text_parts = [t.strip() for t in company.stripped_strings if t.strip()]
        company_name = " ".join(text_parts)
        company_name = company_name.replace("@", "").strip()
    
    salary = soup.find("span", string=lambda t: "$" in t)
    posted_text_node = soup.find(string=re.compile(r'\bPosted\b', re.I))
    posted_tag = posted_text_node.parent if posted_text_node else None

    
    work_mode = soup.find("span", string=lambda t: t and any(x in t for x in ["Remote", "Onsite", "Hybrid"]))
    employment_type = soup.find("span", string=lambda t: t and any(x in t for x in ["Full Time", "Part Time","Temporary","Contract","All Commitments Available"]))
    
    # --- Location parsing (fixed) ---
    location = None
    location_choices = []
    
    # Try to find location container with the map pin icon
    loc_containers = soup.select('div.flex')
    for container in loc_containers:
        # Verify this div has the map pin SVG with the correct path pattern
        svg = container.find('svg')
        if not svg:
            continue
            
        # Check if this is the location pin SVG by looking at its paths
        paths = svg.find_all('path')
        path_data = ' '.join(p.get('d', '') for p in paths)
        # Location pin SVG has specific path data containing these patterns
        if not ('M15 10.5a3 3 0' in path_data and 'M19.5 10.5c0 7.142' in path_data):
            continue
            
        # Find the span next to SVG
        span = container.find('span')
        if not span:
            continue
            
        # Skip loading placeholder
        text = span.get_text(strip=True)
        if not text or text.lower() in ('loading...', 'hiringcafe'):
            continue
            
        # Found valid location text
        if ' or ' in text:
            location_choices = [loc.strip() for loc in text.split(' or ')]
            location = location_choices[0]
        else:
            location = text
            location_choices = [text]
        break  # Found valid location, stop searching

    # Store results
    data["location"] = location if location else "N/A" 
    data["location_choices"] = location_choices

    data["job_title"] = title.get_text(strip=True) if title else "N/A"
    data["company"] = company_name#extract company name
    data["salary"] = salary.get_text(strip=True) if salary else "N/A"
    data["work_mode"] = work_mode.get_text(strip=True) if work_mode else "N/A"
    data["employment_type"] = employment_type.get_text(strip=True) if employment_type else "N/A"
    # parse and normalize posted date
    if posted_tag:
        pd_text = posted_tag.get_text(strip=True)
        parsed = parse_posted_date_text(pd_text)
        data["posted_date"] = parsed if parsed else pd_text
    else:
        data["posted_date"] = "N/A"

    data["responsibilities"] = extract_text_after_button(soup, "Responsibilities")
    data["requirements"] = extract_text_after_button(soup, "Requirements Summary")

    return data


def parse_company_info_table(html):
    """Parse the company info table with proper key-value mapping."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="table-auto")
    company_info = {}

    if not table:
        return {"company_info": "N/A"}

    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        field = cols[0].get_text(strip=True)
        value_td = cols[1]

        if field in ["Industries", "Activities"]:
            links = [a.get_text(strip=True) for a in value_td.find_all("a")]
            value = ", ".join(links) if links else value_td.get_text(strip=True)
        elif field == "Linkedin Url":
            link = value_td.find("a")
            value = link["href"] if link else value_td.get_text(strip=True)
        else:
            value = value_td.get_text(strip=True)

        company_info[field] = value

    return company_info


async def crawl_full_job_with_tabs(job_url):
    """Async version: render a full job page and extract Job Info + Company Info + Job Description + Website."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print(f"🌐 Opening {job_url}")
        
        # Increase initial page load timeout and wait
        await page.goto(job_url, wait_until="networkidle", timeout=90000)
        await page.wait_for_timeout(3000)  # Initial wait for JS to settle

        result = {"job_url": job_url}

        # --- Tab 1: Job Info (default) ---
        html_job = await page.content()
        result.update(parse_job_sections(html_job))

        # --- Tab 2: Company Info (improved) ---
        try:
            # Click Company Info tab with retry
            for attempt in range(3):
                try:
                    await page.click("text=Company Info", timeout=5000)
                    # Wait for table to appear
                    await page.wait_for_selector("table.table-auto", timeout=5000)
                    await page.wait_for_timeout(2000)  # Additional wait for content
                    
                    html_company = await page.content()
                    company_data = parse_company_info_table(html_company)
                    
                    # Verify we got actual data
                    if company_data and not isinstance(company_data, str) and len(company_data) > 0:
                        result["company_info"] = company_data
                        break
                    else:
                        print(f"⚠️ Company Info attempt {attempt+1}: Empty data, retrying...")
                        await page.wait_for_timeout(2000)
                except Exception as e:
                    print(f"⚠️ Company Info attempt {attempt+1} failed: {e}")
                    await page.wait_for_timeout(2000)
            else:
                print("❌ All attempts to get company info failed")
                result["company_info"] = "N/A"
        except Exception as e:
            print(f"⚠️ Company Info section failed: {e}")
            result["company_info"] = "N/A"

        # --- Tab 3: Job Description (improved) ---
        try:
            await page.click("text=Job Description", timeout=5000)
            await page.wait_for_timeout(3000)
            await page.wait_for_selector("div.flex.flex-col", timeout=5000)
            html_desc = await page.content()
            soup_desc = BeautifulSoup(html_desc, "html.parser")
            desc_section = soup_desc.find("div", class_="flex flex-col")
            result["job_description"] = (
                desc_section.get_text(" ", strip=True) if desc_section else "N/A"
            )
        except Exception as e:
            print(f"⚠️ Job Description not found: {e}")
            result["job_description"] = "N/A"

        # --- Website extraction (async-safe) ---
        try:
            website_url = None

            website_selector_candidates = [
                'button:has-text("Website")',
                'a:has-text("Website")',
                '[role="button"]:has-text("Website")',
                '[data-test="company-website"]',
            ]

            website_elem = None
            for sel in website_selector_candidates:
                try:
                    website_elem = await page.query_selector(sel)
                except Exception:
                    website_elem = None
                if website_elem:
                    break

            if website_elem:
                try:
                    async with page.context.expect_page(timeout=4000) as popup_info:
                        await website_elem.click()
                    popup = await popup_info.value
                    try:
                        await popup.wait_for_load_state("load", timeout=5000)
                    except Exception:
                        pass
                    popup_url = popup.url or None
                    if popup_url and popup_url.startswith(("http://", "https://")) and "hiring.cafe" not in popup_url:
                        website_url = popup_url
                    try:
                        await popup.close()
                    except Exception:
                        pass
                except Exception:
                    try:
                        original_url = page.url
                        await website_elem.click()
                        await page.wait_for_timeout(1500)
                        new_url = page.url
                        if (
                            new_url != original_url
                            and new_url.startswith(("http://", "https://"))
                            and "hiring.cafe" not in new_url
                        ):
                            website_url = new_url
                        else:
                            href = await website_elem.get_attribute("href")
                            if not href:
                                href = await website_elem.get_attribute("data-href") or await website_elem.get_attribute("data-url")
                            if href and href.startswith(("http://", "https://")) and "hiring.cafe" not in href:
                                website_url = href
                    except Exception:
                        pass

            if not website_url:
                html_after = await page.content()
                soup_after = BeautifulSoup(html_after, "html.parser")
                a = soup_after.find("a", string=re.compile(r'Website', re.I))
                if a and a.get("href"):
                    href = a["href"]
                    if href.startswith(("http://", "https://")) and "hiring.cafe" not in href:
                        website_url = href
                if not website_url:
                    btn = soup_after.find(
                        lambda tag: tag.name in ["button", "div", "span"]
                        and tag.get_text(strip=True)
                        and "website" in tag.get_text(strip=True).lower()
                    )
                    if btn:
                        parent = btn.parent
                        if parent:
                            link = parent.find("a", href=True)
                            if link:
                                href = link["href"]
                                if href.startswith(("http://", "https://")) and "hiring.cafe" not in href:
                                    website_url = href
                if not website_url:
                    for link in soup_after.find_all("a", href=True):
                        href = link["href"]
                        if href.startswith(("http://", "https://")) and "hiring.cafe" not in href:
                            website_url = href
                            break

            result["company_website"] = website_url or "N/A"
        except Exception as e:
            print(f"⚠️ Website extraction failed: {e}")
            result["company_website"] = "N/A"

        await page.wait_for_timeout(1000)  # Final wait before closing
        await browser.close()
        return result