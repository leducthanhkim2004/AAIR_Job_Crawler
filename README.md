# 🧠 AAIR Job Crawler

A modular, Playwright-powered crawler for extracting job data from **HiringCafe**, serving as the **data ingestion foundation** for an upcoming **AI-based job interview agent in Vietnam**.

---

## 📁 Project Structure

| Folder                                        | Description                                                 |
| --------------------------------------------- | ----------------------------------------------------------- |
| `web_Crawler/crawl_website/`                  | Core crawlers, parsers, and site-specific logic             |
| `web_Crawler/utils/`                          | Shared utilities — logging, folder setup, YAML config, etc. |
| `apolo_Crawl/`                                | Apollo.io crawler assets and browser profile data           |
| `web_Crawler/config/hiring_caffe_config.yaml` | Main configuration file                                     |
| `crawled_data/`                               | Output directory for crawled results and logs               |

---

## ⚙️ Prerequisites

* **Python** ≥ 3.8
* **Git**
* **Internet connection** (Playwright browser download required)

---

## 🚀 Quick Setup (PowerShell, Windows)

Run all commands from the **repository root**.

### 1️⃣ Create & activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2️⃣ Install dependencies

If you have `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Otherwise, install manually:

```powershell
python -m pip install --upgrade pip
python -m pip install playwright requests beautifulsoup4 PyYAML pytest
```

### 3️⃣ Install Playwright browsers (only once)

```powershell
python -m playwright install
```

---

## ⚙️ Configuration

Edit the file:

```
web_Crawler/config/hiring_caffe_config.yaml
```

Available keys:

```yaml
BASE_URL: "https://hiring.cafe/jobs/it"
SAVE_ROOT_DIR: "./data"
TIMEOUT: 60000
HEADERS:
  User-Agent: "Mozilla/5.0 ..."
```

> The configuration controls where logs/results are saved, timeout behavior, and request headers.

You can load it in code with:

```python
from web_Crawler.utils.utils import load_config
config = load_config("web_Crawler/config/hiring_caffe_config.yaml")
```

---

## 🧙‍♂️ Running the Crawler

Always run from the **repository root** to ensure package imports work properly.

### Full run (with async-safe entry)

```powershell
python -m web_Crawler.crawl_website._hiring_caffe_IT_crawl
```

This command will:

* Launch a Playwright Chromium browser
* Scroll through all visible jobs on HiringCafe
* Automatically click the “>” button on each company card to reveal hidden job postings
* Continue scrolling until no new DOM elements are detected
* Save all unique job URLs and details to JSON files in your result folder

---

## 🧥 Debug & Logging

* Logs are saved automatically under:

  ```
  ./data/logs_it_vn/
  ./data/result_it_vn/
  ```
* To watch logs in real time:

  ```powershell
  Get-Content .\data\logs_it_vn\latest.log -Wait
  ```
* To enable debug-level logs:
  Edit your YAML config or adjust the logger setup in code:

  ```python
  self.logger.setLevel("DEBUG")
  ```

---

## 📦 Output Files

After a successful crawl, you’ll find:

| File                              | Description                                           |
| --------------------------------- | ----------------------------------------------------- |
| `job_links_all_safe_dynamic.json` | All unique job links (visible + hidden carousel jobs) |
| `*.json`                          | Individual job postings with parsed metadata          |
| Log files                         | Stored under `/logs_it_vn/` with timestamps           |

Example:

```
data/
 ├── result_it_vn/
 │   ├─ job_links_all_safe_dynamic.json
 │   ├─ 6d9a12c3e9f3.json
 │   └─ ...
 └─ logs_it_vn/
     ├─ run_2025-10-30.log
     └─ latest.log
```

---

## 💡 Notes & Tips

* The crawler runs best when `headless=False` during debugging,
  so you can visually confirm that scrolling and clicking behaviors work.
* If you see **TimeoutError: networkidle**, replace `wait_until="networkidle"`
  with `wait_until="domcontentloaded"` in your code — this site uses dynamic JavaScript loading.
* For very large datasets (6,000+ jobs), increase:

  ```python
  max_scroll_rounds = 120
  scroll_sleep = 2.5
  ```

---



**Developed with ❤️ by AAIR Lab**
_Vietnamese-German University 
