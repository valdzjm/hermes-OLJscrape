     1|---
     2|name: onlinejobs-scraper
     3|description: >
     4|  Scrape AI Automation Jobs from OnlineJobs.ph using a local Python script
     5|  (zero API cost), generate personalized proposals for each listing, and
     6|  append everything to the Hermes Scraper Google Sheet. Also supports manual
     7|  Upwork job links provided by the user. Triggers when the user says "run
     8|  the job scraper", "scrape onlinejobs", "find new AI jobs", or is invoked
     9|  by the scheduled cron job.
    10|tags: [scraping, jobs, automation, proposals, requirements-scanning, upwork]
    11|---
    12|
    13|# Job Scraper + Proposal Generator (OnlineJobs.ph + Upwork)
    14|
    15|You are running an automated job scraper and proposal generator. Follow these steps **exactly and in order**. Do not skip steps. Do not improvise.
    16|
    17|This skill scrapes from **OnlineJobs.ph** via a local Python script (zero API cost). **Upwork** is not included in the automated scrape — the user can provide individual Upwork job URLs for manual processing.
    18|
    19|For each scraped job, you also generate a personalized proposal (Subject + Message) tailored to the user's profile as an AI Automation Specialist.
    20|
    21|## User Profile (for proposal generation)
    22|
    23|- **Name**: Justin Mark Valdez
    24|- **Role**: AI Automation Specialist | Cloud & Infrastructure Engineer
    25|- **Location**: [YOUR_LOCATION]
    26|- **Experience**: 4+ years cloud/infrastructure, 1+ year freelance AI automation (since April 2025)
    27|- **Previous role**: System Administrator / Change Analyst at DXC Technology (Sept 2022 – March 2026) — managed Windows Server environments, ITIL/ITSM change management, ~20 server builds/month, CAB meetings, SOPs
    28|- **Core tools**: n8n, Make.com, Zapier, Claude Code, GoHighLevel, Airtable
    29|- **AI/LLM**: OpenAI, Claude, Gemini, Google Vertex AI, ElevenLabs, Vapi
    30|- **Cloud**: AWS (Solutions Architect Associate certified), Azure (AZ-104), GCP, Docker, Terraform, Ansible
    31|- **Databases**: PostgreSQL, MySQL, Redis, Supabase
    32|- **Scripting**: Python, Bash, PowerShell
    33|- **Certifications**: AWS Solutions Architect Associate, AWS Cloud Practitioner, Azure Admin (AZ-104), Azure Fundamentals (AZ-900), Oracle Cloud Foundations, ITIL 4 Foundation
    34|- **Education**: BS Electronics Engineering (TIP, 2022), BS Mechatronics Technology (TUTP, 2017)
    35|- **Portfolio**: jmvautomates.tech
    36|- **OnlineJobs.ph profile**: [YOUR_OJ_PROFILE_URL]
    37|- **Upwork**: upwork.com/freelancers/~01b70d87d89f9b7ae0
    38|- **LinkedIn**: linkedin.com/in/justinmarkvaldez
    39|
    40|### Project Reference (CRITICAL)
    41|
    42|**Before generating any proposal, load the project portfolio:**
    43|`skill_view(name='onlinejobs-scraper', file_path='references/your-portfolio.md')`
    44|
    45|**Resume reference (for certifications, experience, education):**
    46|`skill_view(name='onlinejobs-scraper', file_path='references/your-resume.md')`
    47|
    48|**NEVER fabricate project details, client names, metrics, or tools.** Only reference projects, tools, and outcomes that are documented in the portfolio. If a job asks for an example you don't have, use one of these strategies:
    49|1. Reference the closest real project from the portfolio
    50|2. Use honest phrasing: "I've built similar systems using..." and describe the actual tools/approach
    51|3. Add a placeholder: **[✏️ FILL IN: specific project example]**
    52|
    53|**Honesty rules for skill ratings:**
    54|- Never rate yourself 5/5 unless you could teach the tool
    55|- Vapi: 3/5 (used in AI Appointment Setter project, not deep custom)
    56|- ElevenLabs: 2-3/5 (limited experience)
    57|- Claude Code: 4/5 (daily development tool)
    58|- n8n: 4/5 (50+ production workflows, primary tool)
    59|- Make.com: 4/5 (Xero-Asana, Email Attachment projects)
    60|- Zapier: 4/5 (Content Repurposing, Lead Qualification, CRM projects)
    61|- GoHighLevel: 3-4/5 (used in client integrations)
    62|- REST APIs / Webhooks: 5/5 (foundation of every project)
    63|- AWS: 4/5 (Solutions Architect Certified, 4+ years infrastructure)
    64|- Azure: 4/5 (AZ-104 certified)
    65|- Python: 4/5 (primary scripting language)
    66|- PostgreSQL/Supabase: 4/5 (used in multiple projects)
    67|
    68|## Constants
    69|
    70|- **Search queries (OnlineJobs.ph)**: `n8n automation`, `Make.com automation`, `Zapier automation`, `automation specialist`, `AI automation`
    71|- **Scraper script (OnlineJobs.ph)**: `/home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_onlinejobs.py`
    72|- **Target Google Sheet ID**: `1oNdtp4iSTKus1cDUWcP1ZvbLJJeuQ6QjKQH0Rmuh81k`
    73|- **Worksheet name**: `jobs`
    74|- **Column layout (row 1 header — do NOT modify)**:
    75|  - A: Status
    76|  - B: Job URL
    77|  - C: Job Title
    78|  - D: Employment Type
    79|  - E: Date Posted
    80|  - F: Salary
    81|  - G: Description
    82|  - H: Skills Needed
    83|  - I: Subject
    84|  - J: Message
    85|  - K: Source (OnlineJobs.ph or Upwork)
    86|- **Append range**: `jobs!A:K`
    87|- **Dedup column**: B (Job URL)
    88|- **State file (OnlineJobs.ph)**: `/home/jmvadmin/.hermes/profiles/work-assistant/state/job-scraper-last-run.txt`
    89|- **Timezone**: Asia/Manila (UTC+8)
    90|- **Per-run cap**: 30 new jobs maximum (OnlineJobs.ph only)
    91|
    92|## Procedure
    93|
    94|### Step 1 — Read the last-run timestamp
    95|
    96|Use the terminal tool:
    97|
    98|```bash
    99|cat /home/jmvadmin/.hermes/profiles/work-assistant/state/job-scraper-last-run.txt
   100|```
   101|
   102|Store the trimmed result as `last_run_iso` (e.g., `2026-05-15T18:00:00+08:00`). If the file is empty or unreadable, default to `2020-01-01T00:00:00+08:00`.
   103|
   104|### Step 2 — Run the local Python scraper
   105|
   106|Use the terminal tool. Pass `last_run_iso` to the script's `--since` flag so it filters server-side and returns only listings newer than the last run. Cap at 30:
   107|
   108|```bash
   109|python3 /home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_onlinejobs.py --since "<last_run_iso>" --limit 30
   110|```
   111|
   112|Substitute `<last_run_iso>` with the value from Step 1.
   113|
   114|The script outputs a JSON array on stdout (progress messages go to stderr — ignore those). Parse stdout as JSON. Each object has these exact keys:
   115|
   116|- `url`
   117|- `job_title`
   118|- `employment_type`
   119|- `date_posted` (ISO-8601 with +08:00)
   120|- `salary`
   121|- `description`
   122|- `skills_needed`
   123|
   124|If the JSON array is empty, skip to Step 7 with the "no new jobs" summary and **do not update the state file**.
   125|
   126|### Step 2b — Manual Upwork link scraping (user-provided URLs only)
   127|
   128|Upwork is NOT included in the automated scrape. If the user provides a specific Upwork job URL, scrape it individually:
   129|
   130|1. Use `firecrawl_scrape` with JSON extraction on the job page
   131|2. Check `location_restriction` field — if it contains "U.S.", "United States", or similar, warn the user and skip
   132|3. If no restriction, generate a proposal and append to the sheet
   133|
   134|**Prompt for individual Upwork job scrape:**
   135|- `formats: ["json"]`
   136|- `jsonOptions.prompt`: "Extract job details: job title, employment type (hourly/fixed), budget/salary range, description (up to 500 chars), skills/tags, and any location restriction (e.g. 'Only freelancers located in the U.S. may apply'). Return location_restriction as 'None' if no restriction found."
   137|- `jsonOptions.schema`: `{"type": "object", "properties": {"job_title": {"type": "string"}, "employment_type": {"type": "string"}, "salary": {"type": "string"}, "description": {"type": "string"}, "skills_needed": {"type": "string"}, "location_restriction": {"type": "string"}}}`
   138|
   139|**If location_restriction contains US/United States:** Do NOT add to sheet. Tell the user: "This job is restricted to US-based freelancers."
   140|
   141|**If location_restriction is "None" or empty:** Generate proposal, dedup against sheet, append.
   142|
   143|No state file tracking for manual Upwork links.
   144|```
   145|https://www.upwork.com/jobs/span-class-highlight-Zapier-span-span-class-highlight-Make-com-span-Form-Setup_~022059486673153633521/
   146|```
   147|**Before running the normalizer**, you MUST:
   148|- **Clean URLs**: Strip `span-class-highlight-` and `-span` artifacts from URL slugs. Replace with the actual keyword text. Use a regex like `re.sub(r'span-class-highlight-|-span', '', url)`.
   149|- **Apply GHL filter**: Filter out jobs containing "GoHighLevel", "GHL", or "Go High Level" in title/description/skills BEFORE passing to the normalizer. The normalizer does NOT handle GHL filtering.
   150|- **Normalize relative dates**: Firecrawl returns dates like "1 hour ago", "yesterday", "3 days ago", "last week". Convert to ISO-8601 with +08:00 timezone before storing. The normalizer expects this but may not always handle it correctly — verify output.
   151|- **Use execute_code for all pre-processing** (URL cleaning + GHL filtering + date normalization) in a single Python script, then pass cleaned JSON to the normalizer OR skip the normalizer if your execute_code script already handles everything.
   152|
   153|4. Clean the data using the normalizer script:
   154|```bash
   155|echo '<firecrawl_json>' | python3 /home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_upwork.py
   156|```
   157|   The normalizer: removes HTML artifacts from titles, parses relative dates ("Posted yesterday" → ISO-8601), truncates descriptions to 500 chars, adds `"source": "Upwork"` to each job.
   158|
   159|5. Merge the cleaned Upwork jobs with the OnlineJobs.ph results from Step 2. Tag each OnlineJobs.ph job with `"source": "OnlineJobs.ph"`.
   160|
   161|6. If the Firecrawl agent fails or returns no results, log a warning and continue with OnlineJobs.ph results only.
   162|
   163|### Step 3 — Safety-net dedup against the sheet
   164|
   165|Use the **google_sheets** MCP to read column B (Job URL):
   166|
   167|- Spreadsheet ID: as in Constants
   168|- Range: `jobs!B2:B`
   169|
   170|Build a set of `existing_urls`. Drop any candidate from Step 2 whose `url` is already in this set.
   171|
   172|If zero candidates remain after dedup, skip to Step 7 with the "no new jobs" summary and **do not update the state file**.
   173|
   174|### Step 4 — Generate personalized proposals
   175|
   176|**SAFEGUARD: Only generate proposals for rows where BOTH conditions are true:**
   177|- Status is "New"
   178|- Columns I (Subject) AND J (Message) are BOTH empty
   179|
   180|**NEVER overwrite an existing proposal.** If a row already has a Subject or Message, skip it — even if the Status is "New". This protects against re-runs clobbering manually edited proposals.
   181|
   182|For each eligible job candidate, generate a **Subject** and **Message** using your understanding of the job details and the User Profile above.
   183|
   184|#### Subject rules:
   185|- Short and specific (under 60 characters before name suffix)
   186|- Reference the job title or key skill from the listing
   187|- **Always append** ` — Justin Mark Valdez` at the end of the subject UNLESS the job description specifies a required subject line (e.g., "Include [word] in your subject" or "Subject must be..."). When a required subject is specified, use it exactly as instructed without adding the name.
   188|- Examples:
   189|  - `"n8n Automation Expert for Your Workflow Needs — Justin Mark Valdez"`
   190|  - `"AI Automation Specialist — Make.com & Zapier — Justin Mark Valdez"`
   191|  - `"Your Next Automation Specialist is Here — Justin Mark Valdez"`
   192|
   193|#### Step 4a — Extract application requirements
   194|
   195|Before generating the proposal, scan the job `description` text for application requirements. Look for these keyword patterns (case-insensitive):
   196|
   197|- "How to Apply" / "How to apply" / "To Apply"
   198|- "Requirements" / "Application Requirements" / "Job Requirements"
   199|- "Must include" / "Please include" / "Should include"
   200|- "Video" / "Video introduction" / "Video resume" / "Loom"
   201|- "Portfolio" / "Sample work" / "Work samples"
   202|- "Answer" / "Answer the following" / "Answer these questions"
   203|- "Start your message with" / "Begin your application with" / "Start with the word"
   204|- "Test" / "Trial task" / "Paid test"
   205|- "Resume" / "CV" / "Cover letter"
   206|- "Rate" / "Expected salary" / "Hourly rate"
   207|
   208|If any requirements are found, extract them into a list called `requirements`.
   209|
   210|#### Step 4b — Generate personalized proposals
   211|
   212|For each remaining job candidate, generate a **Subject** and **Message** using your understanding of the job details, the User Profile above, and the extracted requirements from Step 4a.
   213|
   214|#### Subject rules:
   215|- Short and specific (under 60 characters before name suffix)
   216|- Reference the job title or key skill from the listing
   217|- **Always append** ` — Justin Mark Valdez` at the end of the subject UNLESS the job description specifies a required subject line (e.g., "Include [word] in your subject" or "Subject must be..."). When a required subject is specified, use it exactly as instructed without adding the name.
   218|- Examples:
   219|  - `"n8n Automation Expert for Your Workflow Needs — Justin Mark Valdez"`
   220|  - `"AI Automation Specialist — Make.com & Zapier — Justin Mark Valdez"`
   221|  - `"Your Next Automation Specialist is Here — Justin Mark Valdez"`
   222|
   223|#### Message rules:
   224|- **Opening**: Reference something specific from the job description (the company, the role, a specific task mentioned). Show you actually read the listing.
   225|- **Middle**: Briefly highlight relevant experience with the tools they need (n8n, Make.com, Zapier, GoHighLevel, Airtable, Claude Code). Mention 1-2 concrete outcomes (e.g., "built workflows that saved 20+ hours/week", "automated lead pipelines end-to-end").
   226|- **Requirements block**: If application requirements were found in Step 4a, add a section that addresses each one. For example:
   227|  - If they ask you to "start your message with a specific word" → include that word at the start of the message
   228|  - If they ask for your "hourly rate" or "expected salary" → include a rate or **[PLACEHOLDER: YOUR RATE]**
   229|  - If they ask for a "video introduction" or "Loom video" → add **[📹 VIDEO REQUIRED: Record a short video intro]**
   230|  - If they ask for "portfolio samples" → link jmvautomates.tech and add **[📎 ATTACH: Portfolio samples / case studies]**
   231|  - If they ask you to "answer specific questions" → answer what you can, and for anything requiring personal input, add **[✏️ FILL IN: <question they asked>]**
   232|  - If they ask for a "resume/CV" → add **[📄 ATTACH: Resume/CV]**
   233|  - If they ask for a "test task" → acknowledge willingness and add **[📋 TEST TASK: Review requirements and confirm]**
   234|  - If they say "start with [word]" → literally start the message with that exact word
   235|- **Close**: Express enthusiasm and include a call to action (e.g., "I'd love to discuss how I can help — let's chat!")
   236|- **Length**: 120-150 words MAX. Professional but conversational tone. Not robotic. User explicitly prefers short, direct proposals — hit the job's requirements, reference one real project with a metric, and close. No corporate fluff, no "I'm excited to apply," no walls of text. The shorter the better — long proposals get ignored.
   237|- **Do NOT** include greetings like "Dear Hiring Manager" — OnlineJobs.ph proposals are more direct. Upwork proposals can be slightly more formal.
   238|- **Do NOT** use generic filler like "I am a hard worker" or "I have 10 years of experience" unless it's backed by specifics.
   239|- **DO** tailor each message to the specific job. A Make.com job should emphasize Make.com; an n8n job should emphasize n8n.
   240|- **DO** use bold markers for placeholders so they stand out when reviewing: `**[PLACEHOLDER TEXT]**`
   241|- **DO** reference REAL projects from `references/your-portfolio.md` — never invent client names, metrics, or project details
   242|- **DO** use honest skill ratings based on the portfolio — never inflate
   243|- If the employer requires applying through an external form/link (not OnlineJobs), flag with `**[🔗 APPLY VIA FORM: ...]**`
   244|- If the job post has been deleted, set Subject to "N/A - Job Post Deleted" and Message to "This job post has been deleted and is no longer available on OnlineJobs.ph."
   245|
   246|#### Placeholder legend (for user review):
   247|When scanning completed proposals, look for these markers that need manual input:
   248|- `**[📹 VIDEO REQUIRED: ...]**` — Record and attach a video
   249|- `**[📎 ATTACH: ...]**` — Attach files/links
   250|- `**[✏️ FILL IN: ...]**` — Write a custom answer
   251|- `**[📄 ATTACH: Resume/CV]**` — Attach your resume
   252|- `**[📋 TEST TASK: ...]**` — Review and complete a test
   253|- `**[PLACEHOLDER: YOUR RATE]**` — Insert your rate
   254|- `**[🔗 APPLY VIA FORM: ...]**` — Apply through external form/link
   255|
   256|Store the generated Subject and Message alongside each job candidate for Step 5.
   257|
   258|### Step 5 — Append new rows to the Sheet
   259|
   260|**Do NOT use `add_rows`** — it inserts empty rows at the top and corrupts existing data. Instead, find the last occupied row by reading column B, then write directly to the next row.
   261|
   262|Use the **google_sheets** MCP:
   263|1. Read `jobs!B:B` to find the last non-empty row (e.g., row N)
   264|2. Use `update_cells` to write directly to `jobs!A(N+1):J(N+count)`
   265|
   266|- Spreadsheet ID: as in Constants
   267|- Values: one row per candidate, in this exact column order:
   268|
   269|```
   270|["New", url, job_title, employment_type, date_posted, salary, description, skills_needed, subject, message, source]
   271|```
   272|
   273|**Column order matters** — these must map to header columns A → K. Always set Status to "New" for newly appended rows. Set `source` to "OnlineJobs.ph" or "Upwork" based on where the job came from.
   274|
   275|**Pitfall:** If using `batch_update` API directly, text values must use `{"stringValue": "text"}` format, not bare strings.
   276|
   277|**Google Sheets MCP pitfall:** ALL tools with a `sheet` + `range` parameter double the sheet name (e.g., `get_sheet_data` produces `jobs!jobs!B:B`, `batch_update_cells` produces `jobs!jobs!A:J`). Workarounds:
   278|- **For reads (Step 3):** Use `find_in_spreadsheet` instead of `get_sheet_data` — it searches by value and returns cell locations without the doubling bug.
   279|- **For writes (Step 5):** Use `update_cells` and pass the range WITHOUT the sheet prefix (e.g., `A67:J69` instead of `jobs!A67:J69`). The `sheet` parameter already specifies the sheet.
   280|- **Broken pipe errors:** Common with large payloads (5+ rows). Keep batch writes to 5 rows max per call. Retry once — usually works on second attempt.
   281|
   282|### Step 6 — Update the state file
   283|
   284|Find the **newest** `date_posted` value from the rows you just appended. Write it via terminal:
   285|
   286|```bash
   287|echo "<newest_onlinejobs_iso>" > /home/jmvadmin/.hermes/profiles/work-assistant/state/job-scraper-last-run.txt
   288|```
   289|
   290|If no new jobs were added, or if Step 5 failed, **do NOT update** the state file.
   291|
   292|### Step 7 — Report summary
   293|
   294|Output a concise Telegram-friendly summary:
   295|
   296|```
   297|📋 Job scrape complete (OnlineJobs.ph)
   298|
   299|✅ N new jobs added (with proposals)
   300|🕐 Run time: <current Manila time>
   301|🔗 Sheet: https://docs.google.com/spreadsheets/d/1oNdtp4iSTKus1cDUWcP1ZvbLJJeuQ6QjKQH0Rmuh81k
   302|
   303|Top 3 new listings:
   304|1. <Title> — <Salary> | Subject: <Subject>
   305|2. <Title> — <Salary> | Subject: <Subject>
   306|3. <Title> — <Salary> | Subject: <Subject>
   307|```
   308|
   309|If no new jobs: a single line "No new AI automation jobs since last run."
   310|
   311|## Fallback: Fetching full job descriptions when Firecrawl is unavailable
   312|
   313|Both `firecrawl_scrape` and `web_extract` use Firecrawl credits — when credits are exhausted, BOTH fail. OnlineJobs.ph job pages can be scraped directly with curl since the content is server-rendered (no JS required).
   314|
   315|**Technique:** curl + Python HTMLParser to extract the `job-description` div. Simple regex fails because the div has nested children; use depth-tracking HTMLParser:
   316|
   317|```python
   318|from html.parser import HTMLParser
   319|import re
   320|
   321|class JobDescExtractor(HTMLParser):
   322|    def __init__(self):
   323|        super().__init__()
   324|        self.in_job_desc = False
   325|        self.depth = 0
   326|        self.text = []
   327|
   328|    def handle_starttag(self, tag, attrs):
   329|        attrs_dict = dict(attrs)
   330|        cls = attrs_dict.get('class', '')
   331|        if 'job-description' in cls:
   332|            self.in_job_desc = True
   333|            self.depth = 0
   334|        if self.in_job_desc:
   335|            self.depth += 1
   336|            if tag in ('br', 'p', 'div', 'li'):
   337|                self.text.append('\n')
   338|
   339|    def handle_endtag(self, tag):
   340|        if self.in_job_desc:
   341|            self.depth -= 1
   342|            if self.depth <= 0:
   343|                self.in_job_desc = False
   344|
   345|    def handle_data(self, data):
   346|        if self.in_job_desc:
   347|            self.text.append(data.strip())
   348|```
   349|
   350|Usage: `curl -sL -A "Mozilla/5.0 ..." "<url>" | python3 -c "<parser above>"` → clean text output.
   351|
   352|**OnlineJobs.ph HTML notes:**
   353|- Job description lives in `<div class="job-description">` inside `<div class="card job-post">`
   354|- Meta description (`og:description`) is generic boilerplate — not useful for proposals
   355|- User-Agent header required (blocks default curl UA)
   356|
   357|## Error handling
   358|
   359|- **Python script returns non-zero exit code or empty stdout**: report the stderr output and stop. Do NOT update the state file.
   360|- **Python script outputs invalid JSON**: report what was returned and stop. Do NOT update the state file. Suggest user check the script with `python3 /home/jmvadmin/.hermes/profiles/work-assistant/projects/Webscraping/scripts/scrape_onlinejobs.py --limit 3` directly.
   361|- **google_sheets read fails (Step 3)**: report and stop. Suggest user check sheet permissions and service account access.
   362|- **google_sheets append fails (Step 5)**: report error AND dump the candidate JSON array (including generated Subject/Message and any placeholders) so data can be recovered manually. Do NOT update the state file.
   363|
   364|## Reviewing proposals with placeholders
   365|
   366|When the user reviews the sheet, they should look for bold-bracketed placeholders in the Message column:
   367|- `**[📹 VIDEO REQUIRED: ...]**` — User must record and attach a video introduction
   368|- `**[📎 ATTACH: ...]**` — User must attach files or portfolio links
   369|- `**[✏️ FILL IN: ...]**` — User must write a custom answer to a specific question
   370|- `**[📄 ATTACH: Resume/CV]**` — User must attach their resume
   371|- `**[📋 TEST TASK: ...]**` — User must review and complete a test assignment
   372|- `**[PLACEHOLDER: YOUR RATE]**` — User must insert their desired hourly/monthly rate
   373|- `**[🔗 APPLY VIA FORM: ...]**` — User must apply through an external form/link (not OnlineJobs)
   374|
   375|### Special requirement patterns to watch for:
   376|- **"Start your message with [word]"** → Message must literally start with that word
   377|- **"Include [word] in your subject/title"** → Subject must contain that exact word
   378|- **"Write [phrase] at the top"** → Message starts with that exact phrase
   379|- **"OnlineJobs submissions will not be considered"** → External form required, flag with **[🔗 APPLY VIA FORM]**
   380|- **Deleted job posts** → Subject: "N/A - Job Post Deleted", Message: note about deletion
   381|
   382|If a job listing has strict requirements that cannot be auto-generated (e.g., "answer these 5 questions"), the message should still address what it can and flag the rest. The user can then edit the message in the sheet before sending.
   383|
   384|## Query Filtering (User Preference)
   385|
   386|**Always discard GoHighLevel / GHL listings.** After scraping (Step 2) and before dedup (Step 3), filter out any job whose title, description, or skills contain "GoHighLevel", "GHL", or "Go High Level" (case-insensitive). GHL is a tool the user can handle but does not want to be the primary focus of job matches. This filter applies to both OnlineJobs.ph and Upwork results. Log the count of discarded GHL jobs in the summary.
   387|
   388|**Always discard US-only / US-based restricted listings.** The `firecrawl_scrape` JSON extraction returns a `location_restriction` field directly from the Upwork search results page. Filter out any job where `location_restriction` contains "U.S.", "United States", or "US". Also filter jobs where `location_restriction` contains "in-office" or "no remote". Justin is Philippines-based and cannot take US-restricted or in-office roles. Log the count of discarded jobs in the summary.
   389|
   390|## Common Pitfalls
   391|
   392|1. **Upwork `location_restriction` from search pages is unreliable.** The search results page only shows location restrictions for SOME jobs — many US-only jobs show no restriction on the search page. The actual "Only freelancers located in the U.S. may apply" banner only appears on the individual job page. Do NOT trust empty `location_restriction` from search results as "no restriction." This is why Upwork was dropped from automated scraping.
   393|
   394|2. **Upwork Cloudflare blocks return 403 with stale cached data.** When `firecrawl_scrape` returns 403 on an Upwork job page, the JSON extraction may return data from a DIFFERENT job (cached from a previous scrape). Always verify the `job_title` in the response matches the URL you scraped. If they don't match, the data is stale — discard it.
   395|
   396|3. **Upwork URL HTML artifacts.** Firecrawl scrapes include `span-class-highlight-` artifacts in URLs from Upwork's search highlight markup. Clean these with regex before dedup or storage: `re.sub(r'span-class-highlight-', '', url)` and `re.sub(r'span-', '', url)`.
   397|
   398|4. **Generic proposals.** Every proposal must reference specific portfolio projects or DXC experience with metrics. No filler like "I am a hard worker."
   399|
   400|5. **Overlong proposals.** User explicitly prefers short, direct proposals (120-150 words). Hit the job's specific requirements, reference one real project with a metric, and close. No corporate fluff, no "I'm excited to apply," no walls of text.
   401|
   402|6. **Fabricating experience.** Never make up projects or skills not in the portfolio/resume. Flag gaps honestly.
   403|
   404|7. **Google Sheets MCP doubling bug.** Tools with `sheet` + `range` double the sheet name. For reads, use `find_in_spreadsheet`. For writes, pass range WITHOUT sheet prefix (e.g. `A20:K24` not `jobs!A20:K24`).
   405|
   406|8. **Broken pipe on large writes.** Keep batch writes to 5 rows max per `update_cells` call. Retry once on failure.
   407|
   408|9. **`add_rows` corrupts data.** Never use `add_rows` — it inserts empty rows at the top. Always find the last occupied row and write directly with `update_cells`.
   409|
   410|## Constraints
   411|
   412|- Maximum 30 new rows per run per source (60 total)
   413|- Never modify or delete existing rows
   414|- Never modify the header row (row 1)
   415|- Never overwrite existing proposals (columns I/J) — always check first
   416|- Worksheet tab is named `jobs`
   417|- Column K = Source ("OnlineJobs.ph" or "Upwork") — always set this
   418|- All timestamps use Asia/Manila timezone (+08:00)
   419|- Use the salary text verbatim from the script output, even if it looks odd (e.g., bare numbers like "6") — that's how OnlineJobs.ph displays them
   420|- Keep summary concise — this runs unattended via cron
   421|- Zero Firecrawl credits should be consumed by this skill
   422|- Each proposal must be unique and tailored to the specific job — no copy-paste across listings
   423|- When the user explicitly says "re-run proposals" or "update proposals," the "never overwrite" safeguard is suspended — overwrite existing Subject/Message for Status="New" rows. The user's explicit instruction takes precedence.
   424|
   425|## Sheet Reorganization
   426|
   427|When the jobs sheet accumulates too many non-"New" rows, reorganize by status:
   428|- **Applied** → move to `Applied` sheet
   429|- **Discarded + Closed** → move to `Discarded-Closed` sheet
   430|- **New** → keep in `jobs` sheet
   431|
   432|Full procedure: `references/sheet-reorganization.md`
   433|
   434|## Reference files
   435|- `references/your-portfolio.md` — real project portfolio (NEVER fabricate)
   436|- `references/your-resume.md` — resume for certs, experience, education
   437|- `references/sheet-reorganization.md` — moving rows between sheets by status
   438|- `references/upwork-lessons-learned.md` — Why Upwork was dropped from automated scraping, location restriction detection failures, manual link approach, credit costs
   439|- `references/upwork-scraping-approach.md` — Upwork Cloudflare bypass, Firecrawl agent config, API key location
   440|- `references/onlinejobs-site-structure.md` — site structure notes
   441|- `references/batch-proposal-backfill.md` — pattern for backfilling proposals on existing rows, including how to fetch full descriptions and handle deleted jobs
   442|- `references/upwork-scraping.md` — Upwork-specific notes: Cloudflare workarounds, OAuth API alternative, data cleaning, differences vs OnlineJobs.ph