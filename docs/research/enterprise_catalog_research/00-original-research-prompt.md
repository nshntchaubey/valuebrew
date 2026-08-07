# ValueBrew — Karnataka Beer Database Research & Acquisition Program

You are acting as the founding **Chief Data Officer**, **Lead Data Engineer**, **Data Architect**, **Research Team**, and **Catalog Acquisition Team** for a startup called **ValueBrew**.

This is **NOT** a coding task.

This is **NOT** a software architecture task.

This is a deep research, intelligence gathering, and master database acquisition project.

Your objective is to design **and begin building** the highest-quality **Karnataka beer master database**, with an architecture capable of expanding into the most authoritative beer database in India.

Accuracy is significantly more important than speed.

Do not optimize for "getting something working."

Optimize for building a long-term strategic data asset.

---

# Context

I have attached a document describing:

- Product vision
- Long-term data architecture
- Licensing decisions
- Rejected approaches
- Entity model
- Recommended acquisition strategy

Read the document completely before beginning.

Treat it as the governing document.

Do not contradict it unless you have strong evidence.

Whenever you disagree:

- explain why
- provide evidence
- cite sources

---

# Geographic Scope (Critical)

The first production release of ValueBrew is **Karnataka-only**.

This is a hard constraint.

Every recommendation, acquisition strategy, database design, and research decision should optimize for Karnataka first.

Beer prices in India are state-specific because excise policies differ across states.

Therefore:

- Treat Karnataka as the single source of truth for all legal MRP values.
- Prioritize Karnataka government sources above every other source.
- Prioritize Bangalore and Karnataka retailers.
- Prioritize breweries whose products are sold in Karnataka.
- Ignore products unavailable in Karnataka unless they are expected to launch there soon.
- Do not spend significant effort collecting prices from Maharashtra, Goa, Delhi, Telangana, Tamil Nadu, etc.

National information such as:

- GTIN
- Barcode
- Product descriptions
- Brewery information
- Images
- Alcohol %
- Calories

may be collected because those are generally state-independent.

Pricing must always be Karnataka-specific.

Design the database so expansion to every Indian state is straightforward, but populate only Karnataka pricing during this research project.

---

# IMPORTANT

Use Claude's **Parallel Agents** aggressively.

Do NOT perform this sequentially.

Spawn independent specialized research agents.

Each agent should independently research its assigned domain.

The final report should reconcile every agent's findings into one coherent strategy.

Think like the founding data team of a startup that expects to manage **50,000+ SKUs**, not a hobby spreadsheet.

---

# Agent 1 — Government Data Intelligence

Research every government source for Karnataka beer information.

Focus on:

- Karnataka State Beverages Corporation (KSBCL)
- Karnataka Excise Department
- Karnataka Government Open Data
- Public procurement portals
- Gazette notifications
- Price circulars
- Supplier lists
- PDFs
- Excel files
- CSV files
- APIs
- Historical archives

Deliver:

- URLs
- update frequency
- file formats
- completeness
- automation feasibility
- licensing
- reliability
- strengths
- weaknesses

---

# Agent 2 — Brewery Intelligence

Research every brewery operating in Karnataka and India whose products are sold in Karnataka.

Include (not limited to):

- United Breweries
- Kingfisher
- Heineken India
- AB InBev India
- Budweiser
- Corona
- Hoegaarden
- Carlsberg India
- Bira91
- Simba
- Geist
- Arbor
- Toit
- Murphy's
- STOK
- Goa Brewing
- local Karnataka breweries

For every brewery determine:

- official website
- official catalogue
- downloadable catalogues
- product pages
- images
- ABV
- calories
- package sizes
- GTIN
- UPC
- distributor catalogues
- retailer catalogues

---

# Agent 3 — Retail Intelligence

Research every Karnataka retailer exposing searchable beer catalogues.

Start with:

https://www.madhuloka.com/

Also research:

- Tonique
- Living Liquidz
- Spencer's
- Nature's Basket
- Metro Cash & Carry
- Liquor Mart
- Bangalore wine stores
- Karnataka liquor retailers
- premium alcohol retailers

Determine for every retailer:

- searchable catalogue
- structured HTML
- APIs
- JSON endpoints
- GraphQL
- search endpoints
- robots.txt
- anti scraping
- Cloudflare
- pagination
- update frequency
- beer coverage
- Karnataka coverage

Rank retailers by usefulness.

---

# Agent 4 — Barcode Intelligence

Research:

- GS1 India
- DataKart
- GTIN
- UPC
- barcode lookup APIs
- commercial APIs
- free APIs

Determine:

- coverage
- licensing
- pricing
- commercial usability
- API quality
- manufacturer participation
- limitations

---

# Agent 5 — Open Dataset Intelligence

Research:

- Open Food Facts
- Open Product Data
- Kaggle
- GitHub datasets
- public beer datasets
- grocery datasets
- Indian product datasets
- government datasets

Evaluate:

- coverage
- freshness
- licensing
- quality
- commercial usability

Specifically determine whether they contain Indian beer products.

---

# Agent 6 — Import & Market Discovery

Research:

- Volza
- Zauba
- Indian customs
- HSN 2203
- beer import databases

Determine whether import intelligence can automatically discover:

- new beers entering India
- imported brands
- upcoming launches

---

# Agent 7 — Web Scraping Engineer

Your responsibility is evaluating engineering feasibility.

Do NOT merely list websites.

Actually evaluate whether ValueBrew should scrape them.

For every identified source determine:

- robots.txt
- anti-bot protection
- Cloudflare
- JavaScript rendering
- hidden APIs
- GraphQL
- JSON endpoints
- Playwright suitability
- BeautifulSoup suitability
- Selenium suitability
- expected maintenance effort
- expected data quality

Estimate engineering effort.

---

# Agent 8 — Database Architect

Using every other agent's findings, design the production master database.

Include entities such as:

- Beer
- Brewery
- Brand
- Style
- SKU
- GTIN
- Barcode
- Karnataka Legal MRP
- Historical Karnataka MRP
- Alcohol %
- Calories
- Volume
- Package Type
- Image
- Availability
- Source Provenance
- Confidence Score
- Aliases
- Search Keywords
- Version History
- Audit Trail

Design:

- normalization
- entity resolution
- duplicate detection
- merge strategy
- provenance tracking
- confidence scoring
- update workflow

Think at the scale of 50,000+ SKUs.

---

# Agent 9 — Search Engineer

Design the search system.

Support:

- typing
- autocomplete
- fuzzy search
- typo tolerance
- phonetic search
- aliases
- abbreviations
- GTIN
- barcode
- brewery
- brand
- style
- package size

Examples:

KF

King Fisher

Kingfisher

KF Premium

Bud

Bira Blonde

650

500 ml

Hoegaarden White

Determine:

- indexing strategy
- ranking strategy
- synonym strategy
- alias strategy

---

# Agent 10 — Founder Execution Team

Ignore software.

Design the operational plan.

Answer:

How does one founder actually build Karnataka's most authoritative beer database?

Estimate:

- number of beers
- number of SKUs
- hours required
- manpower
- cost
- QA
- verification workflow
- daily throughput
- monthly throughput
- ongoing maintenance

Recommend:

- manual work
- semi-automated work
- fully automated work

Identify:

- partnerships
- outreach strategy
- manufacturer collaboration
- distributor collaboration

---

# Deliverables

I do NOT want only research notes.

Produce actual artifacts.

---

## Deliverable 1

Master Source Matrix

Include every discovered source.

Columns:

- Source
- URL
- Coverage
- Reliability
- Licensing
- Automation Difficulty
- Refresh Frequency
- Confidence
- Recommendation

---

## Deliverable 2

Catalog Acquisition Strategy

Exactly which sources should be used.

In what order.

Explain why.

---

## Deliverable 3

Production Database Schema

Production-grade.

Normalized.

Future-proof.

---

## Deliverable 4

Catalog Acquisition Playbook

An operational handbook.

Step-by-step.

Explain exactly how ValueBrew should acquire, verify, maintain and expand its catalog.

---

## Deliverable 5

Top Karnataka Breweries & Brands

List every major brewery and beer brand available in Karnataka.

Include:

- official website
- beer catalogue
- Karnataka availability
- confidence

---

## Deliverable 6

Initial Karnataka Beer Catalog

Build the largest possible verified Karnataka beer catalog.

Target:

**500–1,000 Karnataka beer SKUs.**

For every SKU collect as many verified fields as possible.

Include:

- Beer Name
- Brand
- Brewery
- Style
- ABV
- Calories
- Size
- Package Type
- Karnataka MRP
- GTIN
- Barcode
- Image URL
- Manufacturer URL
- Retail Source
- Government Source
- Confidence Score
- Last Verified Date

Never fabricate values.

If information cannot be verified, leave it blank.

---

## Deliverable 7

Automation Roadmap

Categorize every acquisition activity as:

- Manual
- Semi-Automated
- Fully Automated

Recommend engineering priorities.

---

## Deliverable 8

Risk Register

Include:

- Licensing risks
- Scraping risks
- Legal risks
- Government dependency
- GS1 limitations
- Retail dependency
- Maintenance risks

---

## Deliverable 9

Gap Analysis

Identify every important data field that still cannot be obtained reliably.

Recommend how each gap can eventually be closed.

---

# Success Targets

The objective is NOT simply to research sources.

The objective is to build the foundation of Karnataka's most authoritative beer database.

Target outcomes:

- 100% coverage of major beer brands sold in Karnataka.
- 95%+ coverage of packaged beer SKUs sold in Karnataka.
- Every SKU linked to at least one authoritative source.
- Every Karnataka MRP sourced from KSBCL or another authoritative Karnataka source wherever possible.
- Every barcode linked to its corresponding SKU whenever available.
- Every fact accompanied by provenance.
- Every uncertainty explicitly marked with a confidence score.

If multiple sources disagree:

Do NOT choose one arbitrarily.

Record every value with its provenance and confidence level.

---

# Research Rules

- Prefer primary sources over blogs.
- Never fabricate information.
- Every important claim must include citations.
- Separate verified facts from assumptions.
- Separate evidence from inference.
- Preserve provenance for every field.
- Clearly indicate confidence levels.
- Think like the founding data team of a startup building a strategic data asset, not someone compiling a spreadsheet.

---

# Final Success Criteria

When finished, I should have:

1. A production-grade strategy for building Karnataka's best beer database.
2. A ranked list of every viable data source.
3. A practical roadmap for acquiring 500–1,000 Karnataka beer SKUs.
4. A production-ready master database design.
5. A founder's operational playbook for scaling from Karnataka to every state in India.
6. The beginnings of a real, usable Karnataka beer catalog that can immediately seed the ValueBrew application.
```