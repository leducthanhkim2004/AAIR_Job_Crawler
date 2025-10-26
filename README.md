# AAIR_Job_Crawler
Collect data from Hiring Caffe job posting 

## Overview
This repository contains web crawlers and helpers to collect job data (examples: hiring.cafe and Apollo crawlers). Key folders:
- `web_Crawler/crawl_website/` — crawlers and job parsing tools
- `web_Crawler/utils/` — helpers (logging, config, folder utilities)
- `apolo_Crawl/` — Apollo crawler (cookies/profile usage)
- `web_Crawler/test/` — pytest unit tests

> Note: run commands from the repository root: `C:\Users\leduc\aair_lab`.And hiring_caffe_crawl.py is in progress and released soon

## Prerequisites
- Python 3.8+ (3.10 or 3.11 recommended)
- pip
- Git
- (Optional) Playwright for browser automation

## Quick setup (PowerShell)
Open PowerShell and run these steps from repo root:

1) Create and activate a virtual environment

```powershell
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
# or CMD
# .\.venv\Scripts\activate.bat
```

2) Install dependencies


```powershell
python -m pip install -r requirements.txt
```



3) Install Playwright browsers (when using Playwright scripts)

```powershell
python -m playwright install
```



## Configuration
Main config file (example) is at:

```
web_Crawler/config/hiring_caffe_config.yaml
```


## Run crawlers
- Hiring.cafe crawler (package-aware run):

```powershell
python -m web_Crawler.crawl_website._hiring_caffe_crawl
```




## Running tests
Run pytest from the repository root (this ensures package imports resolve):

```powershell
python -m pytest -q
# or a single test file
python -m pytest web_Crawler/test/test_hiring_crawl.py -q
```

If `pytest` is not found, make sure the virtualenv is active and `pytest` is installed.


## Common troubleshooting
- ModuleNotFoundError / attempted relative import:
  - Run scripts/tests from the repository root.
  - Ensure `web_Crawler/__init__.py`, `web_Crawler/crawl_website/__init__.py`, and `web_Crawler/utils/__init__.py` exist.
  - Or install the package in editable mode: `python -m pip install -e .`.

- Playwright-rendered content missing:
  - Use appropriate waits in Playwright (e.g., `page.wait_for_selector(...)`) before reading `page.content()`.

- Cookie / SSO issues with automation:
  - Google SSO and some sites block automated browsers. Workarounds: manual login + persistent Playwright profile, exporting/importing cookies, or use official APIs when available.
