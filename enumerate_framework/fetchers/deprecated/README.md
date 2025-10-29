# Deprecated API Fetchers

This directory contains API fetchers that have been removed from the main framework due to violations of the "Enumerate All" core principles.

## Removed APIs

### OpenWeatherMap (Removed: 2024-10-29)

**File:** `openweathermap.py`

**Removal Reason:** Violations of core "Enumerate All" principles

#### 1. Completeness Issues (PRIMARY REASON)

- **Claimed:** Historical data from 1979 to present
- **Reality:** Only ~5 days of historical data accessible via API
- **Impact:** Cannot truly "enumerate all" historical weather data
- **Violation:** Fails the **"Completeness"** principle - unable to enumerate all results without major omissions

**Evidence:**
```python
# Documentation claims: "Historical data from 1979 to 4 days ahead"
# Reality: timemachine endpoint only provides ~5 days of data
fetcher.fetch_historical_weather(days_back=30)  # ❌ Actually only gets ~5 days
```

#### 2. Authentication Complexity

- **Requirement:** Mandatory API key registration
- **Free tier limit:** 1000 API calls per day
- **Impact:**
  - Adds friction for testing and usage
  - Rate limits prevent comprehensive enumeration
  - Not suitable for "enumerate all" scenarios requiring many API calls
- **Violation:** Increases complexity and prevents true comprehensive enumeration

#### 3. Determinism Concerns

- **Issue:** Results depend on API subscription tier
- **Impact:** Same query may return different completeness levels based on paid vs free tier
- **Violation:** Weakens the **"Determinism"** principle

### Replacement

**Recommended Alternative:** Open-Meteo API

**Location:** `enumerate_framework/fetchers/weather_climate/openmeteo.py`

**Advantages:**
- ✅ **TRUE Completeness:** 80+ years of historical data (1940-present)
- ✅ **No Authentication:** Completely free, no API key required
- ✅ **No Rate Limits:** Unlimited queries for reasonable use
- ✅ **Deterministic:** Same query always returns same complete dataset
- ✅ **Global Coverage:** Works anywhere in the world with lat/lon coordinates

**Comparison:**

| Feature | OpenWeatherMap | Open-Meteo |
|---------|---------------|------------|
| Historical Data | ~5 days | 1940-present (80+ years) |
| Authentication | API key required | None |
| Free Tier Limit | 1000 calls/day | No limits |
| Completeness | Poor ❌ | Excellent ✅ |
| "Enumerate All" Capable | No | Yes |

**Migration Example:**

```python
# OLD (OpenWeatherMap) - Limited
from fetchers.openweathermap import OpenWeatherMapFetcher
fetcher = OpenWeatherMapFetcher(api_key="your_key")
data, _, _ = fetcher.fetch_historical_weather(
    lat=35.5494, lon=139.7798,
    days_back=30  # ❌ Only gets ~5 days
)

# NEW (Open-Meteo) - Complete
from fetchers.weather_climate.openmeteo import OpenMeteoFetcher
fetcher = OpenMeteoFetcher()  # No API key needed!
data, _, _ = fetcher.fetch_historical_weather(
    lat=35.5494, lon=139.7798,
    start_date="1940-01-01",  # ✅ Can get 80+ years of data
    end_date="2024-10-29"
)
```

## Notes

These deprecated fetchers are kept for reference purposes only. They should **NOT** be used in new test cases or documentation.

For questions about why an API was deprecated, refer to the main project documentation (`GEMINI.md`).

## Related Documentation

- Main documentation: `/GEMINI.md` - Section "5. Deprecated/Removed APIs"
- Open-Meteo fetcher: `/enumerate_framework/fetchers/weather_climate/openmeteo.py`
- Open-Meteo tests: `/enumerate_framework/test_runners/weather_climate/test_openmeteo.py`
