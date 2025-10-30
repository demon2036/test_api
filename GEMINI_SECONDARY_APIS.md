# Secondary Academic APIs

These API test runners are implemented but considered secondary to the core scenarios highlighted in `GEMINI.md`.

## PubMed

- **Purpose:** Enumerate all publications for an author (preferably via ORCID).
- **Advanced Questions (Implemented):**
  - `filter_by_author_role`: List all publications by author X where they are the corresponding author.
  - `filter_by_article_type`: Find all publications by author X that are review articles.
  - `filter_by_journal`: List all publications by author X that were published in the 'Nature' journal.
  - `filter_by_year`: Filter publications by year range.

## Zenodo

- **Purpose:** Enumerate all research data for a researcher (via ORCID).
- **Advanced Questions (Implemented):**
  - `filter_by_size`: List all datasets by researcher X that are over 1GB in size.
  - `filter_by_resource_type`: Find all software publications by researcher X.
  - `filter_by_license`: List all publications by researcher X that have a Creative Commons license.
  - `filter_by_year`: Filter records by year range.
