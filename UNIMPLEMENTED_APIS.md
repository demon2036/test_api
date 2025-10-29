# Unimplemented APIs

This file lists the APIs that are mentioned in the project documentation but do not have a corresponding fetcher and/or test runner implementation.

## Code Ecosystem

*   **Docker Hub:** Enumerate all images, tags, and layers for a repository.
    *   **Status:** Fetcher implemented but removed (test runner deleted).
    *   **Reason:** Fetcher exists at `enumerate_framework/fetchers/deprecated/docker.py` but corresponding test runner has been removed from the code_ecosystem directory. Unclear if it should be fully deprecated or if test runner needs to be reimplemented.

## Media/Entertainment

*   **Goodreads:** Enumerate all books for an author, reviews for a book, etc.
    *   **Status:** Fetcher implemented at `enumerate_framework/fetchers/media_entertainment/goodreads.py` but **no test runner**.
    *   **Next Steps:** Implement `enumerate_framework/test_runners/media_entertainment/test_goodreads.py`.
*   **IMDb:** Enumerate all movies/shows for an actor/director.
    *   **Status:** Fetcher implemented at `enumerate_framework/fetchers/media_entertainment/imdb.py` but **no test runner**.
    *   **Next Steps:** Implement `enumerate_framework/test_runners/media_entertainment/test_imdb.py`.

## Social Media

*   **Twitter/X:** Enumerate tweets, followers, and lists for a user.
*   **Reddit:** Enumerate posts in a subreddit and comments on a post.
*   **Discord:** Enumerate servers (guilds), channels, and members.

## Gaming

*   **Steam:** Enumerate all games owned by a user, and all achievements for a game.
*   **Twitch:** Enumerate all live streams for a specific game, and all followers of a channel.

## Transportation & Transit

*   **Public Transit APIs (e.g., GTFS-based):** Enumerate routes, stops, schedules, and real-time vehicle positions for a city's transit system.
*   **Aviation Data APIs (e.g., FlightAware, OpenSky Network):** Enumerate flight statuses, airport information, and aircraft trajectories.

## Sports

*   **TheSportsDB:** Enumerate teams, players, schedules, and results for various sports leagues.

## Recipes & Nutrition

*   **TheMealDB / Edamam:** Enumerate recipes, ingredients, and detailed nutritional information.

## Deprecated/Removed APIs

This section documents APIs that have been removed from the framework and the reasons for their removal.

### Docker Hub (Removed/Incomplete - 2025-10-29)

*   **Reason**: Test runner was removed from the framework while fetcher remains in deprecated folder.
*   **Status**: Partial implementation - fetcher exists at `enumerate_framework/fetchers/deprecated/docker.py` but test runner has been deleted.
*   **Technical Details**:
    - Fetcher implementation appears complete for enumerating Docker images, tags, and layers
    - Test runner (`enumerate_framework/test_runners/code_ecosystem/test_docker.py`) has been removed from the codebase
    - Unclear if removal was intentional or if test runner needs to be reimplemented
*   **Impact**: Without test runner, Docker Hub cannot be included in automated testing and verification workflows. The API may still work but lacks integration with the framework's testing infrastructure.
*   **Next Steps**:
    - If Docker Hub support is desired, reimplement test runner at `enumerate_framework/test_runners/code_ecosystem/test_docker.py`
    - If Docker Hub is being deprecated, move fetcher from deprecated folder and document reason for removal

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