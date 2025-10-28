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

## 3. API Catalog and Advanced Questions

This section summarizes the available APIs and proposes more complex, metadata-based questions, as inspired by the `dblp.py` fetcher.

### Code Ecosystem (11 APIs)

*   **NPM, PyPI, Crates.io, RubyGems, NuGet, Go Proxy, Conda, CRAN:** Enumerate all versions of a package.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "Find all versions of package X that were published by a specific user/owner."
        *   "List all versions of package X that have a specific dependency."
        *   "Identify all pre-release versions of package X (e.g., containing 'alpha', 'beta', 'rc')."
        *   "Find the version of package X with the most downloads."
*   **GitHub:** Enumerate repositories, tags, releases, and branches.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all repositories for user X that are forks."
        *   "Find all releases for repository Y that are marked as pre-release."
        *   "List all branches in repository Y that have not been updated in the last year."
        *   "Find the repository owned by user X with the most stars."
*   **Docker Hub:** Enumerate all tags for an image.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all tags for the 'python' image that are based on 'alpine'."
        *   "Find the most recently pushed tag for the 'ubuntu' image."
        *   "List all tags for the 'nginx' image that are for a specific architecture (e.g., 'arm64')."
*   **Homebrew:** Enumerate the current version and variations of a formula.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all available services for the 'postgresql' formula."
        *   "Check if the 'python' formula is keg-only and why."
        *   "List all aliases for the 'openssl@3' formula."

### Academic/Research (3 APIs)

*   **DBLP:** Enumerate all publications for an author using their PID.
    *   **Existing Advanced Questions:**
        *   Filter publications by author position (first, last, etc.).
        *   Filter by venue (conference/journal).
        *   Filter by year range.
        *   Filter by publication type.
*   **PubMed:** Enumerate all publications for an author (preferably via ORCID).
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all publications by author X where they are the corresponding author."
        *   "Find all publications by author X that are review articles."
        *   "List all publications by author X that were published in the 'Nature' journal."
*   **Zenodo:** Enumerate all research data for a researcher (via ORCID).
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all datasets by researcher X that are over 1GB in size."
        *   "Find all software publications by researcher X."
        *   "List all publications by researcher X that have a Creative Commons license."

### Media/Entertainment (4 APIs)

*   **Spotify:** Enumerate all albums for an artist and all tracks for an album.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all albums by artist X that are collaborations."
        *   "Find all tracks on album Y that are explicit."
        *   "List all albums by artist X that were released before the year 2000."
*   **YouTube:** Enumerate all videos and playlists for a channel.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all videos in channel X that are longer than 1 hour."
        *   "Find the most viewed video in playlist Y."
        *   "List all live streams from channel X."
*   **TMDb:** Enumerate all works for an actor/director, all seasons for a series, etc.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all movies where actor X also served as a producer."
        *   "Find all episodes of TV series Y from season 3 that have a guest star."
        *   "List all movies directed by director Z that are in the 'Science Fiction' genre."
*   **Open Library:** Enumerate all works for an author and all editions of a book.
    *   **Advanced Questions (Not Yet Implemented):**
        *   "List all books by author X that have been translated into more than 10 languages."
        *   "Find the first edition of book Y."
        *   "List all books by author X that have more than 500 pages."

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

### Weather & Climate (New Category - Not Yet Implemented)

*   **OpenWeatherMap:** Enumerate various weather data for a given location.
    *   **Advanced Questions:**
        *   "Find all days in the last 30 days in city X where it rained and the wind speed exceeded 20 km/h."
        *   "List all rain-free windows (lasting at least 6 hours) for a farmer over the next week for spraying pesticides."
        *   "Query all active severe weather alerts within a 50km radius of a specific coordinate."

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

### AI & Machine Learning (New Category - Not Yet Implemented)

*   **Hugging Face Hub:** Enumerate public machine learning models, datasets, and Spaces.
    *   **Advanced Questions:**
        *   "List all text-generation models that support Chinese and have more than 100,000 downloads."
        *   "Find all datasets tagged with 'medical imaging' that are licensed under Apache 2.0."
        *   "Enumerate all PyTorch-based image segmentation models that have been updated in the last month."

## 4. Deprecated/Removed APIs

This section documents APIs that have been removed from the framework and the reasons for their removal.

### Maven Central (Removed - 2025-10-28)

*   **Reason**: Cannot guarantee completeness - the Solr Search API has a hard limit on the number of results that can be returned (default: 1000 versions maximum).
*   **Violation**: Fails to meet the **"Completeness"** principle - unable to enumerate ALL versions for packages with more than 1000 releases.
*   **Technical Details**: The Maven Central API uses `max_versions` parameter with a cap, making it impossible to retrieve the complete version history for prolific packages (e.g., some Spring Framework artifacts have thousands of versions).
*   **Impact**: While 1000 versions may be sufficient for most packages, this limitation violates the core philosophy of "Enumerate All" - a truly intelligent search system must be the most "complete," not bounded by arbitrary limits.

## 5. API Authentication

To assist with testing, the APIs listed above can be grouped by their authentication requirements. Note that some APIs may have stricter rate limits for unauthenticated requests.

### APIs Typically Not Requiring an API Key

*   **Code Ecosystem:** PyPI, Crates.io, RubyGems, NuGet, Go Proxy, Conda, CRAN
*   **Academic/Research:** DBLP
*   **Media/Entertainment:** Open Library
*   **Business/Finance:** SEC EDGAR
*   **Infrastructure/Security:** crt.sh
*   **Geolocation/Maps:** OpenStreetMap
*   **Government & Open Data:** Data.gov

### APIs Requiring an API Key or OAuth

*   **Code Ecosystem:** GitHub, Docker Hub, Homebrew (key recommended for full access)
*   **Academic/Research:** PubMed, Zenodo
*   **Media/Entertainment:** Spotify, YouTube, TMDb
*   **Social Media:** Twitter/X, Reddit, Discord
*   **Gaming:** Steam, Twitch

## 6. How to Use

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
