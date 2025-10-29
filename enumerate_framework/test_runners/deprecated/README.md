# Deprecated Test Runners

This directory contains test runners for deprecated API fetchers.

These tests are preserved for historical reference but should **NOT** be executed in regular test suites.

## Deprecated Tests

### test_openweathermap.py

Test runner for the deprecated OpenWeatherMap API fetcher.

**Deprecated:** 2024-10-29

**Reason:** The OpenWeatherMap API fetcher was removed due to completeness issues (only ~5 days of historical data vs claimed 1979-present) and authentication complexity.

**Replacement:** Use `test_runners/weather_climate/test_openmeteo.py` instead.

## Related Documentation

- Deprecated fetchers: `/enumerate_framework/fetchers/deprecated/README.md`
- Main documentation: `/GEMINI.md` - Section "5. Deprecated/Removed APIs"
