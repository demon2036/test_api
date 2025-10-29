"""
OpenWeatherMap API Fetcher

This module provides functionality to enumerate weather data using the OpenWeatherMap One Call API 3.0.

Key Features:
- Enumerate historical weather data (from 1979 to 4 days ahead)
- Enumerate hourly and daily forecasts
- Enumerate weather alerts for a location
- Advanced filtering: rainy+windy days, rain-free windows, alert filtering
- Requires API key (1000 free calls/day)

Example Usage:
    fetcher = OpenWeatherMapFetcher(api_key="your_api_key")

    # Get historical weather data for last 30 days
    weather_data, api_info, question = fetcher.fetch_historical_weather(
        lat=40.7128,
        lon=-74.0060,
        days_back=30
    )

    # Filter rainy and windy days
    rainy_windy = fetcher.filter_rainy_and_windy_days(
        weather_data,
        min_wind_speed=20  # km/h
    )

    # Find rain-free windows in forecast
    forecast, _, _ = fetcher.fetch_hourly_forecast(lat=40.7128, lon=-74.0060)
    rain_free = fetcher.find_rain_free_windows(forecast, min_hours=6)
"""

import os
import time
import requests
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta

from .base import BaseFetcher


class OpenWeatherMapFetcher(BaseFetcher):
    """Fetcher for OpenWeatherMap One Call API 3.0"""

    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
    PRESET_LOCATIONS = {
        "tokyo_haneda_airport": {
            "name": "东京羽田机场",
            "lat": 35.5494,
            "lon": 139.7798
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenWeatherMap fetcher.

        Args:
            api_key: OpenWeatherMap API key. If not provided, will try to read from
                    OPENWEATHERMAP_API_KEY environment variable.

        Raises:
            ValueError: If no API key is provided or found in environment
        """
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenWeatherMap API key is required. "
                "Provide it as a parameter or set OPENWEATHERMAP_API_KEY environment variable."
            )

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to the OpenWeatherMap API.

        Args:
            endpoint: API endpoint (e.g., 'timemachine', 'day_summary')
            params: Query parameters

        Returns:
            JSON response from the API

        Raises:
            requests.RequestException: If the API request fails
        """
        if params is None:
            params = {}

        # Add API key to all requests
        params['appid'] = self.api_key

        # Default to metric units
        if 'units' not in params:
            params['units'] = 'metric'

        url = f"{self.BASE_URL}/{endpoint}" if endpoint else self.BASE_URL

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenWeatherMap API request failed: {str(e)}")

    def _format_weather_data(
        self,
        data: Dict,
        timestamp: Optional[int] = None,
        include_metadata: bool = False
    ) -> Any:
        """Format weather data for output.

        Args:
            data: Raw weather data from API
            timestamp: Unix timestamp for this data point
            include_metadata: Whether to include full metadata

        Returns:
            Formatted weather data (timestamp or dict with metadata)
        """
        if not include_metadata:
            return timestamp or data.get('dt', '')

        # Extract relevant weather information
        result = {
            "timestamp": timestamp or data.get('dt'),
            "datetime": datetime.fromtimestamp(timestamp or data.get('dt')).isoformat(),
            "temp": data.get('temp'),
            "feels_like": data.get('feels_like'),
            "pressure": data.get('pressure'),
            "humidity": data.get('humidity'),
            "dew_point": data.get('dew_point'),
            "clouds": data.get('clouds'),
            "visibility": data.get('visibility'),
            "wind_speed": data.get('wind_speed'),
            "wind_deg": data.get('wind_deg'),
            "wind_gust": data.get('wind_gust'),
            "weather": data.get('weather', []),
            "rain": data.get('rain', {}),
            "snow": data.get('snow', {})
        }

        return result

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
        coords = f"({lat}, {lon})"
        return f"{location_name} {coords}" if location_name else coords

    def fetch_historical_weather(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        days_back: int = 30,
        include_metadata: bool = True,
        location_key: Optional[str] = None
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch historical weather data for the last N days.

        This uses the timemachine endpoint to retrieve hourly historical data.

        Args:
            lat: Latitude (-90 to 90). Optional if location_key is provided.
            lon: Longitude (-180 to 180). Optional if location_key is provided.
            days_back: Number of days to look back (default: 30)
            include_metadata: Whether to include full weather metadata
            location_key: Optional preset location identifier

        Returns:
            Tuple of (list of weather data, api_info dict, question string)
        """
        lat, lon, location_name, resolved_key = self._resolve_coordinates(lat, lon, location_key)
        location_label = self._format_location_label(lat, lon, location_name)

        weather_data = []
        current_time = datetime.now()

        # Fetch data for each day
        for days_ago in range(days_back, 0, -1):
            target_date = current_time - timedelta(days=days_ago)
            timestamp = int(target_date.timestamp())

            params = {
                'lat': lat,
                'lon': lon,
                'dt': timestamp
            }

            try:
                data = self._make_request('timemachine', params)

                # timemachine returns data for a single timestamp
                if 'data' in data and len(data['data']) > 0:
                    formatted = self._format_weather_data(
                        data['data'][0],
                        timestamp,
                        include_metadata
                    )
                    weather_data.append(formatted)

                # Rate limiting: wait a bit between requests
                time.sleep(0.1)

            except Exception as e:
                print(f"Warning: Failed to fetch data for {target_date.date()}: {str(e)}")
                continue

        question = f"枚举过去 {days_back} 天在{location_label}的历史天气数据"

        api_info = {
            "api_endpoint": f"{self.BASE_URL}/timemachine",
            "method": "GET",
            "parameters": {
                "lat": lat,
                "lon": lon,
                "dt": "Unix timestamp for each day",
                "units": "metric"
            },
            "authentication": "API Key (appid parameter)",
            "rate_limit": "1000 free calls/day, then paid",
            "documentation": "https://openweathermap.org/api/one-call-3",
            "total_found": len(weather_data),
            "days_requested": days_back
        }

        if resolved_key:
            api_info["parameters"]["location_key"] = resolved_key
            api_info["location_name"] = location_name

        return weather_data, api_info, question

    def fetch_hourly_forecast(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        include_metadata: bool = True,
        location_key: Optional[str] = None
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch hourly weather forecast for the next 48 hours.

        Args:
            lat: Latitude (-90 to 90). Optional if location_key is provided.
            lon: Longitude (-180 to 180). Optional if location_key is provided.
            include_metadata: Whether to include full weather metadata
            location_key: Optional preset location identifier

        Returns:
            Tuple of (list of hourly forecasts, api_info dict, question string)
        """
        lat, lon, location_name, resolved_key = self._resolve_coordinates(lat, lon, location_key)
        location_label = self._format_location_label(lat, lon, location_name)

        params = {
            'lat': lat,
            'lon': lon,
            'exclude': 'current,minutely,daily,alerts'
        }

        data = self._make_request('', params)  # Base endpoint for current/forecast

        hourly_data = data.get('hourly', [])
        formatted = [
            self._format_weather_data(hour, hour.get('dt'), include_metadata)
            for hour in hourly_data
        ]

        question = f"枚举{location_label}未来 48 小时的逐小时天气预报"

        api_info = {
            "api_endpoint": self.BASE_URL,
            "method": "GET",
            "parameters": {
                "lat": lat,
                "lon": lon,
                "exclude": "current,minutely,daily,alerts",
                "units": "metric"
            },
            "authentication": "API Key (appid parameter)",
            "rate_limit": "1000 free calls/day, then paid",
            "documentation": "https://openweathermap.org/api/one-call-3",
            "total_found": len(formatted)
        }

        if resolved_key:
            api_info["parameters"]["location_key"] = resolved_key
            api_info["location_name"] = location_name

        return formatted, api_info, question

    def fetch_daily_forecast(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        include_metadata: bool = True,
        location_key: Optional[str] = None
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch daily weather forecast for the next 8 days.

        Args:
            lat: Latitude (-90 to 90). Optional if location_key is provided.
            lon: Longitude (-180 to 180). Optional if location_key is provided.
            include_metadata: Whether to include full weather metadata
            location_key: Optional preset location identifier

        Returns:
            Tuple of (list of daily forecasts, api_info dict, question string)
        """
        lat, lon, location_name, resolved_key = self._resolve_coordinates(lat, lon, location_key)
        location_label = self._format_location_label(lat, lon, location_name)

        params = {
            'lat': lat,
            'lon': lon,
            'exclude': 'current,minutely,hourly,alerts'
        }

        data = self._make_request('', params)

        daily_data = data.get('daily', [])

        if not include_metadata:
            formatted = [day.get('dt') for day in daily_data]
        else:
            formatted = []
            for day in daily_data:
                formatted.append({
                    "timestamp": day.get('dt'),
                    "datetime": datetime.fromtimestamp(day.get('dt')).isoformat(),
                    "temp_min": day.get('temp', {}).get('min'),
                    "temp_max": day.get('temp', {}).get('max'),
                    "temp_day": day.get('temp', {}).get('day'),
                    "temp_night": day.get('temp', {}).get('night'),
                    "pressure": day.get('pressure'),
                    "humidity": day.get('humidity'),
                    "wind_speed": day.get('wind_speed'),
                    "wind_deg": day.get('wind_deg'),
                    "wind_gust": day.get('wind_gust'),
                    "clouds": day.get('clouds'),
                    "pop": day.get('pop'),  # Probability of precipitation
                    "rain": day.get('rain'),
                    "snow": day.get('snow'),
                    "weather": day.get('weather', []),
                    "uvi": day.get('uvi')  # UV index
                })

        question = f"枚举{location_label}未来 8 天的每日天气预报"

        api_info = {
            "api_endpoint": self.BASE_URL,
            "method": "GET",
            "parameters": {
                "lat": lat,
                "lon": lon,
                "exclude": "current,minutely,hourly,alerts",
                "units": "metric"
            },
            "authentication": "API Key (appid parameter)",
            "rate_limit": "1000 free calls/day, then paid",
            "documentation": "https://openweathermap.org/api/one-call-3",
            "total_found": len(formatted)
        }

        if resolved_key:
            api_info["parameters"]["location_key"] = resolved_key
            api_info["location_name"] = location_name

        return formatted, api_info, question

    def fetch_weather_alerts(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        include_metadata: bool = True,
        location_key: Optional[str] = None
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch active weather alerts for a location.

        Args:
            lat: Latitude (-90 to 90). Optional if location_key is provided.
            lon: Longitude (-180 to 180). Optional if location_key is provided.
            include_metadata: Whether to include full alert metadata
            location_key: Optional preset location identifier

        Returns:
            Tuple of (list of alerts, api_info dict, question string)
        """
        lat, lon, location_name, resolved_key = self._resolve_coordinates(lat, lon, location_key)
        location_label = self._format_location_label(lat, lon, location_name)

        params = {
            'lat': lat,
            'lon': lon,
            'exclude': 'current,minutely,hourly,daily'
        }

        data = self._make_request('', params)

        alerts = data.get('alerts', [])

        if not include_metadata:
            formatted = [alert.get('event', '') for alert in alerts]
        else:
            formatted = []
            for alert in alerts:
                formatted.append({
                    "sender_name": alert.get('sender_name'),
                    "event": alert.get('event'),
                    "start": alert.get('start'),
                    "start_datetime": datetime.fromtimestamp(alert.get('start')).isoformat(),
                    "end": alert.get('end'),
                    "end_datetime": datetime.fromtimestamp(alert.get('end')).isoformat(),
                    "description": alert.get('description'),
                    "tags": alert.get('tags', [])
                })

        question = f"枚举{location_label}的所有活跃天气警报"

        api_info = {
            "api_endpoint": self.BASE_URL,
            "method": "GET",
            "parameters": {
                "lat": lat,
                "lon": lon,
                "exclude": "current,minutely,hourly,daily",
                "units": "metric"
            },
            "authentication": "API Key (appid parameter)",
            "rate_limit": "1000 free calls/day, then paid",
            "documentation": "https://openweathermap.org/api/one-call-3",
            "total_found": len(formatted)
        }

        if resolved_key:
            api_info["parameters"]["location_key"] = resolved_key
            api_info["location_name"] = location_name

        return formatted, api_info, question

    # Advanced filter methods

    def filter_rainy_and_windy_days(
        self,
        weather_data: List[Dict],
        min_wind_speed: float = 20.0
    ) -> List[Dict]:
        """Filter days where it rained AND wind speed exceeded threshold.

        This answers the advanced question:
        "Find all days in the last 30 days in city X where it rained and
        the wind speed exceeded 20 km/h."

        Args:
            weather_data: List of weather data with metadata
            min_wind_speed: Minimum wind speed in km/h (default: 20)

        Returns:
            Filtered list of weather data
        """
        # Convert km/h to m/s (API returns m/s)
        min_wind_speed_ms = min_wind_speed / 3.6

        filtered = []
        for data in weather_data:
            # Check if it rained
            has_rain = False
            rain_data = data.get('rain')
            if rain_data:
                # rain can be a dict with '1h' key or a number
                if isinstance(rain_data, dict):
                    has_rain = rain_data.get('1h', 0) > 0
                else:
                    has_rain = rain_data > 0

            # Also check weather description
            if not has_rain:
                weather_list = data.get('weather', [])
                for w in weather_list:
                    if 'rain' in w.get('main', '').lower() or 'rain' in w.get('description', '').lower():
                        has_rain = True
                        break

            # Check wind speed
            wind_speed = data.get('wind_speed', 0)

            if has_rain and wind_speed >= min_wind_speed_ms:
                filtered.append(data)

        return filtered

    def find_rain_free_windows(
        self,
        hourly_forecast: List[Dict],
        min_hours: int = 6
    ) -> List[Dict]:
        """Find continuous rain-free windows of at least N hours.

        This answers the advanced question:
        "List all rain-free windows (lasting at least 6 hours) for a farmer
        over the next week for spraying pesticides."

        Args:
            hourly_forecast: List of hourly forecast data with metadata
            min_hours: Minimum duration of rain-free window in hours (default: 6)

        Returns:
            List of rain-free windows with start/end times and duration
        """
        windows = []
        current_window_start = None
        current_window_hours = []

        for i, hour_data in enumerate(hourly_forecast):
            # Check if this hour has rain
            has_rain = False

            # Check rain data
            rain_data = hour_data.get('rain')
            if rain_data:
                if isinstance(rain_data, dict):
                    has_rain = rain_data.get('1h', 0) > 0
                else:
                    has_rain = rain_data > 0

            # Check probability of precipitation
            pop = hour_data.get('pop', 0)
            if pop > 0.3:  # More than 30% chance of rain
                has_rain = True

            # Check weather description
            if not has_rain:
                weather_list = hour_data.get('weather', [])
                for w in weather_list:
                    if 'rain' in w.get('main', '').lower():
                        has_rain = True
                        break

            if not has_rain:
                # Rain-free hour
                if current_window_start is None:
                    current_window_start = i
                    current_window_hours = [hour_data]
                else:
                    current_window_hours.append(hour_data)
            else:
                # Rain detected - check if we have a window to save
                if current_window_start is not None:
                    duration = len(current_window_hours)
                    if duration >= min_hours:
                        windows.append({
                            "start_index": current_window_start,
                            "start_datetime": current_window_hours[0]['datetime'],
                            "end_datetime": current_window_hours[-1]['datetime'],
                            "duration_hours": duration,
                            "avg_temp": sum(h.get('temp', 0) for h in current_window_hours) / duration,
                            "avg_wind_speed": sum(h.get('wind_speed', 0) for h in current_window_hours) / duration,
                            "avg_humidity": sum(h.get('humidity', 0) for h in current_window_hours) / duration
                        })
                    # Reset window
                    current_window_start = None
                    current_window_hours = []

        # Check final window
        if current_window_start is not None:
            duration = len(current_window_hours)
            if duration >= min_hours:
                windows.append({
                    "start_index": current_window_start,
                    "start_datetime": current_window_hours[0]['datetime'],
                    "end_datetime": current_window_hours[-1]['datetime'],
                    "duration_hours": duration,
                    "avg_temp": sum(h.get('temp', 0) for h in current_window_hours) / duration,
                    "avg_wind_speed": sum(h.get('wind_speed', 0) for h in current_window_hours) / duration,
                    "avg_humidity": sum(h.get('humidity', 0) for h in current_window_hours) / duration
                })

        return windows

    def filter_alerts_by_radius(
        self,
        center_lat: Optional[float] = None,
        center_lon: Optional[float] = None,
        radius_km: float = 50,
        sample_points: int = 8,
        center_location_key: Optional[str] = None
    ) -> List[Dict]:
        """Query all active severe weather alerts within a radius.

        This answers the advanced question:
        "Query all active severe weather alerts within a 50km radius
        of a specific coordinate."

        Note: Since OpenWeatherMap's alert API is location-specific,
        this method samples multiple points around the center to find alerts.

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers (default: 50)
            sample_points: Number of points to sample around the circle

        Returns:
            List of unique alerts found within the radius
        """
        import math

        alerts_map = {}  # Use dict to deduplicate alerts

        if center_location_key:
            preset = self.get_preset_location(center_location_key)
            if center_lat is None:
                center_lat = preset['lat']
            if center_lon is None:
                center_lon = preset['lon']

        if center_lat is None or center_lon is None:
            raise ValueError(
                "center_lat and center_lon are required unless center_location_key provides a preset."
            )

        # Sample points around the circle
        # Convert radius to degrees (approximate)
        radius_deg = radius_km / 111.0  # 1 degree ≈ 111 km

        # Check center point
        try:
            center_alerts, _, _ = self.fetch_weather_alerts(
                lat=center_lat,
                lon=center_lon,
                include_metadata=True
            )
            for alert in center_alerts:
                key = f"{alert['event']}_{alert['start']}_{alert['end']}"
                alerts_map[key] = alert
        except:
            pass

        # Check points around the circle
        for i in range(sample_points):
            angle = 2 * math.pi * i / sample_points
            lat = center_lat + radius_deg * math.sin(angle)
            lon = center_lon + radius_deg * math.cos(angle) / math.cos(math.radians(center_lat))

            # Ensure coordinates are valid
            lat = max(-90, min(90, lat))
            lon = ((lon + 180) % 360) - 180  # Normalize to -180 to 180

            try:
                alerts, _, _ = self.fetch_weather_alerts(
                    lat=lat,
                    lon=lon,
                    include_metadata=True
                )
                for alert in alerts:
                    key = f"{alert['event']}_{alert['start']}_{alert['end']}"
                    if key not in alerts_map:
                        alerts_map[key] = alert

                # Rate limiting
                time.sleep(0.2)
            except:
                continue

        return list(alerts_map.values())

    def filter_by_temperature(
        self,
        weather_data: List[Dict],
        min_temp: Optional[float] = None,
        max_temp: Optional[float] = None
    ) -> List[Dict]:
        """Filter weather data by temperature range.

        Args:
            weather_data: List of weather data with metadata
            min_temp: Minimum temperature in Celsius
            max_temp: Maximum temperature in Celsius

        Returns:
            Filtered list of weather data
        """
        filtered = []
        for data in weather_data:
            temp = data.get('temp')
            if temp is None:
                continue

            if min_temp is not None and temp < min_temp:
                continue
            if max_temp is not None and temp > max_temp:
                continue

            filtered.append(data)

        return filtered

    def filter_by_humidity(
        self,
        weather_data: List[Dict],
        min_humidity: Optional[int] = None,
        max_humidity: Optional[int] = None
    ) -> List[Dict]:
        """Filter weather data by humidity percentage.

        Args:
            weather_data: List of weather data with metadata
            min_humidity: Minimum humidity percentage
            max_humidity: Maximum humidity percentage

        Returns:
            Filtered list of weather data
        """
        filtered = []
        for data in weather_data:
            humidity = data.get('humidity')
            if humidity is None:
                continue

            if min_humidity is not None and humidity < min_humidity:
                continue
            if max_humidity is not None and humidity > max_humidity:
                continue

            filtered.append(data)

        return filtered

    # Implement abstract methods

    def fetch(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        data_type: str = "historical",
        days_back: int = 30,
        location_key: Optional[str] = None,
        **kwargs
    ) -> Tuple[List, Dict, str]:
        """Fetch weather data (generic method).

        Args:
            lat: Latitude
            lon: Longitude
            data_type: Type of data to fetch ('historical', 'hourly', 'daily', 'alerts')
            days_back: Number of days for historical data
            **kwargs: Additional parameters

        Returns:
            Tuple of (list of data, api_info dict, question string)
        """
        resolved_key = location_key or kwargs.get('location_key')

        if data_type == "historical":
            return self.fetch_historical_weather(
                lat=lat,
                lon=lon,
                days_back=days_back,
                include_metadata=False,
                location_key=resolved_key
            )
        elif data_type == "hourly":
            return self.fetch_hourly_forecast(
                lat=lat,
                lon=lon,
                include_metadata=False,
                location_key=resolved_key
            )
        elif data_type == "daily":
            return self.fetch_daily_forecast(
                lat=lat,
                lon=lon,
                include_metadata=False,
                location_key=resolved_key
            )
        elif data_type == "alerts":
            return self.fetch_weather_alerts(
                lat=lat,
                lon=lon,
                include_metadata=False,
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
            return f"openweathermap_{data_type}_{location_key}"

        lat = kwargs.get('lat', '')
        lon = kwargs.get('lon', '')

        return f"openweathermap_{data_type}_lat{lat}_lon{lon}"

    def get_metadata(self, **kwargs) -> Dict:
        """Return metadata about the query.

        Args:
            **kwargs: Query parameters

        Returns:
            Metadata dictionary
        """
        metadata = {
            "api": "OpenWeatherMap One Call API 3.0",
            "requires_auth": True,
            "auth_type": "API Key"
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

        return metadata
