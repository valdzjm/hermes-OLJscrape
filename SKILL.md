---
name: onlinejobs-scraper
description: >
  Scrape AI Automation Jobs from OnlineJobs.ph using a local Python script
  (zero API cost), generate personalized proposals for each listing, and
  append everything to the Hermes Scraper Google Sheet. Also supports manual
  Upwork job links provided by the user. Triggers when the user says "run
  the job scraper", "scrape onlinejobs", "find new AI jobs", or is invoked
  by the scheduled cron job.
tags: [scraping, jobs, automation, proposals, requirements-scanning, upwork]
---

# Job Scraper + Proposal Generator (OnlineJobs.ph + Upwork)

You are running an automated job scraper and proposal generator. Follow these steps **exactly and in order**. Do not skip steps. Do not improvise.

This skill scrapes from **OnlineJobs.ph** via a local Python script (zero API cost). **Upwork** is not included in the automated scrape — the user can provide individual Upwork job URLs for manual processing.

For each scraped job, you also generate a personalized proposal (Subject + Message) tailored to the user's profile as an AI Automation Specialist.

## User Profile (for proposal generation)

- **Name**: Justin Mark Valdez
- **Role**: AI Automation Specialist | Cloud & Infrastructure Engineer
- **Location**: Pangasinan, Philippines
- **Experience**: 4+ years cloud/infrastructure, 1+ year freelance AI automation (since April 2025)
- **Previous role**: System Administrator / Change Analyst at DXC Technology (Sept 2022 – March 2026) — managed Windows Server environments, ITIL/ITSM change management, ~20 server builds/month, CAB meetings, SOPs
- **Core tools**: n8n, Make.com, Zapier, Claude Code, GoHighLevel, Airtable
- **AI/LLM**: OpenAI, Claude, Gemini, Google Vertex AI, ElevenLabs, Vapi
- **Cloud**: AWS (Solutions Architect Associate certified), Azure (AZ-104), GCP, Docker, Terraform, Ansible
- **Databases**: PostgreSQL, MySQL, Redis, Supabase
- **Scripting**: Python, Bash, PowerShell
- **Certifications**: AWS Solutions Architect Associate, AWS Cloud Practitioner, Azure Admin (AZ-104), Azure Fundamentals (AZ-900), Oracle Cloud Foundations, ITIL 4 Foundation
- **Education**: BS Electronics Engineering (TIP, 2022), BS Mechatronics Technology (TUTP, 2017)
- **Portfolio**: jmvautomates.tech
- **OnlineJobs.ph profile**: v2.onlinejobs.ph/jobseekers/info/2210652
- **Upwork**: upwork.com/freelancers/~01b70d87d89f9b7ae0
- **LinkedIn**: linkedin.com/in/justinmarkvaldez

### Project Reference (CRITICAL)

**Before generating any proposal, load the project portfolio:**
`skill_view(name='onlinejobs-scraper', file_path='references/justin-portfolio.md')`

**Resume reference (for certifications, experience, education):**
`skill_view(name='onlinejobs-scraper', file_path='references/justin-resume.md')`

**NEVER fabricate project details, client names, metrics, or tools.** Only reference projects, tools, and outcomes that are documented in the portfolio. If a job asks for an example you don't have, use one of these strategies:
1. Reference the closest real project from the portfolio
2. Use honest phrasing: "I've built similar systems using..." and describe the actual tools/approach
3. Add a placeholder: **[✏️ FILL IN: specific project example]**

**Honesty rules for skill ratings:**
- Never rate yourself 5/5 unless you could teach the tool
- Vapi: 3/5 (used in AI Appointment Setter project, not deep custom)
- ElevenLabs: 2-3/5 (limited experience)
- Claude Code: 4/5 (daily development tool)
- n8n: 4/5 (50+ production workflows, primary tool)
- Make.com: 4/5 (Xero-Asana, Email Attachment projects)
- Zapier: 4/5 (Content Repurposing, Lead Qualification, CRM projects)
- GoHighLevel: 3-4/5 (used in client integrations)
- REST APIs / Webhooks: 5/5 (foundation of every project)
- AWS: 4/5 (Solutions Architect Certified, 4+ years infrastructure)
- Azure: 4/5 (AZ-104 certified)
- Python: 4/5 (primary scripting language)
- PostgreSQL/Supabase: 4/5 (used in multiple projects)

## Constants

- **Search queries (OnlineJobs.ph)**: `n8n automation`, `Make.com automation`, `Zapier automation`, `automation specialist`, `AI automation`
- **Scraper script (OnlineJobs.ph)**: `/home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_onlinejobs.py`
- **Target Google Sheet ID**: `1oNdtp4iSTKus1cDUWcP1ZvbLJJeuQ6QjKQH0Rmuh81k`
- **Worksheet name**: `jobs`
- **Column layout (row 1 header — do NOT modify)**:
  - A: Status
  - B: Job URL
  - C: Job Title
  - D: Employment Type
  - E: Date Posted
  - F: Salary
  - G: Description
  - H: Skills Needed
  - I: Subject
  - J: Message
  - K: Source (OnlineJobs.ph or Upwork)
- **Append range**: `jobs!A:K`
- **Dedup column**: B (Job URL)
- **State file (OnlineJobs.ph)**: `/home/jmvadmin/.hermes/profiles/work-assistant/state/job-scraper-last-run.txt`
- **Timezone**: Asia/Manila (UTC+8)
- **Per-run cap**: 30 new jobs maximum (OnlineJobs.ph only)

## Procedure

### Step 1 — Read the last-run timestamp

Use the terminal tool:

```bash
cat /home/jmvadmin/.hermes/profiles/work-assistant/state/job-scraper-last-run.txt
```

Store the trimmed result as `last_run_iso` (e.g., `2026-05-15T18:00:00+08:00`). If the file is empty or unreadable, default to `2020-01-01T00:00:00+08:00`.

### Step 2 — Run the local Python scraper

Use the terminal tool. Pass `last_run_iso` to the script's `--since` flag so it filters server-side and returns only listings newer than the last run. Cap at 30:

```bash
python3 /home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_onlinejobs.py --since "<last_run_iso>" --limit 30
```

Substitute `<last_run_iso>` with the value from Step 1.

The script outputs a JSON array on stdout (progress messages go to stderr — ignore those). Parse stdout as JSON. Each object has these exact keys:

- `url`
- `job_title`
- `employment_type`
- `date_posted` (ISO-8601 with +08:00)
- `salary`
- `description`
- `skills_needed`

If the JSON array is empty, skip to Step 7 with the "no new jobs" summary and **do not update the state file**.

### Step 2b — Manual Upwork link scraping (user-provided URLs only)

Upwork is NOT included in the automated scrape. If the user provides a specific Upwork job URL, scrape it individually:

1. Use `firecrawl_scrape` with JSON extraction on the job page
2. Check `location_restriction` field — if it contains "U.S.", "United States", or similar, warn the user and skip
3. If no restriction, generate a proposal and append to the sheet

**Prompt for individual Upwork job scrape:**
- `formats: ["json"]`
- `jsonOptions.prompt`: "Extract job details: job title, employment type (hourly/fixed), budget/salary range, description (up to 500 chars), skills/tags, and any location restriction (e.g. 'Only freelancers located in the U.S. may apply'). Return location_restriction as 'None' if no restriction found."
- `jsonOptions.schema`: `{"type": "object", "properties": {"job_title": {"type": "string"}, "employment_type": {"type": "string"}, "salary": {"type": "string"}, "description": {"type": "string"}, "skills_needed": {"type": "string"}, "location_restriction": {"type": "string"}}}`

**If location_restriction contains US/United States:** Do NOT add to sheet. Tell the user: "This job is restricted to US-based freelancers."

**If location_restriction is "None" or empty:** Generate proposal, dedup against sheet, append.

No state file tracking for manual Upwork links.
```
https://www.upwork.com/jobs/span-class-highlight-Zapier-span-span-class-highlight-Make-com-span-Form-Setup_~022059486673153633521/
```
**Before running the normalizer**, you MUST:
- **Clean URLs**: Strip `span-class-highlight-` and `-span` artifacts from URL slugs. Replace with the actual keyword text. Use a regex like `re.sub(r'span-class-highlight-|-span', '', url)`.
- **Apply GHL filter**: Filter out jobs containing "GoHighLevel", "GHL", or "Go High Level" in title/description/skills BEFORE passing to the normalizer. The normalizer does NOT handle GHL filtering.
- **Normalize relative dates**: Firecrawl returns dates like "1 hour ago", "yesterday", "3 days ago", "last week". Convert to ISO-8601 with +08:00 timezone before storing. The normalizer expects this but may not always handle it correctly — verify output.
- **Use execute_code for all pre-processing** (URL cleaning + GHL filtering + date normalization) in a single Python script, then pass cleaned JSON to the normalizer OR skip the normalizer if your execute_code script already handles everything.

4. Clean the data using the normalizer script:
```bash
echo '<firecrawl_json>' | python3 /home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_upwork.py
```
   The normalizer: removes HTML artifacts from titles, parses relative dates ("Posted yesterday" → ISO-8601), truncates descriptions to 500 chars, adds `"source": "Upwork"` to each job.

5. Merge the cleaned Upwork jobs with the OnlineJobs.ph results from Step 2. Tag each OnlineJobs.ph job with `"source": "OnlineJobs.ph"`.

6. If the Firecrawl agent fails or returns no results, log a warning and continue with OnlineJobs.ph results only.

### Step 3 — Safety-net dedup against the sheet

Use the **google_sheets** MCP to read column B (Job URL):

- Spreadsheet ID: as in Constants
- Range: `jobs!B2:B`

Build a set of `existing_urls`. Drop any candidate from Step 2 whose `url` is already in this set.

If zero candidates remain after dedup, skip to Step 7 with the "no new jobs" summary and **do not update the state file**.

### Step 4 — Generate personalized proposals

**SAFEGUARD: Only generate proposals for rows where BOTH conditions are true:**
- Status is "New"
- Columns I (Subject) AND J (Message) are BOTH empty

**NEVER overwrite an existing proposal.** If a row already has a Subject or Message, skip it — even if the Status is "New". This protects against re-runs clobbering manually edited proposals.

For each eligible job candidate, generate a **Subject** and **Message** using your understanding of the job details and the User Profile above.

#### Subject rules:
- Short and specific (under 60 characters before name suffix)
- Reference the job title or key skill from the listing
- **Always append** ` — Justin Mark Valdez` at the end of the subject UNLESS the job description specifies a required subject line (e.g., "Include [word] in your subject" or "Subject must be..."). When a required subject is specified, use it exactly as instructed without adding the name.
- Examples:
  - `"n8n Automation Expert for Your Workflow Needs — Justin Mark Valdez"`
  - `"AI Automation Specialist — Make.com & Zapier — Justin Mark Valdez"`
  - `"Your Next Automation Specialist is Here — Justin Mark Valdez"`

#### Step 4a — Extract application requirements

Before generating the proposal, scan the job `description` text for application requirements. Look for these keyword patterns (case-insensitive):

- "How to Apply" / "How to apply" / "To Apply"
- "Requirements" / "Application Requirements" / "Job Requirements"
- "Must include" / "Please include" / "Should include"
- "Video" / "Video introduction" / "Video resume" / "Loom"
- "Portfolio" / "Sample work" / "Work samples"
- "Answer" / "Answer the following" / "Answer these questions"
- "Start your message with" / "Begin your application with" / "Start with the word"
- "Test" / "Trial task" / "Paid test"
- "Resume" / "CV" / "Cover letter"
- "Rate" / "Expected salary" / "Hourly rate"

If any requirements are found, extract them into a list called `requirements`.

#### Step 4b — Generate personalized proposals

For each remaining job candidate, generate a **Subject** and **Message** using your understanding of the job details, the User Profile above, and the extracted requirements from Step 4a.

#### Subject rules:
- Short and specific (under 60 characters before name suffix)
- Reference the job title or key skill from the listing
- **Always append** ` — Justin Mark Valdez` at the end of the subject UNLESS the job description specifies a required subject line (e.g., "Include [word] in your subject" or "Subject must be..."). When a required subject is specified, use it exactly as instructed without adding the name.
- Examples:
  - `"n8n Automation Expert for Your Workflow Needs — Justin Mark Valdez"`
  - `"AI Automation Specialist — Make.com & Zapier — Justin Mark Valdez"`
  - `"Your Next Automation Specialist is Here — Justin Mark Valdez"`

#### Message rules:
- **Opening**: Reference something specific from the job description (the company, the role, a specific task mentioned). Show you actually read the listing.
- **Middle**: Briefly highlight relevant experience with the tools they need (n8n, Make.com, Zapier, GoHighLevel, Airtable, Claude Code). Mention 1-2 concrete outcomes (e.g., "built workflows that saved 20+ hours/week", "automated lead pipelines end-to-end").
- **Requirements block**: If application requirements were found in Step 4a, add a section that addresses each one. For example:
  - If they ask you to "start your message with a specific word" → include that word at the start of the message
  - If they ask for your "hourly rate" or "expected salary" → include a rate or **[PLACEHOLDER: YOUR RATE]**
  - If they ask for a "video introduction" or "Loom video" → add **[📹 VIDEO REQUIRED: Record a short video intro]**
  - If they ask for "portfolio samples" → link jmvautomates.tech and add **[📎 ATTACH: Portfolio samples / case studies]**
  - If they ask you to "answer specific questions" → answer what you can, and for anything requiring personal input, add **[✏️ FILL IN: <question they asked>]**
  - If they ask for a "resume/CV" → add **[📄 ATTACH: Resume/CV]**
  - If they ask for a "test task" → acknowledge willingness and add **[📋 TEST TASK: Review requirements and confirm]**
  - If they say "start with [word]" → literally start the message with that exact word
- **Close**: Express enthusiasm and include a call to action (e.g., "I'd love to discuss how I can help — let's chat!")
- **Length**: 120-150 words MAX. Professional but conversational tone. Not robotic. User explicitly prefers short, direct proposals — hit the job's requirements, reference one real project with a metric, and close. No corporate fluff, no "I'm excited to apply," no walls of text. The shorter the better — long proposals get ignored.
- **Do NOT** include greetings like "Dear Hiring Manager" — OnlineJobs.ph proposals are more direct. Upwork proposals can be slightly more formal.
- **Do NOT** use generic filler like "I am a hard worker" or "I have 10 years of experience" unless it's backed by specifics.
- **DO** tailor each message to the specific job. A Make.com job should emphasize Make.com; an n8n job should emphasize n8n.
- **DO** use bold markers for placeholders so they stand out when reviewing: `**[PLACEHOLDER TEXT]**`
- **DO** reference REAL projects from `references/justin-portfolio.md` — never invent client names, metrics, or project details
- **DO** use honest skill ratings based on the portfolio — never inflate
- If the employer requires applying through an external form/link (not OnlineJobs), flag with `**[🔗 APPLY VIA FORM: ...]**`
- If the job post has been deleted, set Subject to "N/A - Job Post Deleted" and Message to "This job post has been deleted and is no longer available on OnlineJobs.ph."

#### Placeholder legend (for user review):
When scanning completed proposals, look for these markers that need manual input:
- `**[📹 VIDEO REQUIRED: ...]**` — Record and attach a video
- `**[📎 ATTACH: ...]**` — Attach files/links
- `**[✏️ FILL IN: ...]**` — Write a custom answer
- `**[📄 ATTACH: Resume/CV]**` — Attach your resume
- `**[📋 TEST TASK: ...]**` — Review and complete a test
- `**[PLACEHOLDER: YOUR RATE]**` — Insert your rate
- `**[🔗 APPLY VIA FORM: ...]**` — Apply through external form/link

Store the generated Subject and Message alongside each job candidate for Step 5.

### Step 5 — Append new rows to the Sheet

**Do NOT use `add_rows`** — it inserts empty rows at the top and corrupts existing data. Instead, find the last occupied row by reading column B, then write directly to the next row.

Use the **google_sheets** MCP:
1. Read `jobs!B:B` to find the last non-empty row (e.g., row N)
2. Use `update_cells` to write directly to `jobs!A(N+1):J(N+count)`

- Spreadsheet ID: as in Constants
- Values: one row per candidate, in this exact column order:

```
["New", url, job_title, employment_type, date_posted, salary, description, skills_needed, subject, message, source]
```

**Column order matters** — these must map to header columns A → K. Always set Status to "New" for newly appended rows. Set `source` to "OnlineJobs.ph" or "Upwork" based on where the job came from.

**Pitfall:** If using `batch_update` API directly, text values must use `{"stringValue": "text"}` format, not bare strings.

**Google Sheets MCP pitfall:** ALL tools with a `sheet` + `range` parameter double the sheet name (e.g., `get_sheet_data` produces `jobs!jobs!B:B`, `batch_update_cells` produces `jobs!jobs!A:J`). Workarounds:
- **For reads (Step 3):** Use `find_in_spreadsheet` instead of `get_sheet_data` — it searches by value and returns cell locations without the doubling bug.
- **For writes (Step 5):** Use `update_cells` and pass the range WITHOUT the sheet prefix (e.g., `A67:J69` instead of `jobs!A67:J69`). The `sheet` parameter already specifies the sheet.
- **Broken pipe errors:** Common with large payloads (5+ rows). Keep batch writes to 5 rows max per call. Retry once — usually works on second attempt.

### Step 6 — Update the state file

Find the **newest** `date_posted` value from the rows you just appended. Write it via terminal:

```bash
echo "<newest_onlinejobs_iso>" > /home/jmvadmin/.hermes/profiles/work-assistant/state/job-scraper-last-run.txt
```

If no new jobs were added, or if Step 5 failed, **do NOT update** the state file.

### Step 7 — Report summary

Output a concise Telegram-friendly summary:

```
📋 Job scrape complete (OnlineJobs.ph)

✅ N new jobs added (with proposals)
🕐 Run time: <current Manila time>
🔗 Sheet: https://docs.google.com/spreadsheets/d/1oNdtp4iSTKus1cDUWcP1ZvbLJJeuQ6QjKQH0Rmuh81k

Top 3 new listings:
1. <Title> — <Salary> | Subject: <Subject>
2. <Title> — <Salary> | Subject: <Subject>
3. <Title> — <Salary> | Subject: <Subject>
```

If no new jobs: a single line "No new AI automation jobs since last run."

## Fallback: Fetching full job descriptions when Firecrawl is unavailable

Both `firecrawl_scrape` and `web_extract` use Firecrawl credits — when credits are exhausted, BOTH fail. OnlineJobs.ph job pages can be scraped directly with curl since the content is server-rendered (no JS required).

**Technique:** curl + Python HTMLParser to extract the `job-description` div. Simple regex fails because the div has nested children; use depth-tracking HTMLParser:

```python
from html.parser import HTMLParser
import re

class JobDescExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_job_desc = False
        self.depth = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')
        if 'job-description' in cls:
            self.in_job_desc = True
            self.depth = 0
        if self.in_job_desc:
            self.depth += 1
            if tag in ('br', 'p', 'div', 'li'):
                self.text.append('\n')

    def handle_endtag(self, tag):
        if self.in_job_desc:
            self.depth -= 1
            if self.depth <= 0:
                self.in_job_desc = False

    def handle_data(self, data):
        if self.in_job_desc:
            self.text.append(data.strip())
```

Usage: `curl -sL -A "Mozilla/5.0 ..." "<url>" | python3 -c "<parser above>"` → clean text output.

**OnlineJobs.ph HTML notes:**
- Job description lives in `<div class="job-description">` inside `<div class="card job-post">`
- Meta description (`og:description`) is generic boilerplate — not useful for proposals
- User-Agent header required (blocks default curl UA)

## Error handling

- **Python script returns non-zero exit code or empty stdout**: report the stderr output and stop. Do NOT update the state file.
- **Python script outputs invalid JSON**: report what was returned and stop. Do NOT update the state file. Suggest user check the script with `python3 /home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_onlinejobs.py --limit 3` directly.
- **google_sheets read fails (Step 3)**: report and stop. Suggest user check sheet permissions and service account access.
- **google_sheets append fails (Step 5)**: report error AND dump the candidate JSON array (including generated Subject/Message and any placeholders) so data can be recovered manually. Do NOT update the state file.

## Reviewing proposals with placeholders

When the user reviews the sheet, they should look for bold-bracketed placeholders in the Message column:
- `**[📹 VIDEO REQUIRED: ...]**` — User must record and attach a video introduction
- `**[📎 ATTACH: ...]**` — User must attach files or portfolio links
- `**[✏️ FILL IN: ...]**` — User must write a custom answer to a specific question
- `**[📄 ATTACH: Resume/CV]**` — User must attach their resume
- `**[📋 TEST TASK: ...]**` — User must review and complete a test assignment
- `**[PLACEHOLDER: YOUR RATE]**` — User must insert their desired hourly/monthly rate
- `**[🔗 APPLY VIA FORM: ...]**` — User must apply through an external form/link (not OnlineJobs)

### Special requirement patterns to watch for:
- **"Start your message with [word]"** → Message must literally start with that word
- **"Include [word] in your subject/title"** → Subject must contain that exact word
- **"Write [phrase] at the top"** → Message starts with that exact phrase
- **"OnlineJobs submissions will not be considered"** → External form required, flag with **[🔗 APPLY VIA FORM]**
- **Deleted job posts** → Subject: "N/A - Job Post Deleted", Message: note about deletion

If a job listing has strict requirements that cannot be auto-generated (e.g., "answer these 5 questions"), the message should still address what it can and flag the rest. The user can then edit the message in the sheet before sending.

## Query Filtering (User Preference)

**Always discard GoHighLevel / GHL listings.** After scraping (Step 2) and before dedup (Step 3), filter out any job whose title, description, or skills contain "GoHighLevel", "GHL", or "Go High Level" (case-insensitive). GHL is a tool the user can handle but does not want to be the primary focus of job matches. This filter applies to both OnlineJobs.ph and Upwork results. Log the count of discarded GHL jobs in the summary.

**Always discard US-only / US-based restricted listings.** The `firecrawl_scrape` JSON extraction returns a `location_restriction` field directly from the Upwork search results page. Filter out any job where `location_restriction` contains "U.S.", "United States", or "US". Also filter jobs where `location_restriction` contains "in-office" or "no remote". Justin is Philippines-based and cannot take US-restricted or in-office roles. Log the count of discarded jobs in the summary.

## Common Pitfalls

1. **Upwork `location_restriction` from search pages is unreliable.** The search results page only shows location restrictions for SOME jobs — many US-only jobs show no restriction on the search page. The actual "Only freelancers located in the U.S. may apply" banner only appears on the individual job page. Do NOT trust empty `location_restriction` from search results as "no restriction." This is why Upwork was dropped from automated scraping.

2. **Upwork Cloudflare blocks return 403 with stale cached data.** When `firecrawl_scrape` returns 403 on an Upwork job page, the JSON extraction may return data from a DIFFERENT job (cached from a previous scrape). Always verify the `job_title` in the response matches the URL you scraped. If they don't match, the data is stale — discard it.

3. **Upwork URL HTML artifacts.** Firecrawl scrapes include `span-class-highlight-` artifacts in URLs from Upwork's search highlight markup. Clean these with regex before dedup or storage: `re.sub(r'span-class-highlight-', '', url)` and `re.sub(r'span-', '', url)`.

4. **Generic proposals.** Every proposal must reference specific portfolio projects or DXC experience with metrics. No filler like "I am a hard worker."

5. **Overlong proposals.** User explicitly prefers short, direct proposals (120-150 words). Hit the job's specific requirements, reference one real project with a metric, and close. No corporate fluff, no "I'm excited to apply," no walls of text.

6. **Fabricating experience.** Never make up projects or skills not in the portfolio/resume. Flag gaps honestly.

7. **Google Sheets MCP doubling bug.** Tools with `sheet` + `range` double the sheet name. For reads, use `find_in_spreadsheet`. For writes, pass range WITHOUT sheet prefix (e.g. `A20:K24` not `jobs!A20:K24`).

8. **Broken pipe on large writes.** Keep batch writes to 5 rows max per `update_cells` call. Retry once on failure.

9. **`add_rows` corrupts data.** Never use `add_rows` — it inserts empty rows at the top. Always find the last occupied row and write directly with `update_cells`.

## Constraints

- Maximum 30 new rows per run per source (60 total)
- Never modify or delete existing rows
- Never modify the header row (row 1)
- Never overwrite existing proposals (columns I/J) — always check first
- Worksheet tab is named `jobs`
- Column K = Source ("OnlineJobs.ph" or "Upwork") — always set this
- All timestamps use Asia/Manila timezone (+08:00)
- Use the salary text verbatim from the script output, even if it looks odd (e.g., bare numbers like "6") — that's how OnlineJobs.ph displays them
- Keep summary concise — this runs unattended via cron
- Zero Firecrawl credits should be consumed by this skill
- Each proposal must be unique and tailored to the specific job — no copy-paste across listings
- When the user explicitly says "re-run proposals" or "update proposals," the "never overwrite" safeguard is suspended — overwrite existing Subject/Message for Status="New" rows. The user's explicit instruction takes precedence.

## Sheet Reorganization

When the jobs sheet accumulates too many non-"New" rows, reorganize by status:
- **Applied** → move to `Applied` sheet
- **Discarded + Closed** → move to `Discarded-Closed` sheet
- **New** → keep in `jobs` sheet

Full procedure: `references/sheet-reorganization.md`

## Reference files
- `references/justin-portfolio.md` — real project portfolio (NEVER fabricate)
- `references/justin-resume.md` — resume for certs, experience, education
- `references/sheet-reorganization.md` — moving rows between sheets by status
- `references/upwork-lessons-learned.md` — Why Upwork was dropped from automated scraping, location restriction detection failures, manual link approach, credit costs
- `references/upwork-scraping-approach.md` — Upwork Cloudflare bypass, Firecrawl agent config, API key location
- `references/onlinejobs-site-structure.md` — site structure notes
- `references/batch-proposal-backfill.md` — pattern for backfilling proposals on existing rows, including how to fetch full descriptions and handle deleted jobs
- `references/upwork-scraping.md` — Upwork-specific notes: Cloudflare workarounds, OAuth API alternative, data cleaning, differences vs OnlineJobs.ph