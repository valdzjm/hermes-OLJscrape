# Webscraping — Job Scraper Collection

Automated scrapers for AI Automation job listings from OnlineJobs.ph and Upwork. Built for the Hermes Agent job pipeline — scrapes listings, generates personalized proposals, and appends to a Google Sheet.

## Project Structure

```
Webscraping/
├── scripts/
│   ├── scrape_onlinejobs.py    # OnlineJobs.ph scraper (requests + BeautifulSoup)
│   └── scrape_upwork.py        # Upwork data normalizer (Firecrawl output cleaner)
├── firecrawl-tools-reference.md # Firecrawl MCP tools reference
└── README.md
```

## Scripts

### `scrape_onlinejobs.py`

Scrapes OnlineJobs.ph for AI automation job listings. **Zero API costs** — uses direct HTTP requests with `requests` + `BeautifulSoup`.

**Features:**
- Searches multiple queries: `n8n automation`, `Make.com automation`, `Zapier automation`, `automation specialist`, `AI automation`
- Filters by date (`--since` flag) to only return new listings
- Caps results (`--limit` flag) to avoid runaway scrapes
- Outputs structured JSON to stdout, progress logs to stderr
- Rate-limited with configurable delays between requests

**Usage:**

```bash
# Scrape all listings (up to 30)
python3 scripts/scrape_onlinejobs.py --limit 30

# Scrape only listings newer than a specific date
python3 scripts/scrape_onlinejobs.py --since "2026-05-25T19:00:00+08:00" --limit 30
```

**Output format (JSON array):**

```json
[
  {
    "url": "https://www.onlinejobs.ph/jobseekers/job/...",
    "job_title": "n8n Automation Specialist",
    "employment_type": "Full Time",
    "date_posted": "2026-05-27T11:54:38+08:00",
    "salary": "$1,800.00 - $2,200.00 per month",
    "description": "We are looking for...",
    "skills_needed": "n8n, Make.com, Zapier"
  }
]
```

**Dependencies:**

```bash
pip install requests beautifulsoup4
```

### `scrape_upwork.py`

Normalizes and cleans Upwork job data from Firecrawl agent/scrape output. Reads JSON from stdin, cleans HTML artifacts from titles, parses relative dates into ISO-8601, and truncates descriptions.

**Usage:**

```bash
# Pipe Firecrawl output through the normalizer
echo '<firecrawl_json>' | python3 scripts/scrape_upwork.py

# Or from a file
python3 scripts/scrape_upwork.py < upwork_raw.json
```

**What it does:**
- Removes `<span class="highlight">` HTML artifacts from job titles
- Converts relative dates ("Posted yesterday", "Posted 3 days ago") to ISO-8601
- Truncates descriptions to 500 characters
- Adds `"source": "Upwork"` tag to each job

**Dependencies:** Python standard library only (json, re, sys, datetime).

## Google Sheet Integration

Scraped jobs are appended to a Google Sheet with this column layout:

| Column | Field |
|--------|-------|
| A | Status (New / Applied / Discarded) |
| B | Job URL |
| C | Job Title |
| D | Employment Type |
| E | Date Posted |
| F | Salary |
| G | Description |
| H | Skills Needed |
| I | Subject (proposal) |
| J | Message (proposal) |
| K | Source (OnlineJobs.ph / Upwork) |

## Hermes Agent Skill

This project is used by the `onlinejobs-scraper` Hermes Agent skill, which automates the full pipeline:
1. Read last-run timestamp
2. Run the scraper with `--since` filter
3. Deduplicate against existing sheet entries
4. Generate personalized proposals for each new job
5. Append rows to the Google Sheet
6. Update the last-run timestamp

## Notes

- **OnlineJobs.ph** is the primary source (free, no API costs, Philippines-focused)
- **Upwork** scraping requires Firecrawl credits and has US-only location restriction challenges — manual link scraping is supported via the Hermes skill
- All timestamps use Asia/Manila timezone (UTC+8)
- The scraper respects rate limits with configurable delays between requests
