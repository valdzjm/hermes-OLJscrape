#!/usr/bin/env python3
"""
Scrape OnlineJobs.ph "AI Automation" job listings using requests + BeautifulSoup.
Zero external API costs. Outputs structured JSON to stdout; progress logs to stderr.
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

# ── Constants ────────────────────────────────────────────────────────────────

SEARCH_URL = "https://www.onlinejobs.ph/jobseekers/jobsearch"
SEARCH_QUERIES = [
    "n8n automation",
    "Make.com automation",
    "Zapier automation",
    "automation specialist",
    "AI automation",
]
BASE_URL = "https://www.onlinejobs.ph"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}
PHT = timezone(timedelta(hours=8))  # Asia/Manila
PER_PAGE = 30
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_PAGES = 1.5  # seconds between pagination requests
DELAY_BETWEEN_DETAIL = 1.5  # seconds between detail page requests


def log(msg: str) -> None:
    """Print a progress message to stderr."""
    print(msg, file=sys.stderr, flush=True)


def parse_search_date(date_str: str) -> str | None:
    """
    Parse a date string from the search results page into ISO-8601 PHT.
    Handles both absolute dates and relative time strings.
    """
    if not date_str:
        return None

    # Absolute format: "Posted on 2026-05-15 14:20:26"
    m = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", date_str)
    if m:
        dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=PHT).isoformat()

    # Relative: "Posted X minutes/hours/days ago"
    m = re.search(r"Posted\s+(\d+)\s+(minute|hour|day)s?\s+ago", date_str, re.I)
    if m:
        num = int(m.group(1))
        unit = m.group(2).lower()
        delta = {
            "minute": timedelta(minutes=num),
            "hour": timedelta(hours=num),
            "day": timedelta(days=num),
        }.get(unit)
        if delta:
            dt = datetime.now(PHT) - delta
            return dt.isoformat()

    return None


def parse_detail_date(date_str: str) -> str | None:
    """Parse date from detail page (may differ in format)."""
    if not date_str:
        return None

    # Try common formats
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%B %d, %Y %I:%M %p",
        "%B %d, %Y",
        "%b %d, %Y",
        "%m/%d/%Y",
    ):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.replace(tzinfo=PHT).isoformat()
        except ValueError:
            continue

    # Fall back to the search-page parser
    return parse_search_date(date_str)


def make_session() -> requests.Session:
    """Create a requests session with retry and realistic headers."""
    session = requests.Session()
    session.headers.update(HEADERS)
    adapter = requests.adapters.HTTPAdapter(
        max_retries=requests.adapters.Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# ── Search-page scraping ─────────────────────────────────────────────────────


def fetch_search_page(session: requests.Session, query: str, offset: int = 0) -> str | None:
    """Fetch one page of search results. Returns HTML or None on failure."""
    url = SEARCH_URL
    params = {"jobkeyword": query, "isFromJobsearchForm": "1"}
    if offset > 0:
        url = f"{SEARCH_URL}/{offset}"
    try:
        resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        log(f"  ⚠ Failed to fetch search page (query={query!r}, offset={offset}): {e}")
        return None


def parse_search_page(html: str) -> list[dict]:
    """Extract job listings from one search-results page."""
    soup = BeautifulSoup(html, "html.parser")
    results_div = soup.find("div", class_="results")
    if not results_div:
        return []

    cards = results_div.find_all(
        "a",
        href=lambda h: h
        and "/jobseekers/job/" in h
        and "jobsearch" not in h,
        recursive=False,
    )

    jobs = []
    for card in cards:
        try:
            href = card.get("href", "")
            url = href if href.startswith("http") else BASE_URL + href

            # Skip duplicate numeric-ID links (every job has a slug + numeric link)
            if re.search(r"/jobseekers/job/\d+$", href):
                continue

            # Title + employment type
            h4 = card.find("h4")
            if not h4:
                continue

            badge = h4.find("span", class_="badge")
            employment_type = badge.get_text(strip=True) if badge else "Not specified"
            # Remove badge text from title
            title_text = h4.get_text(strip=True)
            if badge:
                title_text = title_text.replace(badge.get_text(strip=True), "").strip()

            # Date
            p_tag = card.find("p", attrs={"data-temp": True})
            posted_date_iso = None
            posted_date_raw = ""
            if p_tag:
                posted_date_raw = p_tag.get("data-temp", "")
                posted_date_iso = parse_search_date(
                    f"Posted on {posted_date_raw}" if posted_date_raw else ""
                )

            # Salary
            salary = "Not specified"
            dd = card.find("dd", class_="col")
            if dd:
                salary_text = dd.get_text(strip=True)
                if salary_text:
                    salary = salary_text

            # Description
            desc_div = card.find("div", class_="desc")
            description = ""
            if desc_div:
                # Remove the "See More" link
                for see_more in desc_div.find_all("a"):
                    see_more.decompose()
                description = desc_div.get_text(separator=" ", strip=True)[:500]

            # Skills / tags
            skills = []
            tag_div = card.find("div", class_="job-tag")
            if tag_div:
                for badge_a in tag_div.find_all("a", class_="badge"):
                    skill_text = badge_a.get_text(strip=True)
                    if skill_text:
                        skills.append(skill_text)
            skills_str = ", ".join(skills) if skills else "Not specified"

            jobs.append(
                {
                    "url": url,
                    "job_title": title_text,
                    "employment_type": employment_type,
                    "date_posted": posted_date_iso or "",
                    "salary": salary,
                    "description": description,
                    "skills_needed": skills_str,
                }
            )
        except Exception as e:
            log(f"  ⚠ Failed to parse a job card: {e}")
            continue

    return jobs


def scrape_all_search_pages(
    session: requests.Session, queries: list[str], limit: int | None = None
) -> list[dict]:
    """Iterate through paginated search results for multiple queries and collect all job cards."""
    all_jobs: list[dict] = []
    seen_urls: set[str] = set()

    for qi, query in enumerate(queries):
        log(f"[{qi + 1}/{len(queries)}] Searching for: {query!r}")
        offset = 0

        while True:
            log(f"  Scraping search page (offset={offset})...")
            html = fetch_search_page(session, query, offset)
            if not html:
                break

            page_jobs = parse_search_page(html)
            if not page_jobs:
                log("  No more listings found.")
                break

            new_count = 0
            for job in page_jobs:
                if job["url"] not in seen_urls:
                    seen_urls.add(job["url"])
                    all_jobs.append(job)
                    new_count += 1

                if limit and len(all_jobs) >= limit:
                    log(f"  Reached limit of {limit} listings.")
                    return all_jobs

            log(f"  Fetched {new_count} new listings (total: {len(all_jobs)})")

            if new_count == 0:
                break

            offset += PER_PAGE
            time.sleep(DELAY_BETWEEN_PAGES)

        time.sleep(DELAY_BETWEEN_PAGES)  # pause between queries

    return all_jobs


# ── Detail-page scraping ─────────────────────────────────────────────────────


def fetch_detail_page(session: requests.Session, url: str) -> str | None:
    """Fetch a single job detail page. Returns HTML or None on failure."""
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        log(f"  ⚠ Detail page failed: {url} — {e}")
        return None


def parse_detail_page(html: str, existing: dict) -> dict:
    """
    Extract richer data from a job detail page and merge into existing dict.
    Only overwrites fields if the detail page provides better data.
    """
    soup = BeautifulSoup(html, "html.parser")
    result = dict(existing)

    try:
        # Job title — usually in an <h1> or prominent heading
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
            if title:
                result["job_title"] = title

        # Employment type — look for badges or specific sections
        for badge in soup.find_all("span", class_=lambda c: c and "badge" in c):
            text = badge.get_text(strip=True).lower()
            if text in ("full time", "full-time", "part time", "part-time", "gig", "freelance"):
                result["employment_type"] = badge.get_text(strip=True)
                break

        # Salary — look for salary section
        # Common patterns: <dt>Salary</dt><dd>...</dd> or a section with ₱/$
        salary_section = soup.find(string=re.compile(r"Salary|Compensation|Pay", re.I))
        if salary_section:
            parent = salary_section.find_parent()
            if parent:
                sibling = parent.find_next_sibling()
                if sibling:
                    salary_text = sibling.get_text(strip=True)
                    if salary_text:
                        result["salary"] = salary_text

        # If salary still "Not specified", look for ₱ or $ patterns
        if result["salary"] == "Not specified":
            body_text = soup.get_text()
            salary_match = re.search(
                r"[\$₱]\s*[\d,]+(?:\s*[-–]\s*[\$₱]?\s*[\d,]+)?(?:\s*/\s*\w+)?",
                body_text,
            )
            if salary_match:
                result["salary"] = salary_match.group(0).strip()

        # Description — main job description text
        # Look for the largest text block or a specific description section
        desc_div = soup.find("div", class_=lambda c: c and "job-description" in str(c).lower())
        if not desc_div:
            desc_div = soup.find("div", class_=lambda c: c and "description" in str(c).lower())
        if desc_div:
            desc_text = desc_div.get_text(separator=" ", strip=True)[:500]
            if desc_text:
                result["description"] = desc_text

        # Skills — look for skill tags or requirements section
        skill_tags = []
        for tag_div in soup.find_all("div", class_=lambda c: c and "tag" in str(c).lower()):
            for a_tag in tag_div.find_all("a"):
                skill = a_tag.get_text(strip=True)
                if skill and len(skill) < 50:
                    skill_tags.append(skill)
        if skill_tags:
            result["skills_needed"] = ", ".join(skill_tags)

        # If no skills found via tags, look for requirements section
        if result["skills_needed"] == "Not specified":
            req_section = soup.find(
                string=re.compile(r"Requirements|Skills|Qualifications", re.I)
            )
            if req_section:
                parent = req_section.find_parent()
                if parent:
                    # Get list items in the next sibling or within the parent
                    items = parent.find_all("li")
                    if items:
                        skills = [li.get_text(strip=True) for li in items[:10]]
                        result["skills_needed"] = ", ".join(skills)

        # Date posted — try to get a more precise date from the detail page
        date_el = soup.find(string=re.compile(r"Posted on|Date Posted|Posted:", re.I))
        if date_el:
            date_text = date_el.strip()
            parsed = parse_detail_date(date_text)
            if parsed:
                result["date_posted"] = parsed

    except Exception as e:
        log(f"  ⚠ Error parsing detail page: {e}")

    return result


def enrich_with_details(session: requests.Session, jobs: list[dict]) -> list[dict]:
    """Fetch detail pages for each job and merge richer data."""
    total = len(jobs)
    for i, job in enumerate(jobs):
        log(f"Fetching detail {i + 1}/{total}: {job['url']}")
        html = fetch_detail_page(session, job["url"])
        if html:
            jobs[i] = parse_detail_page(html, job)
        time.sleep(DELAY_BETWEEN_DETAIL)
    return jobs


# ── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Scrape OnlineJobs.ph AI Automation job listings."
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Max number of listings to return."
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Only return listings posted after this ISO-8601 timestamp.",
    )
    parser.add_argument(
        "--with-detail",
        action="store_true",
        help="Enrich listings by fetching each detail page (slower, may corrupt salary data).",
    )
    parser.add_argument(
        "--query",
        type=str,
        nargs="+",
        default=None,
        help="Override default search queries (space-separated).",
    )
    args = parser.parse_args()

    session = make_session()
    queries = args.query if args.query else SEARCH_QUERIES

    # Phase 1: scrape search results
    log(f"Phase 1: Scraping {len(queries)} search queries...")
    jobs = scrape_all_search_pages(session, queries, limit=args.limit)
    log(f"Collected {len(jobs)} listings from search results.")

    if not jobs:
        log("No listings found. Exiting.")
        print("[]")
        return

    # Phase 2: filter by --since
    if args.since:
        try:
            since_dt = datetime.fromisoformat(args.since)
            if since_dt.tzinfo is None:
                since_dt = since_dt.replace(tzinfo=PHT)
            before = len(jobs)
            jobs = [
                j
                for j in jobs
                if j["date_posted"]
                and datetime.fromisoformat(j["date_posted"]) > since_dt
            ]
            log(f"Filtered by --since: {before} → {len(jobs)} listings.")
        except ValueError as e:
            log(f"⚠ Invalid --since timestamp: {e}")
            sys.exit(1)

    # Phase 3: enrich with detail pages (opt-in only)
    if args.with_detail:
        log("Phase 2: Fetching detail pages for enrichment...")
        jobs = enrich_with_details(session, jobs)

    # Output
    log(f"Done. Outputting {len(jobs)} listings.")
    print(json.dumps(jobs, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
