#!/usr/bin/env python3
"""
Clean and normalize Upwork job data from Firecrawl agent output.
Reads JSON from stdin, outputs cleaned JSON to stdout.

Usage:
  echo '<firecrawl_json>' | python3 scrape_upwork.py
  python3 scrape_upwork.py < input.json
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta

PHT = timezone(timedelta(hours=8))


def clean_title(title: str) -> str:
    """Remove HTML artifacts from Upwork job titles."""
    # Remove span tags with class="highlight"
    title = re.sub(r'<[^>]+>', '', title)
    # Clean up extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def parse_relative_date(date_str: str) -> str | None:
    """Parse Upwork relative dates like 'Posted yesterday', 'Posted 2 days ago'."""
    if not date_str:
        return None

    date_str = date_str.strip().lower()

    # "posted just now" or "posted today"
    if 'just now' in date_str or 'today' in date_str:
        return datetime.now(PHT).isoformat()

    # "posted yesterday"
    if 'yesterday' in date_str:
        dt = datetime.now(PHT) - timedelta(days=1)
        return dt.isoformat()

    # "posted X days/hours/minutes ago"
    m = re.search(r'posted\s+(\d+)\s+(minute|hour|day|week)s?\s+ago', date_str)
    if m:
        num = int(m.group(1))
        unit = m.group(2).lower()
        delta = {
            'minute': timedelta(minutes=num),
            'hour': timedelta(hours=num),
            'day': timedelta(days=num),
            'week': timedelta(weeks=num),
        }.get(unit)
        if delta:
            dt = datetime.now(PHT) - delta
            return dt.isoformat()

    # "posted last week"
    if 'last week' in date_str:
        dt = datetime.now(PHT) - timedelta(weeks=1)
        return dt.isoformat()

    return None


def clean_description(desc: str) -> str:
    """Truncate and clean description."""
    if not desc:
        return ""
    # Remove HTML tags
    desc = re.sub(r'<[^>]+>', '', desc)
    # Clean whitespace
    desc = re.sub(r'\s+', ' ', desc).strip()
    # Truncate to 500 chars
    return desc[:500]


def clean_skills(skills: str) -> str:
    """Clean skills string."""
    if not skills:
        return "Not specified"
    # Remove HTML tags
    skills = re.sub(r'<[^>]+>', '', skills)
    return skills.strip()


def normalize_job(job: dict) -> dict:
    """Normalize a single Upwork job to match the OnlineJobs format."""
    return {
        "url": job.get("url", ""),
        "job_title": clean_title(job.get("job_title", "")),
        "employment_type": job.get("employment_type", "Not specified"),
        "date_posted": parse_relative_date(job.get("date_posted", "")) or "",
        "salary": job.get("salary", "Not specified"),
        "description": clean_description(job.get("description", "")),
        "skills_needed": clean_skills(job.get("skills_needed", "Not specified")),
        "source": "Upwork",
    }


def main():
    """Read JSON from stdin, clean and output."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle both direct array and nested structure
    jobs = []
    if isinstance(data, list):
        jobs = data
    elif isinstance(data, dict):
        # Firecrawl agent wraps in {"jobs": [...]}
        if "jobs" in data:
            jobs = data["jobs"]
        elif "data" in data and isinstance(data["data"], dict):
            if "jobs" in data["data"]:
                jobs = data["data"]["jobs"]

    if not jobs:
        print("[]")
        return

    # Normalize all jobs
    normalized = [normalize_job(j) for j in jobs]

    # Deduplicate by URL
    seen = set()
    unique = []
    for job in normalized:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)

    print(json.dumps(unique, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
