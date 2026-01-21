# scraper-core is a minimal, AI-first web scraping prototype for isolating and validating core data-ingestion logic before integration into a larger scraping system.

This repo is a reference implementation for:
	•	Fetching data from non-API-first websites
	•	Parsing and normalizing HTML into AI-ready schemas
	•	Designing scraper components that are reusable across frameworks such as Scrapy, Playwright, Selenium, etc.

Prioritizes clarity, separation of concerns, and extensibility over scale.

Basic Dev Principles:
	•	Thin entry point, strong internals
The CLI coordinates execution; logic lives in focused modules.
	•	Strict separation of concerns
Fetching, parsing, normalization, and storage are fully decoupled.
	•	AI-oriented data modeling
Data is normalized early into consistent, model-friendly structures.
	•	Hostile-web aware
Assumes APIs may not exist and that sites may require browser automation,
custom headers, or anti-bot mitigation.

This project is NOT a crawler framework, and the pipeline is purposefully linear and explicit.

Execution:
	1.	Fetch
Retrieves HTML via HTTP or Playwright.
	2.	Parse
Extracts raw data from the HTML.
	3.	Normalize
Converts raw rows into a consistent schema.
	4.	Store
Persists normalized records.

Intended to make debugging, testing, iteration, and reuse as easy and straightforward as possible.
