# Enumerate All - API Test Framework

## 1. Core Philosophy

The fundamental principle of this framework is that the essence of AI search lies in the ability to **"Enumerate All"** possible results, rather than just fuzzy reasoning. A truly intelligent search system is not the "smartest" but the most "complete."

This framework is built on four pillars of API quality:

*   **Precision:** Use unique identifiers (e.g., package names, user IDs, PIDs) instead of ambiguous text searches.
*   **Completeness:** Be able to enumerate all results without omission, typically through full pagination.
*   **Verifiability:** Results must come from official, queryable APIs.
*   **Determinism:** The same query must always return the same complete set of results.

## 2. Project Overview

This project is a Python-based API testing framework designed to evaluate the "Enumerate All" capabilities of AI models across a wide range of domains. It provides a collection of "fetchers" for various public APIs, allowing for the generation of test cases that require complete and accurate enumeration of data.

## 3. Test Writing Best Practices

### 3.1 Including Metadata in Test Results

When writing tests, it is **CRITICAL** to include relevant metadata alongside the enumerated items. This metadata enriches the test cases and enables more sophisticated verification questions.

**Key Principles:**

1. **Always include metadata fields** that are available from the API response (downloads, likes, timestamps, ratings, etc.)
2. **Add ranking information** for ordered results (e.g., `rank: 1, 2, 3...`)
3. **Structure answers with both identifiers and metadata** instead of just listing IDs

**Example - Good Practice (Hugging Face):**

See `enumerate_framework/test_runners/test_huggingface_enhanced.py` for a reference implementation:

```python
# ✅ GOOD: Include metadata with each item
answer_with_metadata = [{
    'id': m['id'],
    'downloads': m.get('downloads', 0),
    'likes': m.get('likes', 0),
    'rank': idx + 1  # Add ranking for Top N queries
} for idx, m in enumerate(models)]

results.append(create_test_result(
    identifier="text_generation_top_downloads",
    question="列出下载量最高的100个text-generation模型",
    api_info=api_info,
    data=answer_with_metadata,  # Rich structured data
    data_key="models",
    filter="task=text-generation, sort=downloads(desc), limit=100"
))
```

**Anti-Pattern - Avoid:**

```python
# ❌ BAD: Only listing IDs without metadata
answer = [m['id'] for m in models]
```

**Benefits of Including Metadata:**

- Enables verification of sorting (e.g., "Are the results truly sorted by downloads?")
- Allows AI models to answer follow-up questions (e.g., "What's the download count of the 10th most popular model?")
- Provides context for understanding the enumeration (e.g., distinguishing between 1M and 100 downloads)
- Makes test results self-documenting and more valuable for analysis

### 3.2 Metadata Fields to Consider

Depending on the API domain, consider including:

- **Popularity metrics:** downloads, stars, likes, views, followers
- **Temporal data:** created_at, updated_at, published_date, last_modified
- **Quality indicators:** ratings, scores, verification status
- **Categorization:** tags, labels, types, genres, categories
- **Quantitative data:** size, duration, count, price
- **Ranking:** position in sorted results (especially for Top N queries)

## 4. API Catalog and Advanced Questions

This section summarizes the available APIs and proposes more complex, metadata-based questions, as inspired by the `dblp.py` fetcher.

### Code Ecosystem (10 APIs)

*   **NPM:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_by_maintainer`: Find all versions published by a specific user.
        *   `filter_by_dependency`: List all versions that have a specific dependency.
        *   `filter_prerelease_versions`: Identify all pre-release versions.
    *   **Advanced Questions (Feasible but Not Implemented):**
        *   "Find the version of package X with the most downloads."
            *   **Evidence:** The API endpoint `https://api.npmjs.org/versions/{package}/last-week` provides download counts for each version over the last 7 days.
*   **PyPI:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_prerelease_versions`: Identify all pre-release versions.
*   **Crates.io:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_prerelease_versions`: Identify all pre-release versions.
    *   **Advanced Questions (Partially Implemented):**
        *   The `downloads` count for each version is available in the metadata, but a specific function to find the single version with the most downloads is not implemented.
    *   **Advanced Questions (Feasible but Not Implemented):**
        *   "List all versions of package X that have a specific dependency."
            *   **Evidence:** This is possible by making a separate API call for each version to the `/api/v1/crates/{crate_name}/{version}/dependencies` endpoint.
*   **RubyGems:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_prerelease_versions`: Identify all pre-release versions (using the `prerelease` boolean flag from the API).
    *   **Advanced Questions (Feasible but Not Implemented):**
        *   "Find the version of package X with the most downloads."
            *   **Evidence:** This is possible by making a separate API call for each version to the `/api/v1/downloads/{gem_name}-{version}.json` endpoint.
*   **NuGet:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_prerelease_versions`: Identify all pre-release versions.
    *   **Advanced Questions (Partially Implemented):**
        *   The `authors` field is available in the metadata for each version, but a specific filter function (`filter_by_author`) is not implemented.
    *   **Advanced Questions (Feasible but Not Implemented):**
        *   "List all versions of package X that have a specific dependency."
            *   **Evidence:** The `dependencyGroups` field is available for each version in the V3 registration endpoint, so a local filter could be implemented.
*   **Go Proxy:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_prerelease_versions`: Identify all pre-release versions.
    *   **Advanced Questions (Feasible but Not Implemented):**
        *   "List all versions of package X that have a specific dependency."
            *   **Evidence:** This is possible by making a separate API call for each version to the `/@v/{version}.mod` endpoint to retrieve and parse the go.mod file.
    *   **Advanced Questions (Not Applicable / Not Supported):**
        *   The Go Proxy protocol does not have a concept of package "owners".
        *   The default proxy (`proxy.golang.org`) does not provide an API for download counts.
*   **Conda:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_prerelease_versions`: Identify all pre-release versions.
    *   **Advanced Questions (Partially Implemented):**
        *   The `total_downloads` count for each version is available in the metadata, but a specific function to find the single version with the most downloads is not implemented.
*   **CRAN:** Enumerate all versions of a package.
    *   **Advanced Questions (Implemented):**
        *   `filter_prerelease_versions`: Identify all pre-release versions.
    *   **Advanced Questions (Partially Implemented):**
        *   The `maintainer` is available in the metadata for each version, but a specific filter function (`filter_by_maintainer`) is not implemented.
    *   **Advanced Questions (Feasible but Not Implemented):**
        *   "List all versions of package X that have a specific dependency."
            *   **Evidence:** The `crandb` API response for each version includes dependency fields (`Depends`, `Imports`), so a local filter could be implemented.
*   **GitHub:** Enumerate repositories, tags, releases, and branches.
    *   **Advanced Questions (Implemented):**
        *   `filter_by_fork_status`: List all repositories for user X that are forks.
        *   `filter_prerelease`: Find all releases for repository Y that are marked as pre-release.
        *   `filter_stale_branches`: List all branches in repository Y that have not been updated in the last year.
        *   `get_most_starred_repo`: Find the repository owned by user X with the most stars.
        *   `filter_by_stars`, `filter_by_language`, `filter_by_created_date`: Additional filtering capabilities.
 
*   **Homebrew:** Enumerate the current version and variations of a formula.
    *   **Advanced Questions (Implemented):**
        *   `get_service_info`: List all available services for the 'postgresql' formula.
        *   `get_keg_only_reason`: Check if the 'python' formula is keg-only and why.
        *   `get_aliases`: List all aliases for the 'openssl@3' formula.
        *   `filter_deprecated`: Filter deprecated formulae.

### Academic/Research (1 API)

*   **DBLP:** Enumerate all publications for an author using their PID.
    *   **Existing Advanced Questions:**
        *   Filter publications by author position (first, last, etc.).
        *   Filter by venue (conference/journal).
        *   Filter by year range.
        *   Filter by publication type.

### Media/Entertainment (3 APIs)

*   **Spotify:** Enumerate all albums for an artist and all tracks for an album.
    *   **Advanced Questions (Implemented):**
        *   `filter_collaboration_albums`: List all albums by artist X that are collaborations.
        *   `filter_explicit_tracks`: Find all tracks on album Y that are explicit.
        *   `filter_albums_by_year`: List all albums by artist X that were released before a specific year.
        *   `filter_albums_by_type`: Filter albums by type (album/single/compilation).
        *   `filter_tracks_by_duration`: Filter tracks by duration (min/max milliseconds).
*   **YouTube:** Enumerate all videos and playlists for a channel.
    *   **Advanced Questions (Implemented):**
        *   `filter_videos_by_duration`: List all videos in channel X that are longer than 1 hour.
        *   `get_most_viewed_video`: Find the most viewed video in a channel/playlist.
        *   `filter_videos_by_views`: Filter videos by view count (min/max views).
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all live streams from channel X."
*   **TMDb:** Enumerate all works for an actor/director, all seasons for a series, etc.
    *   **Advanced Questions (Implemented):**
        *   `filter_person_credits_by_role`: List all movies where actor X also served as a producer.
        *   `filter_episodes_with_guest_stars`: Find all episodes of TV series Y from season 3 that have a guest star.
        *   `filter_person_credits_by_genre`: List all movies directed by director Z that are in the 'Science Fiction' genre.

### Business/Finance (1 API)

*   **SEC EDGAR:** Enumerate all filings for a company.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all 8-K filings for company X that relate to a change in executive officers."
        *   "Find the 10-K filing for company Y for the year 2022."
        *   "List all filings for company Z that were submitted by a specific individual."

### Infrastructure/Security (1 API)

*   **crt.sh:** Enumerate all SSL/TLS certificates and subdomains for a domain.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all expired certificates for the domain 'google.com'."
        *   "Find all certificates for 'github.com' that were issued by 'Let's Encrypt'."
        *   "List all subdomains of 'example.com' that have a wildcard certificate."

### Geolocation/Maps (1 API)

*   **OpenStreetMap:** Enumerate map features (nodes, ways, relations) within a bounding box.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "Find all hospitals within a 5km radius of a given coordinate."
        *   "List all public parks in a specific city that have a playground."
        *   "Enumerate all subway stations in a city and list their connecting lines."

### Government & Open Data (1 API)

*   **Data.gov:** Enumerate all datasets from a specific organization.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all datasets from the 'NASA' organization related to 'Mars'."
        *   "Find all CSV datasets related to 'air quality' updated in the last month."
        *   "Enumerate all datasets from the 'Department of Commerce' that are available in GeoJSON format."

### Weather & Climate (1 API)

*   **Open-Meteo:** Enumerate weather data for any location globally with TRUE "Enumerate All" capability.
    *   **Key Features:**
        *   NO API key required - completely free and open
        *   Historical data: 1940-present (80+ years of complete data)
        *   Weather forecast: 16 days
        *   NO rate limits for reasonable use
        *   Global coverage with precise lat/lon coordinates
    *   **Advanced Questions (Implemented):**
        *   **Basic Enumeration:**
            *   `filter_by_precipitation`: Enumerate all rainy days in Tokyo from 2020-2024 (5 years of complete data).
            *   `filter_by_temperature`: Filter by temperature range with multiple fields (max/min/mean).
            *   `filter_by_wind_speed`: Filter by wind speed thresholds.
            *   `filter_by_season`: Filter by season (spring/summer/autumn/winter).
            *   `find_rain_free_windows`: Find all continuous 7+ day rain-free windows in Tokyo for 2024.
        *   **Historical Extremes (80+ years):**
            *   `get_top_n_by_temperature` (n=10): Find the 10 hottest days ever recorded in Tokyo from 1940-2024.
            *   `get_top_n_by_temperature` (n=100): Enumerate the 100 hottest days in history - demonstrates TRUE "Enumerate All" capability.
        *   **Climate Change Analysis:**
            *   `compare_period_temperatures`: Compare Tokyo summer temperatures between 1940-1970 vs 1990-2024 to detect climate warming.
            *   Cross-decade temperature trend analysis with statistical significance.
        *   **Complex Time Windows:**
            *   `find_longest_heatwave`: Find the longest continuous heatwave (>30°C) in Tokyo's 80-year history.
            *   Sophisticated consecutive-day pattern detection over decades of data.
    *   **Advantages over OpenWeatherMap:**
        *   TRUE completeness: 80+ years vs 5 days
        *   NO authentication: None vs API key required
        *   NO rate limits: Unlimited vs 1000 calls/day
        *   Climate change analysis possible: Yes vs No
        *   Historical extremes possible: Yes vs No
        *   Perfectly aligned with "Enumerate All" philosophy

### AI & Machine Learning (1 API)

*   **Hugging Face Hub:** Enumerate public machine learning models, datasets, and Spaces.
    *   **Advanced Questions (Implemented):**
        *   `filter_by_task` + `filter_by_tag` + `filter_by_downloads`: List all text-generation models that support Chinese and have more than 100,000 downloads.
        *   `filter_by_tag` + `filter_by_license`: Find all datasets tagged with 'medical imaging' that are licensed under Apache 2.0.
        *   `filter_by_library` + `filter_by_task` + `filter_by_update_time`: Enumerate all PyTorch-based image segmentation models that have been updated in the last month.
        *   `filter_by_likes`: Filter resources by minimum likes count.
        *   Additional filtering capabilities for comprehensive metadata-based queries.
    *   **Test Implementation:** See `enumerate_framework/test_runners/ai_ml/test_huggingface.py` for a reference implementation of metadata-rich test results (includes both basic and enhanced tests).

## 5. Unimplemented APIs

For a list of APIs that are mentioned in the project documentation but do not have a corresponding fetcher and/or test runner implementation, please see [UNIMPLEMENTED_APIS.md](UNIMPLEMENTED_APIS.md).


## 7. API Authentication

To assist with testing, the APIs listed above can be grouped by their authentication requirements. Note that some APIs may have stricter rate limits for unauthenticated requests.

### APIs Typically Not Requiring an API Key

*   **Code Ecosystem:** PyPI, Crates.io, RubyGems, NuGet, Go Proxy, Conda, CRAN
*   **Academic/Research:** DBLP
*   **Business/Finance:** SEC EDGAR
*   **Infrastructure/Security:** crt.sh
*   **Geolocation/Maps:** OpenStreetMap
*   **Government & Open Data:** Data.gov
*   **Weather & Climate:** Open-Meteo

### APIs Requiring an API Key or OAuth

*   **Code Ecosystem:** GitHub, Homebrew (key recommended for full access)
*   **Academic/Research:** PubMed, Zenodo (see `GEMINI_SECONDARY_APIS.md`)
*   **Media/Entertainment:** Spotify, YouTube, TMDb

## 8. How to Use

### Running Tests

*   **APIs without Authentication:**
    ```bash
    cd enumerate_framework
    python test_all_apis_v2.py
    ```
*   **APIs with Authentication:**
    1.  `cp .env.example .env`
    2.  Edit `.env` with your API keys.
    3.  `python test_with_api_keys_v2.py`

### Generating a Complete Test Set

```bash
cd enumerate_framework
python main.py
```
This will generate `output/test_cases.json`.

### Viewing Statistics

```bash
cd enumerate_framework
python stats.py
```
