# 🧠 AAIR Job Crawler

A modular, Playwright-powered crawler for extracting job data from **HiringCafe**, serving as the **data ingestion foundation** for an upcoming **AI-based job interview agent in Vietnam**.

---

## 📁 Project Structure

| Folder | Description |
|---------|-------------|
| `web_Crawler/crawl_website/` | Core crawlers, parsers, and site-specific logic |
| `web_Crawler/utils/` | Shared utilities — logging, folder setup, YAML config, etc. |
| `apolo_Crawl/` | Apollo.io crawler assets and browser profile data |
| `web_Crawler/config/hiring_caffe_config.yaml` | Main configuration file |
| `crawled_data/` | Output directory for crawled results and logs |

---

## ⚙️ Prerequisites

- **Python** ≥ 3.8  
- **Git**
- **Internet connection** (Playwright browser download required)

---

## 🚀 Quick Setup (PowerShell, Windows)

Run all commands from the **repository root**.

### 1️⃣ Create & activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
