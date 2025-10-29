"""
Open-Meteo API Fetcher

This module provides functionality to enumerate weather data using the Open-Meteo API.

Key Features:
- NO API key required - completely free and open
- Enumerate historical weather data from 1940 to present (80+ years)
- 16-day weather forecast
- Global coverage with precise lat/lon coordinates
- Advanced filtering: temperature, precipitation, wind speed, etc.
- NO rate limits for reasonable use

Advantages over OpenWeatherMap:
- TRUE completeness: 80+ years of historical data (vs 5 days)
- NO authentication complexity (vs API key requirement)
- NO rate limits (vs 1000 calls/day)
- Perfectly aligned with "Enumerate All" philosophy

Example Usage:
    fetcher = OpenMeteoFetcher()

    # Get historical weather data for 5 years
    weather_data, api_info, question = fetcher.fetch_historical_weather(
        lat=35.5494,
        lon=139.7798,
        start_date="2020-01-01",
        end_date="2024-12-31"
    )

    # Find all rainy days in the period
    rainy_days = fetcher.filter_by_precipitation(
        weather_data,
        min_precipitation=0.1  # mm
    )

    # Find hottest days in 80+ years
    all_time_data, _, _ = fetcher.fetch_historical_weather(
        lat=35.5494,
        lon=139.7798,
        start_date="1940-01-01",
        end_date="2024-10-29"
    )
    hottest = fetcher.get_top_n_by_temperature(all_time_data, n=10, descending=True)
"""

import requests
import time
import random
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from fetchers.base import BaseFetcher


class OpenMeteoFetcher(BaseFetcher):
    """Fetcher for Open-Meteo API - No authentication required"""

    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    PRESET_LOCATIONS = {
        "tokyo_haneda_airport": {
            "name": "东京羽田机场",
            "lat": 35.5494,
            "lon": 139.7798
        },
        "tokyo": {
            "name": "东京",
            "lat": 35.6762,
            "lon": 139.6503
        },
        "beijing": {
            "name": "北京",
            "lat": 39.9042,
            "lon": 116.4074
        },
        "shanghai": {
            "name": "上海",
            "lat": 31.2304,
            "lon": 121.4737
        },
        "new_york": {
            "name": "纽约",
            "lat": 40.7128,
            "lon": -74.0060
        },
        "london": {
            "name": "伦敦",
            "lat": 51.5074,
            "lon": -0.1278
        },
        "paris": {
            "name": "巴黎",
            "lat": 48.8566,
            "lon": 2.3522
        }
    }

    def __init__(self):
        """Initialize the Open-Meteo fetcher.

        No API key required - Open-Meteo is completely free and open!
        """
        pass

    def _make_request(
        self,
        endpoint_url: str,
        params: Dict
    ) -> Dict[str, Any]:
        """Make a request to the Open-Meteo API.

        Args:
            endpoint_url: API endpoint URL (archive or forecast)
            params: Query parameters

        Returns:
            JSON response from the API

        Raises:
            requests.RequestException: If the API request fails
        """
        # Determine timeout based on date range (for large historical queries)
        timeout = 30  # Default timeout
        if 'start_date' in params and 'end_date' in params:
            try:
                from datetime import datetime
                start = datetime.strptime(params['start_date'], '%Y-%m-%d')
                end = datetime.strptime(params['end_date'], '%Y-%m-%d')
                days = (end - start).days
                # For very large queries (>10 years), use longer timeout
                if days > 3650:  # >10 years
                    timeout = 120  # 2 minutes for 80+ year queries
                elif days > 365:  # >1 year
                    timeout = 60
            except:
                pass  # Use default timeout if parsing fails

        # Robust retry with exponential backoff and jitter for 429/5xx
        attempts = 6
        backoff = 2.0
        delay = 1.0

        headers = {
            "User-Agent": "enumerate-framework/1.0 (+https://open-meteo.com)"
        }

        for attempt in range(1, attempts + 1):
            try:
                # Small random jitter before request to avoid bursts
                time.sleep(random.uniform(0.0, 0.3))

                response = requests.get(endpoint_url, params=params, timeout=timeout, headers=headers)

                # Handle rate limiting explicitly
                if response.status_code == 429:
                    # Honor Retry-After if present
                    retry_after = response.headers.get('Retry-After')
                    wait = None
                    if retry_after:
                        # Retry-After may be seconds or an HTTP date
                        try:
                            wait = float(retry_after)
                        except ValueError:
                            # Parse HTTP date format
                            try:
                                from email.utils import parsedate_to_datetime
                                ra_dt = parsedate_to_datetime(retry_after)
                                wait = max(0.0, (ra_dt - datetime.utcnow()).total_seconds())
                            except Exception:
                                wait = None
                    if wait is None:
                        wait = delay
                    if attempt == attempts:
                        response.raise_for_status()
                    time.sleep(wait + random.uniform(0.0, 0.5))
                    delay *= backoff
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                if attempt == attempts:
                    raise Exception(f"Open-Meteo API request failed: {str(e)}")
                # Backoff for transient errors (e.g., timeouts, 5xx)
                time.sleep(delay + random.uniform(0.0, 0.5))
                delay *= backoff

    @classmethod
    def get_preset_location(cls, location_key: str) -> Dict[str, Any]:
        """Return preset location information for a known key."""
        preset = cls.PRESET_LOCATIONS.get(location_key)
        if not preset:
            raise ValueError(f"Unknown preset location: {location_key}")
        return preset

    def _resolve_coordinates(
        self,
        lat: Optional[float],
        lon: Optional[float],
        location_key: Optional[str] = None
    ) -> Tuple[float, float, Optional[str], Optional[str]]:
        """Resolve latitude/longitude using either direct values or a preset key."""
        location_name = None

        if location_key:
            preset = self.get_preset_location(location_key)
            preset_lat = preset['lat']
            preset_lon = preset['lon']
            location_name = preset.get('name', location_key)

            if lat is None:
                lat = preset_lat
            if lon is None:
                lon = preset_lon

        if lat is None or lon is None:
            raise ValueError(
                "Latitude and longitude are required. Provide lat/lon directly or supply a known location_key."
            )

        return float(lat), float(lon), location_name, location_key

    @staticmethod
    def _format_location_label(lat: float, lon: float, location_name: Optional[str]) -> str:
        """Format location label for display."""
        coords = f"({lat}, {lon})"
        return f"{location_name} {coords}" if location_name else coords

    def fetch_historical_weather(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        start_date: str = "2024-01-01",
        end_date: str = "2024-12-31",
        include_metadata: bool = True,
        location_key: Optional[str] = None
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch historical weather data for a date range.

        This is the core "Enumerate All" capability - can retrieve 80+ years
        of complete historical data (1940-present).

        Args:
            lat: Latitude (-90 to 90). Optional if location_key is provided.
            lon: Longitude (-180 to 180). Optional if location_key is provided.
            start_date: Start date in YYYY-MM-DD format (earliest: 1940-01-01)
            end_date: End date in YYYY-MM-DD format (latest: today)
            include_metadata: Whether to include full weather metadata
            location_key: Optional preset location identifier

        Returns:
            Tuple of (list of daily weather data, api_info dict, question string)
        """
        lat, lon, location_name, resolved_key = self._resolve_coordinates(lat, lon, location_key)
        location_label = self._format_location_label(lat, lon, location_name)

        params = {
            'latitude': lat,
            'longitude': lon,
            'start_date': start_date,
            'end_date': end_date,
            'daily': ','.join([
                'temperature_2m_max',
                'temperature_2m_min',
                'temperature_2m_mean',
                'precipitation_sum',
                'rain_sum',
                'snowfall_sum',
                'precipitation_hours',
                'wind_speed_10m_max',
                'wind_gusts_10m_max',
                'wind_direction_10m_dominant',
                'shortwave_radiation_sum',
                'et0_fao_evapotranspiration',
                'weather_code'
            ]),
            'timezone': 'auto'
        }

        data = self._make_request(self.ARCHIVE_URL, params)

        # Parse response
        daily_data = data.get('daily', {})
        time_values = daily_data.get('time', [])

        weather_data = []
        for i, date_str in enumerate(time_values):
            if not include_metadata:
                weather_data.append(date_str)
            else:
                weather_data.append({
                    'date': date_str,
                    'temp_max': daily_data.get('temperature_2m_max', [])[i],
                    'temp_min': daily_data.get('temperature_2m_min', [])[i],
                    'temp_mean': daily_data.get('temperature_2m_mean', [])[i],
                    'precipitation': daily_data.get('precipitation_sum', [])[i],
                    'rain': daily_data.get('rain_sum', [])[i],
                    'snowfall': daily_data.get('snowfall_sum', [])[i],
                    'precipitation_hours': daily_data.get('precipitation_hours', [])[i],
                    'wind_speed_max': daily_data.get('wind_speed_10m_max', [])[i],
                    'wind_gusts_max': daily_data.get('wind_gusts_10m_max', [])[i],
                    'wind_direction': daily_data.get('wind_direction_10m_dominant', [])[i],
                    'solar_radiation': daily_data.get('shortwave_radiation_sum', [])[i],
                    'evapotranspiration': daily_data.get('et0_fao_evapotranspiration', [])[i],
                    'weather_code': daily_data.get('weather_code', [])[i]
                })

        question = f"枚举{location_label}从{start_date}到{end_date}的所有历史天气数据"

        api_info = {
            "api_endpoint": self.ARCHIVE_URL,
            "method": "GET",
            "parameters": {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "timezone": "auto"
            },
            "authentication": "No API key required",
            "rate_limit": "No rate limits",
            "documentation": "https://open-meteo.com/en/docs/historical-weather-api",
            "total_found": len(weather_data),
            "date_range": f"{start_date} to {end_date}",
            "data_source": "ERA5 reanalysis (ECMWF)"
        }

        if resolved_key:
            api_info["parameters"]["location_key"] = resolved_key
            api_info["location_name"] = location_name

        return weather_data, api_info, question

    def fetch_weather_forecast(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        forecast_days: int = 16,
        include_metadata: bool = True,
        location_key: Optional[str] = None
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch daily weather forecast for up to 16 days.

        Args:
            lat: Latitude (-90 to 90). Optional if location_key is provided.
            lon: Longitude (-180 to 180). Optional if location_key is provided.
            forecast_days: Number of forecast days (1-16, default: 16)
            include_metadata: Whether to include full weather metadata
            location_key: Optional preset location identifier

        Returns:
            Tuple of (list of daily forecasts, api_info dict, question string)
        """
        lat, lon, location_name, resolved_key = self._resolve_coordinates(lat, lon, location_key)
        location_label = self._format_location_label(lat, lon, location_name)

        if forecast_days < 1 or forecast_days > 16:
            forecast_days = 16

        params = {
            'latitude': lat,
            'longitude': lon,
            'forecast_days': forecast_days,
            'daily': ','.join([
                'temperature_2m_max',
                'temperature_2m_min',
                'temperature_2m_mean',
                'precipitation_sum',
                'rain_sum',
                'snowfall_sum',
                'precipitation_hours',
                'precipitation_probability_max',
                'wind_speed_10m_max',
                'wind_gusts_10m_max',
                'wind_direction_10m_dominant',
                'weather_code',
                'sunrise',
                'sunset',
                'uv_index_max'
            ]),
            'timezone': 'auto'
        }

        data = self._make_request(self.FORECAST_URL, params)

        # Parse response
        daily_data = data.get('daily', {})
        time_values = daily_data.get('time', [])

        forecast_data = []
        for i, date_str in enumerate(time_values):
            if not include_metadata:
                forecast_data.append(date_str)
            else:
                forecast_data.append({
                    'date': date_str,
                    'temp_max': daily_data.get('temperature_2m_max', [])[i],
                    'temp_min': daily_data.get('temperature_2m_min', [])[i],
                    'temp_mean': daily_data.get('temperature_2m_mean', [])[i],
                    'precipitation': daily_data.get('precipitation_sum', [])[i],
                    'rain': daily_data.get('rain_sum', [])[i],
                    'snowfall': daily_data.get('snowfall_sum', [])[i],
                    'precipitation_hours': daily_data.get('precipitation_hours', [])[i],
                    'precipitation_probability': daily_data.get('precipitation_probability_max', [])[i],
                    'wind_speed_max': daily_data.get('wind_speed_10m_max', [])[i],
                    'wind_gusts_max': daily_data.get('wind_gusts_10m_max', [])[i],
                    'wind_direction': daily_data.get('wind_direction_10m_dominant', [])[i],
                    'weather_code': daily_data.get('weather_code', [])[i],
                    'sunrise': daily_data.get('sunrise', [])[i],
                    'sunset': daily_data.get('sunset', [])[i],
                    'uv_index_max': daily_data.get('uv_index_max', [])[i]
                })

        question = f"枚举{location_label}未来{forecast_days}天的天气预报"

        api_info = {
            "api_endpoint": self.FORECAST_URL,
            "method": "GET",
            "parameters": {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": forecast_days,
                "timezone": "auto"
            },
            "authentication": "No API key required",
            "rate_limit": "No rate limits",
            "documentation": "https://open-meteo.com/en/docs",
            "total_found": len(forecast_data),
            "forecast_days": forecast_days
        }

        if resolved_key:
            api_info["parameters"]["location_key"] = resolved_key
            api_info["location_name"] = location_name

        return forecast_data, api_info, question

    # ========================================
    # Advanced Filter Methods
    # ========================================

    def filter_by_precipitation(
        self,
        weather_data: List[Dict],
        min_precipitation: float = 0.1
    ) -> List[Dict]:
        """Filter days where precipitation exceeded threshold.

        This answers questions like:
        "Find all rainy days in Tokyo from 2020-2024"

        Args:
            weather_data: List of weather data with metadata
            min_precipitation: Minimum precipitation in mm (default: 0.1mm)

        Returns:
            Filtered list of weather data
        """
        filtered = []
        for data in weather_data:
            precip = data.get('precipitation', 0) or 0
            if precip >= min_precipitation:
                filtered.append(data)
        return filtered

    def filter_by_temperature(
        self,
        weather_data: List[Dict],
        min_temp: Optional[float] = None,
        max_temp: Optional[float] = None,
        temp_field: str = 'temp_mean'
    ) -> List[Dict]:
        """Filter weather data by temperature range.

        Args:
            weather_data: List of weather data with metadata
            min_temp: Minimum temperature in Celsius
            max_temp: Maximum temperature in Celsius
            temp_field: Which temperature field to use ('temp_mean', 'temp_max', 'temp_min')

        Returns:
            Filtered list of weather data
        """
        filtered = []
        for data in weather_data:
            temp = data.get(temp_field)
            if temp is None:
                continue

            if min_temp is not None and temp < min_temp:
                continue
            if max_temp is not None and temp > max_temp:
                continue

            filtered.append(data)

        return filtered

    def filter_by_wind_speed(
        self,
        weather_data: List[Dict],
        min_wind_speed: Optional[float] = None,
        max_wind_speed: Optional[float] = None
    ) -> List[Dict]:
        """Filter weather data by wind speed range.

        Args:
            weather_data: List of weather data with metadata
            min_wind_speed: Minimum wind speed in km/h
            max_wind_speed: Maximum wind speed in km/h

        Returns:
            Filtered list of weather data
        """
        filtered = []
        for data in weather_data:
            wind = data.get('wind_speed_max', 0) or 0

            if min_wind_speed is not None and wind < min_wind_speed:
                continue
            if max_wind_speed is not None and wind > max_wind_speed:
                continue

            filtered.append(data)

        return filtered

    def filter_rainy_and_windy_days(
        self,
        weather_data: List[Dict],
        min_precipitation: float = 0.1,
        min_wind_speed: float = 20.0
    ) -> List[Dict]:
        """Filter days where it rained AND wind speed exceeded threshold.

        This answers the advanced question:
        "Find all days where it rained and wind speed exceeded 20 km/h."

        Args:
            weather_data: List of weather data with metadata
            min_precipitation: Minimum precipitation in mm (default: 0.1mm)
            min_wind_speed: Minimum wind speed in km/h (default: 20)

        Returns:
            Filtered list of weather data
        """
        rainy = self.filter_by_precipitation(weather_data, min_precipitation)
        rainy_windy = self.filter_by_wind_speed(rainy, min_wind_speed)
        return rainy_windy

    def find_rain_free_windows(
        self,
        weather_data: List[Dict],
        min_days: int = 7
    ) -> List[Dict]:
        """Find continuous rain-free windows of at least N days.

        This answers questions like:
        "List all rain-free windows lasting at least 7 days in 2024"

        Args:
            weather_data: List of daily weather data with metadata
            min_days: Minimum duration of rain-free window in days (default: 7)

        Returns:
            List of rain-free windows with start/end dates and duration
        """
        windows = []
        current_window_start = None
        current_window_days = []

        for i, day_data in enumerate(weather_data):
            # Check if this day has rain
            precip = day_data.get('precipitation', 0) or 0
            has_rain = precip > 0.1  # Consider > 0.1mm as rainy

            if not has_rain:
                # Rain-free day
                if current_window_start is None:
                    current_window_start = i
                    current_window_days = [day_data]
                else:
                    current_window_days.append(day_data)
            else:
                # Rain detected - check if we have a window to save
                if current_window_start is not None:
                    duration = len(current_window_days)
                    if duration >= min_days:
                        # Calculate averages
                        avg_temp = sum(d.get('temp_mean', 0) or 0 for d in current_window_days) / duration
                        avg_wind = sum(d.get('wind_speed_max', 0) or 0 for d in current_window_days) / duration

                        windows.append({
                            "start_date": current_window_days[0]['date'],
                            "end_date": current_window_days[-1]['date'],
                            "duration_days": duration,
                            "avg_temp": round(avg_temp, 2),
                            "avg_wind_speed": round(avg_wind, 2)
                        })
                    # Reset window
                    current_window_start = None
                    current_window_days = []

        # Check final window
        if current_window_start is not None:
            duration = len(current_window_days)
            if duration >= min_days:
                avg_temp = sum(d.get('temp_mean', 0) or 0 for d in current_window_days) / duration
                avg_wind = sum(d.get('wind_speed_max', 0) or 0 for d in current_window_days) / duration

                windows.append({
                    "start_date": current_window_days[0]['date'],
                    "end_date": current_window_days[-1]['date'],
                    "duration_days": duration,
                    "avg_temp": round(avg_temp, 2),
                    "avg_wind_speed": round(avg_wind, 2)
                })

        return windows

    def get_top_n_by_temperature(
        self,
        weather_data: List[Dict],
        n: int = 10,
        descending: bool = True,
        temp_field: str = 'temp_max'
    ) -> List[Dict]:
        """Get top N days sorted by temperature.

        This answers questions like:
        "Find the 10 hottest days in Tokyo from 1940-2024"

        Args:
            weather_data: List of weather data with metadata
            n: Number of top days to return
            descending: If True, get hottest days; if False, get coldest days
            temp_field: Which temperature field to use ('temp_max', 'temp_min', 'temp_mean')

        Returns:
            List of top N days sorted by temperature with rank
        """
        # Filter out days with no temperature data
        valid_data = [d for d in weather_data if d.get(temp_field) is not None]

        # Sort by temperature
        sorted_data = sorted(
            valid_data,
            key=lambda x: x.get(temp_field, -999),
            reverse=descending
        )

        # Take top N and add rank
        top_n = sorted_data[:n]
        for i, day in enumerate(top_n, 1):
            day['rank'] = i

        return top_n

    def filter_by_year(
        self,
        weather_data: List[Dict],
        year: int
    ) -> List[Dict]:
        """Filter weather data to a specific year.

        Args:
            weather_data: List of weather data with metadata
            year: Year to filter (e.g., 2024)

        Returns:
            Filtered list of weather data
        """
        filtered = []
        for data in weather_data:
            date_str = data.get('date', '')
            if date_str.startswith(str(year)):
                filtered.append(data)
        return filtered

    def filter_by_month(
        self,
        weather_data: List[Dict],
        month: int
    ) -> List[Dict]:
        """Filter weather data to a specific month (across all years).

        Args:
            weather_data: List of weather data with metadata
            month: Month to filter (1-12)

        Returns:
            Filtered list of weather data
        """
        filtered = []
        month_str = f"-{month:02d}-"
        for data in weather_data:
            date_str = data.get('date', '')
            if month_str in date_str:
                filtered.append(data)
        return filtered

    def filter_by_season(
        self,
        weather_data: List[Dict],
        season: str
    ) -> List[Dict]:
        """Filter weather data by season (Northern Hemisphere).

        Args:
            weather_data: List of weather data with metadata
            season: Season name ('spring', 'summer', 'autumn'/'fall', 'winter')

        Returns:
            Filtered list of weather data
        """
        season = season.lower()

        # Define season months (Northern Hemisphere)
        season_months = {
            'spring': [3, 4, 5],
            'summer': [6, 7, 8],
            'autumn': [9, 10, 11],
            'fall': [9, 10, 11],
            'winter': [12, 1, 2]
        }

        if season not in season_months:
            raise ValueError(f"Invalid season: {season}. Use 'spring', 'summer', 'autumn'/'fall', or 'winter'")

        months = season_months[season]
        filtered = []

        for data in weather_data:
            date_str = data.get('date', '')
            if len(date_str) >= 7:
                try:
                    month = int(date_str[5:7])
                    if month in months:
                        filtered.append(data)
                except (ValueError, IndexError):
                    continue

        return filtered

    def compare_period_temperatures(
        self,
        weather_data: List[Dict],
        period1_start: str,
        period1_end: str,
        period2_start: str,
        period2_end: str,
        season: Optional[str] = None,
        temp_field: str = 'temp_mean'
    ) -> Dict[str, Any]:
        """Compare average temperatures between two time periods.

        This answers advanced questions like:
        "Compare Tokyo summer temperatures: 1940-1970 vs 1990-2024"
        "Has Tokyo's climate warmed over the past 80 years?"

        Args:
            weather_data: List of weather data with metadata
            period1_start: Start date of first period (YYYY-MM-DD)
            period1_end: End date of first period (YYYY-MM-DD)
            period2_start: Start date of second period (YYYY-MM-DD)
            period2_end: End date of second period (YYYY-MM-DD)
            season: Optional season filter ('spring', 'summer', 'autumn', 'winter')
            temp_field: Temperature field to compare ('temp_mean', 'temp_max', 'temp_min')

        Returns:
            Dictionary with comparison statistics
        """
        # Filter period 1
        period1_data = [
            d for d in weather_data
            if period1_start <= d.get('date', '') <= period1_end
        ]

        # Filter period 2
        period2_data = [
            d for d in weather_data
            if period2_start <= d.get('date', '') <= period2_end
        ]

        # Apply season filter if specified
        if season:
            period1_data = self.filter_by_season(period1_data, season)
            period2_data = self.filter_by_season(period2_data, season)

        # Calculate statistics for period 1
        period1_temps = [d.get(temp_field) for d in period1_data if d.get(temp_field) is not None]
        period1_avg = sum(period1_temps) / len(period1_temps) if period1_temps else None
        period1_max = max(period1_temps) if period1_temps else None
        period1_min = min(period1_temps) if period1_temps else None

        # Calculate statistics for period 2
        period2_temps = [d.get(temp_field) for d in period2_data if d.get(temp_field) is not None]
        period2_avg = sum(period2_temps) / len(period2_temps) if period2_temps else None
        period2_max = max(period2_temps) if period2_temps else None
        period2_min = min(period2_temps) if period2_temps else None

        # Calculate difference
        temp_difference = None
        percent_change = None
        if period1_avg is not None and period2_avg is not None:
            temp_difference = period2_avg - period1_avg
            # Use absolute temperature for percent (Kelvin base)
            period1_kelvin = period1_avg + 273.15
            percent_change = (temp_difference / period1_kelvin) * 100

        return {
            'period1': {
                'date_range': f"{period1_start} to {period1_end}",
                'total_days': len(period1_data),
                'avg_temp': round(period1_avg, 2) if period1_avg is not None else None,
                'max_temp': round(period1_max, 2) if period1_max is not None else None,
                'min_temp': round(period1_min, 2) if period1_min is not None else None
            },
            'period2': {
                'date_range': f"{period2_start} to {period2_end}",
                'total_days': len(period2_data),
                'avg_temp': round(period2_avg, 2) if period2_avg is not None else None,
                'max_temp': round(period2_max, 2) if period2_max is not None else None,
                'min_temp': round(period2_min, 2) if period2_min is not None else None
            },
            'comparison': {
                'temp_difference': round(temp_difference, 2) if temp_difference is not None else None,
                'percent_change': round(percent_change, 4) if percent_change is not None else None,
                'warming_detected': temp_difference > 0 if temp_difference is not None else None,
                'temp_field_used': temp_field,
                'season_filter': season
            }
        }

    def find_longest_heatwave(
        self,
        weather_data: List[Dict],
        min_temp: float = 30.0,
        temp_field: str = 'temp_max',
        min_duration: int = 3
    ) -> Dict[str, Any]:
        """Find the longest continuous period above temperature threshold.

        This answers advanced questions like:
        "Find the longest heatwave (consecutive days >30°C) in Tokyo from 1940-2024"
        "What was the most extreme continuous hot period in history?"

        Args:
            weather_data: List of weather data with metadata
            min_temp: Minimum temperature threshold in Celsius (default: 30°C)
            temp_field: Temperature field to check ('temp_max', 'temp_min', 'temp_mean')
            min_duration: Minimum duration in days to qualify as heatwave (default: 3)

        Returns:
            Dictionary with the longest heatwave information
        """
        longest_heatwave = None
        current_heatwave_start = None
        current_heatwave_days = []

        # Sort by date to ensure chronological order
        sorted_data = sorted(weather_data, key=lambda x: x.get('date', ''))

        for i, day_data in enumerate(sorted_data):
            temp = day_data.get(temp_field)

            # Check if this day qualifies
            if temp is not None and temp >= min_temp:
                # Hot day - part of heatwave
                if current_heatwave_start is None:
                    # Start new heatwave
                    current_heatwave_start = i
                    current_heatwave_days = [day_data]
                else:
                    # Continue heatwave
                    current_heatwave_days.append(day_data)
            else:
                # Not hot enough - check if we should save current heatwave
                if current_heatwave_start is not None:
                    duration = len(current_heatwave_days)
                    if duration >= min_duration:
                        # Calculate heatwave statistics
                        temps = [d.get(temp_field) for d in current_heatwave_days if d.get(temp_field) is not None]
                        avg_temp = sum(temps) / len(temps) if temps else 0
                        max_temp = max(temps) if temps else 0

                        heatwave_info = {
                            "start_date": current_heatwave_days[0]['date'],
                            "end_date": current_heatwave_days[-1]['date'],
                            "duration_days": duration,
                            "avg_temp": round(avg_temp, 2),
                            "max_temp": round(max_temp, 2),
                            "peak_date": max(current_heatwave_days, key=lambda x: x.get(temp_field, 0))['date']
                        }

                        # Check if this is the longest so far
                        if longest_heatwave is None or duration > longest_heatwave['duration_days']:
                            longest_heatwave = heatwave_info

                    # Reset heatwave
                    current_heatwave_start = None
                    current_heatwave_days = []

        # Check final heatwave
        if current_heatwave_start is not None:
            duration = len(current_heatwave_days)
            if duration >= min_duration:
                temps = [d.get(temp_field) for d in current_heatwave_days if d.get(temp_field) is not None]
                avg_temp = sum(temps) / len(temps) if temps else 0
                max_temp = max(temps) if temps else 0

                heatwave_info = {
                    "start_date": current_heatwave_days[0]['date'],
                    "end_date": current_heatwave_days[-1]['date'],
                    "duration_days": duration,
                    "avg_temp": round(avg_temp, 2),
                    "max_temp": round(max_temp, 2),
                    "peak_date": max(current_heatwave_days, key=lambda x: x.get(temp_field, 0))['date']
                }

                if longest_heatwave is None or duration > longest_heatwave['duration_days']:
                    longest_heatwave = heatwave_info

        if longest_heatwave is None:
            return {
                "found": False,
                "message": f"No heatwave found with duration >= {min_duration} days and temperature >= {min_temp}°C"
            }

        longest_heatwave['found'] = True
        longest_heatwave['threshold_temp'] = min_temp
        longest_heatwave['temp_field'] = temp_field
        longest_heatwave['min_duration'] = min_duration

        return longest_heatwave

    # ========================================
    # Implement Abstract Methods from BaseFetcher
    # ========================================

    def fetch(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        data_type: str = "historical",
        start_date: str = "2024-01-01",
        end_date: str = "2024-12-31",
        forecast_days: int = 16,
        location_key: Optional[str] = None,
        **kwargs
    ) -> Tuple[List, Dict, str]:
        """Fetch weather data (generic method).

        Args:
            lat: Latitude
            lon: Longitude
            data_type: Type of data to fetch ('historical' or 'forecast')
            start_date: Start date for historical data
            end_date: End date for historical data
            forecast_days: Number of days for forecast
            location_key: Optional preset location identifier
            **kwargs: Additional parameters

        Returns:
            Tuple of (list of data, api_info dict, question string)
        """
        resolved_key = location_key or kwargs.get('location_key')

        if data_type == "historical":
            return self.fetch_historical_weather(
                lat=lat,
                lon=lon,
                start_date=start_date,
                end_date=end_date,
                include_metadata=kwargs.get('include_metadata', False),
                location_key=resolved_key
            )
        elif data_type == "forecast":
            return self.fetch_weather_forecast(
                lat=lat,
                lon=lon,
                forecast_days=forecast_days,
                include_metadata=kwargs.get('include_metadata', False),
                location_key=resolved_key
            )
        else:
            return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        """Return domain name for file naming.

        Args:
            **kwargs: Query parameters

        Returns:
            Domain name string for file naming
        """
        data_type = kwargs.get('data_type', 'weather')
        location_key = kwargs.get('location_key')

        if location_key:
            return f"openmeteo_{data_type}_{location_key}"

        lat = kwargs.get('lat', '')
        lon = kwargs.get('lon', '')

        return f"openmeteo_{data_type}_lat{lat}_lon{lon}"

    def get_metadata(self, **kwargs) -> Dict:
        """Return metadata about the query.

        Args:
            **kwargs: Query parameters

        Returns:
            Metadata dictionary
        """
        metadata = {
            "api": "Open-Meteo API",
            "requires_auth": False,
            "auth_type": "None - No API key required",
            "historical_data_range": "1940-present (80+ years)",
            "forecast_range": "16 days",
            "rate_limits": "None for reasonable use",
            "data_source": "ERA5 reanalysis (ECMWF), GFS, ICON, MeteoFrance"
        }

        location_key = kwargs.get('location_key')
        if location_key:
            metadata['location_key'] = location_key
            try:
                preset = self.get_preset_location(location_key)
                metadata['location_name'] = preset.get('name', location_key)
                metadata['latitude'] = preset['lat']
                metadata['longitude'] = preset['lon']
            except ValueError:
                metadata['location_name'] = location_key

        if 'lat' in kwargs:
            metadata['latitude'] = kwargs['lat']
        if 'lon' in kwargs:
            metadata['longitude'] = kwargs['lon']
        if 'data_type' in kwargs:
            metadata['data_type'] = kwargs['data_type']
        if 'start_date' in kwargs:
            metadata['start_date'] = kwargs['start_date']
        if 'end_date' in kwargs:
            metadata['end_date'] = kwargs['end_date']

        return metadata
