# Firecrawl MCP Tools Reference

Quick reference for all Firecrawl MCP tools available for web scraping and data gathering tasks.

---

## 1. firecrawl_search

Search the web and optionally extract content from search results. This is the **default starting point** for most research tasks.

**Best for:** Finding information across multiple sites when you don't know which site has it.

**Arguments:**
- `query` (required) — Search query. Supports operators: `""`, `-`, `site:`, `inurl:`, `intitle:`, `related:`
- `limit` — Max results (default 5)
- `sources` — Array of objects: `[{"type": "web"}, {"type": "images"}, {"type": "news"}]`
- `includeDomains` / `excludeDomains` — Restrict or exclude domains
- `scrapeOptions` — To also scrape each result: `{"formats": ["markdown"], "onlyMainContent": true}`
- `tbs` — Time-based search filter
- `lang` / `country` — Locale settings

**Returns:** JSON with `data.web[]` (or `data.images[]`, `data.news[]`), each with `url`, `title`, `description`.

**Workflow tip:** Search first without scrapeOptions for speed. Then scrape the relevant URLs individually.

---

## 2. firecrawl_scrape

Scrape a **single URL** with advanced options. The most powerful and reliable scraper — use this as default for any single-page extraction.

**Best for:** Extracting content from a known page URL.

**Arguments:**
- `url` (required) — The URL to scrape
- `formats` — Array of: `markdown`, `html`, `rawHtml`, `screenshot`, `links`, `summary`, `json`, `query`, `audio`, `branding`, `changeTracking`
- `onlyMainContent` — Boolean, strips nav/footer/sidebar noise
- `jsonOptions` — For JSON format: `{"prompt": "...", "schema": {...}}`
- `queryOptions` — For query format: `{"prompt": "...", "mode": "directQuote"|"freeform"}`
- `waitFor` — Milliseconds to wait for JS rendering (use 5000-10000 for SPAs)
- `actions` — Array of browser actions (wait, click, scroll, screenshot, etc.)
- `mobile` — Boolean, simulate mobile viewport
- `proxy` — `"basic"`, `"stealth"`, `"enhanced"`, `"auto"`
- `maxAge` — Use cached data (ms) for faster scrapes
- `parsers` — `["pdf"]` for PDF content
- `pdfOptions` — `{"maxPages": N}` for long PDFs

**Format selection rules:**
- Use `markdown` when you need to read/summarize full page content
- Use `json` with a schema when you need **specific data points** (prices, names, specs)
- Use `query` for a quick targeted answer from a long page

**JS-heavy page troubleshooting (in order):**
1. Add `waitFor: 5000` to `waitFor: 10000`
2. Try a different URL (check for hash fragments)
3. Use `firecrawl_map` with `search` to find the correct page
4. Use `firecrawl_agent` as last resort

---

## 3. firecrawl_crawl

Crawl a website and extract content from **multiple pages**. Returns an operation ID for async status checking.

**Best for:** Comprehensive coverage of a site section (blog posts, docs, product listings).

**Arguments:**
- `url` (required) — Starting URL (supports `/*` wildcards for path matching)
- `maxDiscoveryDepth` — How many link-hops to follow
- `limit` — Max pages to crawl
- `includePaths` / `excludePaths` — Path patterns to include/exclude
- `allowExternalLinks` — Boolean
- `deduplicateSimilarURLs` — Boolean
- `sitemap` — `"skip"`, `"include"`, or `"only"`
- `delay` — Delay between requests (ms)
- `maxConcurrency` — Parallel request limit
- `scrapeOptions` — Same format options as `firecrawl_scrape`
- `webhook` — URL to POST results to on completion

**Returns:** Operation ID. Use `firecrawl_check_crawl_status` to poll for results.

**Warning:** Crawls can return very large responses. Keep `limit` and `maxDiscoveryDepth` low to avoid token overflow. For large sites, prefer `map` + batch `scrape`.

---

## 4. firecrawl_check_crawl_status

Check the status and progress of a crawl job.

**Arguments:**
- `id` (required) — The operation ID from `firecrawl_crawl`

**Returns:** Status (`processing`, `completed`, `failed`), progress, and results if available.

---

## 5. firecrawl_map

Discover all indexed URLs on a website. **Use this before scraping** when you don't know the exact page URL.

**Best for:** Site exploration, finding specific content/pages, validating link structure.

**Arguments:**
- `url` (required) — The site URL
- `search` — Filter results by keyword (use this to find specific pages!)
- `limit` — Max URLs to return
- `includeSubdomains` — Boolean
- `ignoreQueryParameters` — Boolean
- `sitemap` — `"include"`, `"skip"`, or `"only"`

**Returns:** Array of URLs found on the site.

**Key pattern:** If `scrape` returns empty content, use `map` with `search` to find the right page first, then scrape that specific URL.

---

## 6. firecrawl_extract

Extract **structured information** from web pages using LLM-powered extraction.

**Best for:** Pulling specific fields (prices, names, specs, lists) from one or more known pages.

**Arguments:**
- `urls` (required) — Array of URLs to extract from
- `prompt` — Custom prompt for the LLM
- `schema` — JSON schema defining the output structure
- `allowExternalLinks` — Boolean
- `enableWebSearch` — Boolean (adds web context)
- `includeSubdomains` — Boolean

**Example:**
```json
{
  "urls": ["https://example.com/product"],
  "prompt": "Extract product name, price, and description",
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "price": {"type": "number"},
      "description": {"type": "string"}
    }
  }
}
```

---

## 7. firecrawl_parse

Parse a **local file** (PDF, HTML, DOCX, XLSX, etc.) and extract content. Fastest option for files on disk — no need to upload to the web.

**Best for:** Extracting content from local documents without hosting them publicly.

**Arguments:**
- `filePath` (required) — Absolute or relative path to the file
- `formats` — Same format options as `firecrawl_scrape`
- `jsonOptions` / `queryOptions` — For structured extraction
- `parsers` — `["pdf"]` for PDF files
- `pdfOptions` — `{"maxPages": N}` for long PDFs
- `onlyMainContent` — Boolean
- `includeTags` / `excludeTags` — HTML tag filters

**Supported types:** `.html`, `.htm`, `.xhtml`, `.pdf`, `.docx`, `.doc`, `.odt`, `.rtf`, `.xlsx`, `.xls`

**Unsupported:** `actions`, `screenshot`, `waitFor > 0`, `mobile`, non-basic/auto proxy

---

## 8. firecrawl_agent

Autonomous web research agent. It independently browses, searches, navigates, and extracts data based on a natural language prompt.

**Best for:** Complex research tasks where you don't know exact URLs; multi-source data gathering.

**Not recommended for:** Single-page extraction (use `scrape`), simple searches (use `search`).

**Arguments:**
- `prompt` (required) — Natural language description of what you need (max 10,000 chars)
- `urls` — Optional array of URLs to focus the agent on
- `schema` — Optional JSON schema for structured output

**Returns:** Job ID. Use `firecrawl_agent_status` to poll for results.

**Async workflow:**
1. Call `firecrawl_agent` → returns job ID immediately
2. Poll `firecrawl_agent_status` every 15-30 seconds
3. Keep polling for at least 2-3 minutes (complex tasks can take 5+)
4. Stop when status is `"completed"` or `"failed"`

---

## 9. firecrawl_agent_status

Check the status and retrieve results of an agent research job.

**Arguments:**
- `id` (required) — The job ID from `firecrawl_agent`

**Returns:** Status (`processing`, `completed`, `failed`), progress, and results.

---

## 10. firecrawl_interact

Interact with a previously scraped page in a live browser session — click buttons, fill forms, extract dynamic content, navigate deeper.

**Best for:** Multi-step workflows on a single page (search, click through results, fill forms).

**Requires:** A `scrapeId` from a previous `firecrawl_scrape` call.

**Arguments:**
- `scrapeId` (required) — The scrape ID from the metadata of a previous scrape response
- `prompt` — Natural language instruction (use this OR `code`)
- `code` — Code to execute: bash (agent-browser commands), Python, or Node
- `language` — `"bash"`, `"python"`, or `"node"` (default: `"node"`)
- `timeout` — Seconds (default 30, max 300)

**Common agent-browser commands (bash):**
- `agent-browser click @e5` — Click element by ref
- `agent-browser type @e3 "text"` — Type into element
- `agent-browser fill @e3 "text"` — Clear and fill
- `agent-browser get text @e1` — Get text content
- `agent-browser scroll down` — Scroll page
- `agent-browser snapshot` — Get accessibility tree

---

## 11. firecrawl_interact_stop

Stop an interact session to free resources.

**Arguments:**
- `scrapeId` (required) — The scrape ID to stop

---

## 12. firecrawl_search_feedback

Send feedback on a search result for quality improvement and credit refund.

**Arguments:**
- `searchId` (required) — The ID from `firecrawl_search` response
- `rating` (required) — `"good"`, `"partial"`, or `"bad"`
- `valuableSources` — Array of `{"url": "...", "reason": "..."}`
- `missingContent` — Array of `{"topic": "...", "description": "..."}`
- `querySuggestions` — How to improve

**When to call:** Right after processing search results. Must be within ~2 minutes.

**Requirement:** Substantive feedback only — at least one `valuableSources` or `missingContent` entry per rating.

---

## 13. firecrawl_browser_* (DEPRECATED)

The following browser tools are **deprecated** — use `firecrawl_scrape` + `firecrawl_interact` instead:
- `firecrawl_browser_create`
- `firecrawl_browser_delete`
- `firecrawl_browser_execute`
- `firecrawl_browser_list`

---

## Decision Flowchart

```
Need to find a page?
  → firecrawl_search (broad) or firecrawl_map (within a site)

Know the exact URL?
  → firecrawl_scrape (single page)

Need specific fields from a page?
  → firecrawl_scrape with json format + schema
  → firecrawl_extract (multiple URLs, LLM-powered)

Need to crawl an entire site section?
  → firecrawl_map to discover URLs, then batch scrape
  → firecrawl_crawl (if comprehensive coverage needed)

Complex research across unknown sources?
  → firecrawl_agent (autonomous, async)

Need to interact with a page (click, fill forms)?
  → firecrawl_scrape first, then firecrawl_interact

Parsing a local file?
  → firecrawl_parse
```

---

## Best Practices

1. **Search before scraping.** Use `search` or `map` to find the right URL before scraping.
2. **Prefer `markdown` for reading, `json` for extraction.** Don't use markdown when you need structured data.
3. **Keep crawls narrow.** Low `limit` + low `maxDiscoveryDepth` prevents token overflow.
4. **Use `onlyMainContent: true`** by default to strip navigation/footer noise.
5. **Add `waitFor` for SPAs.** 5000-10000ms for JavaScript-heavy pages.
6. **Use `maxAge`** for speed when fresh data isn't critical (500% faster).
7. **Send feedback** after searches to get credit refunds and improve results.
8. **Stop interact sessions** when done with `firecrawl_interact_stop`.
