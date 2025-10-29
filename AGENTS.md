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

### Code Ecosystem (11 APIs)

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
*   **Docker Hub:** Enumerate all tags for an image.
    *   **Advanced Questions (Implemented):**
        *   `filter_by_name_pattern`: List all tags for the 'python' image that are based on 'alpine'.
        *   `filter_by_architecture`: List all tags for the 'nginx' image that are for a specific architecture (e.g., 'arm64').
    *   **Advanced Questions (Partially Implemented):**
        *   Tags include last_updated timestamp, allowing for sorting to find the most recently pushed tag.
*   **Homebrew:** Enumerate the current version and variations of a formula.
    *   **Advanced Questions (Implemented):**
        *   `get_service_info`: List all available services for the 'postgresql' formula.
        *   `get_keg_only_reason`: Check if the 'python' formula is keg-only and why.
        *   `get_aliases`: List all aliases for the 'openssl@3' formula.
        *   `filter_deprecated`: Filter deprecated formulae.

### Academic/Research (3 APIs)

*   **DBLP:** Enumerate all publications for an author using their PID.
    *   **Existing Advanced Questions:**
        *   Filter publications by author position (first, last, etc.).
        *   Filter by venue (conference/journal).
        *   Filter by year range.
        *   Filter by publication type.
*   **PubMed:** Enumerate all publications for an author (preferably via ORCID).
    *   **Advanced Questions (Implemented):**
        *   `filter_by_author_role`: List all publications by author X where they are the corresponding author.
        *   `filter_by_article_type`: Find all publications by author X that are review articles.
        *   `filter_by_journal`: List all publications by author X that were published in the 'Nature' journal.
        *   `filter_by_year`: Filter publications by year range.
*   **Zenodo:** Enumerate all research data for a researcher (via ORCID).
    *   **Advanced Questions (Implemented):**
        *   `filter_by_size`: List all datasets by researcher X that are over 1GB in size.
        *   `filter_by_resource_type`: Find all software publications by researcher X.
        *   `filter_by_license`: List all publications by researcher X that have a Creative Commons license.
        *   `filter_by_year`: Filter records by year range.

### Media/Entertainment (4 APIs)

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

### Social Media (New Category - Not Yet Implemented)

*   **Twitter/X (Not Yet Implemented):** Enumerate tweets, followers, and lists for a user.
    *   **Advanced Questions:**
        *   "Find all tweets by user X that are retweets with comments."
        *   "List all followers of user Y who have more than 10,000 followers and are verified."
        *   "Enumerate all users on the 'OfficialAPIs' list owned by user 'TwitterDev'."
*   **Reddit (Not Yet Implemented):** Enumerate posts in a subreddit and comments on a post.
    *   **Advanced Questions:**
        *   "Find all posts in subreddit 'r/python' with a score higher than 1000."
        *   "List all comments by user 'spez' in a specific submission."
        *   "Enumerate all moderators of the 'r/programming' subreddit."
*   **Discord (Not Yet Implemented):** Enumerate servers (guilds), channels, and members.
    *   **Advanced Questions:**
        *   "List all users in channel 'general' of server X who have the 'Moderator' role."
        *   "Find all messages in server Y containing the phrase 'Gemini API' from the last 24 hours."
        *   "Enumerate all custom emojis available in server Z."

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

### Geolocation/Maps (New Category - Not Yet Implemented)

*   **OpenStreetMap (Not Yet Implemented):** Enumerate map features (nodes, ways, relations) within a bounding box.
    *   **Advanced Questions:**
        *   "Find all hospitals within a 5km radius of a given coordinate."
        *   "List all public parks in a specific city that have a playground."
        *   "Enumerate all subway stations in a city and list their connecting lines."

### Gaming (New Category - Not Yet Implemented)

*   **Steam (Not Yet Implemented):** Enumerate all games owned by a user, and all achievements for a game.
    *   **Advanced Questions:**
        *   "List all games owned by user X that they have not played yet."
        *   "Find the rarest achievement for the game 'Counter-Strike 2'."
        *   "Enumerate all friends of user Y who also own the game 'Baldur's Gate 3'."
*   **Twitch (Not Yet Implemented):** Enumerate all live streams for a specific game, and all followers of a channel.
    *   **Advanced Questions:**
        *   "Find all live streams of the game 'Elden Ring' with more than 1,000 viewers."
        *   "List all VIPs and moderators for channel X."
        *   "Enumerate all video clips from channel Y that have more than 10,000 views."

### Government & Open Data (New Category - Not Yet Implemented)

*   **Data.gov (Not Yet Implemented):** Enumerate all datasets from a specific organization.
    *   **Advanced Questions:**
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

### Transportation & Transit (New Category - Not Yet Implemented)

*   **Public Transit APIs (e.g., GTFS-based):** Enumerate routes, stops, schedules, and real-time vehicle positions for a city's transit system.
    *   **Advanced Questions:**
        *   "List all bus routes that provide a direct connection from station A to station B before 9 AM on a weekday."
        *   "Identify all subway lines that operate on weekends and are wheelchair accessible."
*   **Aviation Data APIs (e.g., FlightAware, OpenSky Network):** Enumerate flight statuses, airport information, and aircraft trajectories.
    *   **Advanced Questions:**
        *   "Find all international flights departing from JFK that are delayed by more than 2 hours."
        *   "Enumerate all currently airborne Airbus A380 aircraft within European airspace."

### Sports (New Category - Not Yet Implemented)

*   **TheSportsDB:** Enumerate teams, players, schedules, and results for various sports leagues.
    *   **Advanced Questions:**
        *   "List all matches in player X's career where they were named 'Man of the Match'."
        *   "Identify all teams that remained undefeated at home during a specific season."
        *   "Enumerate all international (non-club) matches in which a specific player has participated."

### Recipes & Nutrition (New Category - Not Yet Implemented)

*   **TheMealDB / Edamam:** Enumerate recipes, ingredients, and detailed nutritional information.
    *   **Advanced Questions:**
        *   "Find all gluten-free, vegetarian dinner recipes that take less than 30 minutes to prepare."
        *   "List all recipes with over 30g of protein but under 500 total calories."
        *   "Enumerate all salad recipes that include 'avocado' but not 'cheese'."

### AI & Machine Learning (3 APIs)

*   **Hugging Face Hub:** Enumerate public machine learning models, datasets, and Spaces.
    *   **Advanced Questions (Implemented):**
        *   `filter_by_task` + `filter_by_tag` + `filter_by_downloads`: List all text-generation models that support Chinese and have more than 100,000 downloads.
        *   `filter_by_tag` + `filter_by_license`: Find all datasets tagged with 'medical imaging' that are licensed under Apache 2.0.
        *   `filter_by_library` + `filter_by_task` + `filter_by_update_time`: Enumerate all PyTorch-based image segmentation models that have been updated in the last month.
        *   `filter_by_likes`: Filter resources by minimum likes count.
        *   Additional filtering capabilities for comprehensive metadata-based queries.
    *   **Test Implementation:** See `enumerate_framework/test_runners/ai_ml/test_huggingface_enhanced.py` for a reference implementation of metadata-rich test results.

## 5. Deprecated/Removed APIs

This section documents APIs that have been removed from the framework and the reasons for their removal.

### Maven Central (Removed - 2025-10-28)

*   **Reason**: Cannot guarantee completeness - the Solr Search API has a hard limit on the number of results that can be returned (default: 1000 versions maximum).
*   **Violation**: Fails to meet the **"Completeness"** principle - unable to enumerate ALL versions for packages with more than 1000 releases.
*   **Technical Details**: The Maven Central API uses `max_versions` parameter with a cap, making it impossible to retrieve the complete version history for prolific packages (e.g., some Spring Framework artifacts have thousands of versions).
*   **Impact**: While 1000 versions may be sufficient for most packages, this limitation violates the core philosophy of "Enumerate All" - a truly intelligent search system must be the most "complete," not bounded by arbitrary limits.

### OpenWeatherMap (Removed - 2024-10-29)

*   **Reason**: Completeness issues - despite documentation claiming historical data from 1979 to present, only ~5 days of historical data are accessible via API. Additionally, authentication complexity (API key requirement with 1000 calls/day free limit).
*   **Violation**: Fails to meet the **"Completeness"** principle and adds unnecessary authentication complexity.
*   **Technical Details**:
    - Documentation claims: "Historical data from 1979 to 4 days ahead"
    - Reality: The timemachine endpoint only provides approximately 5 days of historical data
    - Cannot truly "enumerate all" historical weather data as claimed
    - Free tier limited to 1000 API calls per day, restricting comprehensive enumeration
    - Requires API key registration, adding friction for testing and usage
*   **Evidence**:
    ```python
    # Claimed capability
    fetcher.fetch_historical_weather(days_back=30)

    # Reality: Only returns ~5 days of data, not 30
    ```
*   **Impact**: Violates core philosophy - cannot provide complete historical weather enumeration. The 5-day limitation makes it impossible to answer questions like "Find all rainy days in Tokyo from 2020-2024" or "What were the 10 hottest days in history?" An AI model relying on this API would be severely limited in temporal reasoning and historical weather analysis.
*   **Replacement**: **Open-Meteo API** - Provides TRUE completeness with 80+ years of historical data (1940-present), no authentication required, no rate limits, and perfect alignment with "Enumerate All" principles.

### Open Library (Removed - 2025-10-29)

*   **Reason**: Data quality issues - same work has multiple work IDs for different language editions, causing duplication and inability to accurately enumerate unique works.
*   **Violation**: Fails to meet the **"Precision"**, **"Completeness"**, and **"Determinism"** principles.
*   **Technical Details**:
    - Different language editions of the same work are incorrectly created as separate works instead of being editions under one work.
    - Same work may have duplicate work entries (e.g., J.R.R. Tolkien's "The Lord of the Rings" appears 3+ times with different work IDs: "The Lord of the Rings", "O Senhor dos Anéis", etc.).
    - Cannot distinguish between truly different works and translations/language variants.
*   **Examples**:
    - J.R.R. Tolkien (OL26320A): Returns "O Senhor dos Anéis" as 3 separate works with different IDs.
    - J.K. Rowling (OL23919A): Multiple "Harry Potter" works that are actually different language editions.
*   **Impact**: Violates core philosophy - cannot provide accurate enumeration of unique works. Results include duplicates and inflate the actual number of distinct works by an author. An AI model would be misled into thinking translations are separate creative works.

## 6. API Authentication

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

*   **Code Ecosystem:** GitHub, Docker Hub, Homebrew (key recommended for full access)
*   **Academic/Research:** PubMed, Zenodo
*   **Media/Entertainment:** Spotify, YouTube, TMDb
*   **Social Media:** Twitter/X, Reddit, Discord
*   **Gaming:** Steam, Twitch

## 7. How to Use

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
