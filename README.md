# AAIR_Job_Crawler
Collect data from Hiring Caffe job posting . Class _hiring_caffe_crawl.py is in progress for modifying . Run job.py just paste 
```
job_url = "https://hiring.cafe/viewjob/dxxmss9dwt2gcdfx"
```
Please replace this url by view job post on hiring caffe and run 
## Overview
This repository contains web crawlers and helpers to collect job data (examples: hiring.cafe and Apollo crawlers). Key folders:
- `web_Crawler/crawl_website/` — crawlers and job parsing tools
- `web_Crawler/utils/` — helpers (logging, config, folder utilities)
- `apolo_Crawl/` — Apollo crawler (cookies/profile usage)
- `web_Crawler/test/` — pytest unit tests

> Note: run commands from the repository root: `C:\Users\leduc\aair_lab`.And hiring_caffe_crawl.py is in progress and released soon

## Prerequisites
- Python 3.8+ (3.10 or 3.11 recommended)
## Quick setup (PowerShell)

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



## Configuration
Main config file (example) is at:

```
web_Crawler/config/hiring_caffe_config.yaml
```


## Run crawlers
- Hiring.cafe crawler (package-aware run): running this command 

```
python -m web_Crawler.crawl_website._hiring_caffe_crawl
```




