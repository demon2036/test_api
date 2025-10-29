"""
OpenWeatherMap API Test Runner

This module tests the OpenWeatherMapFetcher with various locations and weather queries.

Covers:
- Basic enumeration (historical weather, hourly forecast, daily forecast, alerts)
- All 3 advanced questions from GEMINI.md:
  1. Find all days in the last 30 days in city X where it rained and the wind speed exceeded 20 km/h
  2. List all rain-free windows (lasting at least 6 hours) for a farmer over the next week
  3. Query all active severe weather alerts within a 50km radius of a specific coordinate
- Additional weather filtering tests
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_runners.utils import save_result, create_test_result, print_header


def run(test_config=None):
    """Run OpenWeatherMap API tests

    Args:
        test_config: Optional configuration dictionary to override defaults
    """
    print_header("测试 OpenWeatherMap One Call API 3.0")

    from fetchers.openweathermap import OpenWeatherMapFetcher

    # Check if API key is available
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        print("\n⚠️  警告: 未找到 OPENWEATHERMAP_API_KEY 环境变量")
        print("请设置环境变量或在 .env 文件中添加:")
        print("OPENWEATHERMAP_API_KEY=your_api_key_here")
        print("\n可在以下网址获取免费API密钥: https://openweathermap.org/api")
        return []

    # Default configuration with test locations
    config = {
        "test_locations": [
            {"name": "纽约", "lat": 40.7128, "lon": -74.0060},
            {"name": "伦敦", "lat": 51.5074, "lon": -0.1278},
            {"name": "东京羽田机场", "location_key": "tokyo_haneda_airport"},
            {"name": "悉尼", "lat": -33.8688, "lon": 151.2093}
        ],
        "historical_days": 7,  # Reduced from 30 to save API calls
        "alert_radius_km": 50
    }

    # Merge user config if provided
    if test_config:
        config.update(test_config)

    try:
        fetcher = OpenWeatherMapFetcher(api_key=api_key)
    except ValueError as e:
        print(f"\n✗ 错误: {str(e)}")
        return []

    # Expand preset locations (e.g., airports) to concrete coordinates
    resolved_locations = []
    for location in config["test_locations"]:
        loc = dict(location)
        location_key = loc.get("location_key")
        if location_key:
            try:
                preset = OpenWeatherMapFetcher.get_preset_location(location_key)
            except ValueError as err:
                print(f"\n✗ 错误: 未知预设地点 {location_key}: {err}")
                return []

            loc.setdefault("name", preset.get("name", location_key))
            loc['lat'] = preset['lat']
            loc['lon'] = preset['lon']

        resolved_locations.append(loc)

    config["test_locations"] = resolved_locations

    all_results = []

    # ========================================
    # Part 1: Basic Enumeration Tests - Historical Weather
    # ========================================
    print("\n" + "-"*80)
    print("Part 1: 基本枚举测试（历史天气数据）")
    print("-"*80)

    test_location = config["test_locations"][0]  # Test with New York
    print(f"\n测试地点: {test_location['name']} ({test_location['lat']}, {test_location['lon']})")
    print(f"获取过去 {config['historical_days']} 天的历史天气数据...")

    try:
        historical_weather, api_info, question = fetcher.fetch_historical_weather(
            lat=test_location['lat'],
            lon=test_location['lon'],
            days_back=config['historical_days'],
            include_metadata=True
        )

        result = create_test_result(
            identifier=f"historical_{test_location['name']}",
            question=question,
            api_info=api_info,
            data=historical_weather,
            data_key="weather_data",
            location=test_location['name'],
            latitude=test_location['lat'],
            longitude=test_location['lon'],
            days_back=config['historical_days']
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(historical_weather)} 天的历史数据")

        # Show sample weather data
        if historical_weather:
            for i, weather in enumerate(historical_weather[:3], 1):
                date = weather.get('datetime', '')[:10]
                temp = weather.get('temp', 'N/A')
                humidity = weather.get('humidity', 'N/A')
                wind = weather.get('wind_speed', 'N/A')
                weather_desc = weather.get('weather', [{}])[0].get('description', 'N/A')
                print(f"    {i}. {date}")
                print(f"       温度: {temp}°C, 湿度: {humidity}%, 风速: {wind} m/s")
                print(f"       天气: {weather_desc}")

        time.sleep(2)  # Rate limiting

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 2: Advanced Question 1
    # "Find all days in the last 30 days where it rained and wind speed exceeded 20 km/h"
    # ========================================
    print("\n" + "-"*80)
    print("Part 2: 高级问题 1 - 过去7天中下雨且风速超过20 km/h的日期")
    print("-"*80)

    try:
        location = config["test_locations"][0]
        print(f"测试地点: {location['name']}")

        # We already have historical weather data from Part 1
        if 'historical_weather' in locals() and historical_weather:
            rainy_windy_days = fetcher.filter_rainy_and_windy_days(
                historical_weather,
                min_wind_speed=20  # km/h
            )

            result = create_test_result(
                identifier=f"rainy_windy_{location['name']}",
                question=f"枚举过去{config['historical_days']}天{location['name']}所有下雨且风速超过20 km/h的日期",
                api_info=api_info,
                data=rainy_windy_days,
                data_key="rainy_windy_days",
                location=location['name'],
                min_wind_speed_kmh=20,
                total_days_checked=len(historical_weather)
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(rainy_windy_days)} 天符合条件（下雨且风速>20 km/h）")

            # Show matching days
            for i, day in enumerate(rainy_windy_days, 1):
                date = day.get('datetime', '')[:10]
                temp = day.get('temp', 'N/A')
                wind_ms = day.get('wind_speed', 0)
                wind_kmh = wind_ms * 3.6
                rain = day.get('rain', {})
                rain_amount = rain.get('1h', 0) if isinstance(rain, dict) else rain
                weather_desc = day.get('weather', [{}])[0].get('description', 'N/A')

                print(f"    {i}. {date}")
                print(f"       温度: {temp}°C, 风速: {wind_kmh:.1f} km/h")
                print(f"       降雨量: {rain_amount} mm, 天气: {weather_desc}")

        else:
            print("  ⚠️  跳过：没有历史天气数据")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 3: Hourly Forecast
    # ========================================
    print("\n" + "-"*80)
    print("Part 3: 逐小时预报（未来48小时）")
    print("-"*80)

    try:
        location = config["test_locations"][0]
        print(f"测试地点: {location['name']}")

        hourly_forecast, api_info, question = fetcher.fetch_hourly_forecast(
            lat=location['lat'],
            lon=location['lon'],
            include_metadata=True
        )

        result = create_test_result(
            identifier=f"hourly_{location['name']}",
            question=question,
            api_info=api_info,
            data=hourly_forecast,
            data_key="hourly_forecast",
            location=location['name'],
            latitude=location['lat'],
            longitude=location['lon']
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(hourly_forecast)} 小时的预报数据")

        # Show sample forecast
        if hourly_forecast:
            for i, hour in enumerate(hourly_forecast[:5], 1):
                datetime_str = hour.get('datetime', '')
                temp = hour.get('temp', 'N/A')
                humidity = hour.get('humidity', 'N/A')
                pop = hour.get('pop', 0) * 100  # Convert to percentage
                weather_desc = hour.get('weather', [{}])[0].get('description', 'N/A')
                print(f"    {i}. {datetime_str}")
                print(f"       温度: {temp}°C, 湿度: {humidity}%, 降水概率: {pop:.0f}%")
                print(f"       天气: {weather_desc}")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 4: Advanced Question 2
    # "List all rain-free windows (lasting at least 6 hours) for spraying pesticides"
    # ========================================
    print("\n" + "-"*80)
    print("Part 4: 高级问题 2 - 未来48小时内持续至少6小时的无雨时段")
    print("-"*80)

    try:
        location = config["test_locations"][0]
        print(f"测试地点: {location['name']}")

        # We already have hourly forecast from Part 3
        if 'hourly_forecast' in locals() and hourly_forecast:
            rain_free_windows = fetcher.find_rain_free_windows(
                hourly_forecast,
                min_hours=6
            )

            result = create_test_result(
                identifier=f"rain_free_{location['name']}",
                question=f"枚举{location['name']}未来48小时所有持续至少6小时的无雨时段",
                api_info=api_info,
                data=rain_free_windows,
                data_key="rain_free_windows",
                location=location['name'],
                min_hours=6,
                total_hours_checked=len(hourly_forecast)
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(rain_free_windows)} 个无雨时段（持续≥6小时）")

            # Show rain-free windows
            for i, window in enumerate(rain_free_windows, 1):
                start = window.get('start_datetime', '')
                end = window.get('end_datetime', '')
                duration = window.get('duration_hours', 0)
                avg_temp = window.get('avg_temp', 0)
                avg_wind = window.get('avg_wind_speed', 0) * 3.6  # Convert to km/h
                avg_humidity = window.get('avg_humidity', 0)

                print(f"    {i}. 时段: {start} 至 {end}")
                print(f"       持续: {duration} 小时")
                print(f"       平均温度: {avg_temp:.1f}°C, 风速: {avg_wind:.1f} km/h, 湿度: {avg_humidity:.0f}%")

        else:
            print("  ⚠️  跳过：没有逐小时预报数据")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 5: Daily Forecast
    # ========================================
    print("\n" + "-"*80)
    print("Part 5: 每日预报（未来8天）")
    print("-"*80)

    try:
        location = config["test_locations"][1]  # Test with London
        print(f"测试地点: {location['name']}")

        daily_forecast, api_info, question = fetcher.fetch_daily_forecast(
            lat=location['lat'],
            lon=location['lon'],
            include_metadata=True
        )

        result = create_test_result(
            identifier=f"daily_{location['name']}",
            question=question,
            api_info=api_info,
            data=daily_forecast,
            data_key="daily_forecast",
            location=location['name'],
            latitude=location['lat'],
            longitude=location['lon']
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(daily_forecast)} 天的预报数据")

        # Show sample forecast
        if daily_forecast:
            for i, day in enumerate(daily_forecast[:5], 1):
                date = day.get('datetime', '')[:10]
                temp_min = day.get('temp_min', 'N/A')
                temp_max = day.get('temp_max', 'N/A')
                pop = day.get('pop', 0) * 100
                weather_desc = day.get('weather', [{}])[0].get('description', 'N/A')
                print(f"    {i}. {date}")
                print(f"       温度: {temp_min}°C - {temp_max}°C, 降水概率: {pop:.0f}%")
                print(f"       天气: {weather_desc}")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 6: Advanced Question 3
    # "Query all active severe weather alerts within a 50km radius"
    # ========================================
    print("\n" + "-"*80)
    print("Part 6: 高级问题 3 - 查询50km半径内的所有活跃天气警报")
    print("-"*80)

    try:
        # Test with different locations to find alerts
        for location in config["test_locations"][:2]:
            print(f"\n测试地点: {location['name']}")

            alerts = fetcher.filter_alerts_by_radius(
                center_lat=location['lat'],
                center_lon=location['lon'],
                radius_km=config['alert_radius_km'],
                sample_points=4  # Reduced to save API calls
            )

            result = create_test_result(
                identifier=f"alerts_{location['name']}",
                question=f"枚举{location['name']}周围{config['alert_radius_km']}km半径内的所有活跃天气警报",
                api_info={
                    "api_endpoint": fetcher.BASE_URL,
                    "method": "GET",
                    "sample_points": 4,
                    "radius_km": config['alert_radius_km']
                },
                data=alerts,
                data_key="weather_alerts",
                location=location['name'],
                latitude=location['lat'],
                longitude=location['lon'],
                radius_km=config['alert_radius_km']
            )

            all_results.append(result)

            if alerts:
                print(f"  ✓ 找到 {len(alerts)} 个活跃警报")

                for i, alert in enumerate(alerts, 1):
                    event = alert.get('event', 'Unknown')
                    sender = alert.get('sender_name', 'Unknown')
                    start = alert.get('start_datetime', '')[:16]
                    end = alert.get('end_datetime', '')[:16]
                    print(f"    {i}. {event}")
                    print(f"       发布: {sender}")
                    print(f"       时段: {start} 至 {end}")
            else:
                print(f"  ✓ 当前无活跃警报（这是好消息！）")

            time.sleep(3)  # Longer delay due to multiple API calls

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 7: Additional Filtering Tests
    # ========================================
    print("\n" + "-"*80)
    print("Part 7: 其他过滤测试")
    print("-"*80)

    # Test 7.1: Temperature filtering
    print("\n7.1 温度过滤（高温天气）")
    try:
        if 'historical_weather' in locals() and historical_weather:
            location = config["test_locations"][0]
            hot_days = fetcher.filter_by_temperature(
                historical_weather,
                min_temp=25  # Days with temp > 25°C
            )

            result = create_test_result(
                identifier=f"hot_days_{location['name']}",
                question=f"枚举{location['name']}过去{config['historical_days']}天所有温度超过25°C的日期",
                api_info=api_info,
                data=hot_days,
                data_key="hot_days",
                location=location['name'],
                min_temp=25,
                total_days_checked=len(historical_weather)
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(hot_days)} 天温度超过25°C（共 {len(historical_weather)} 天）")

            for i, day in enumerate(hot_days[:3], 1):
                date = day.get('datetime', '')[:10]
                temp = day.get('temp', 'N/A')
                print(f"    {i}. {date}: {temp}°C")

        else:
            print("  ⚠️  跳过：没有历史天气数据")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # Test 7.2: Humidity filtering
    print("\n7.2 湿度过滤（高湿度天气）")
    try:
        if 'historical_weather' in locals() and historical_weather:
            location = config["test_locations"][0]
            humid_days = fetcher.filter_by_humidity(
                historical_weather,
                min_humidity=80  # Days with humidity > 80%
            )

            result = create_test_result(
                identifier=f"humid_days_{location['name']}",
                question=f"枚举{location['name']}过去{config['historical_days']}天所有湿度超过80%的日期",
                api_info=api_info,
                data=humid_days,
                data_key="humid_days",
                location=location['name'],
                min_humidity=80,
                total_days_checked=len(historical_weather)
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(humid_days)} 天湿度超过80%（共 {len(historical_weather)} 天）")

            for i, day in enumerate(humid_days[:3], 1):
                date = day.get('datetime', '')[:10]
                humidity = day.get('humidity', 'N/A')
                print(f"    {i}. {date}: {humidity}%")

        else:
            print("  ⚠️  跳过：没有历史天气数据")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 8: Preset Location Test - Tokyo Haneda Airport
    # ========================================
    print("\n" + "-"*80)
    print("Part 8: 预设地点测试（东京羽田机场）")
    print("-"*80)

    try:
        haneda_location = next(
            (loc for loc in config["test_locations"] if loc.get("location_key") == "tokyo_haneda_airport"),
            None
        )

        if not haneda_location:
            preset = OpenWeatherMapFetcher.get_preset_location("tokyo_haneda_airport")
            haneda_location = {
                "name": preset.get("name", "东京羽田机场"),
                "lat": preset["lat"],
                "lon": preset["lon"],
                "location_key": "tokyo_haneda_airport"
            }

        location_name = haneda_location.get("name", "东京羽田机场")
        print(f"测试地点: {location_name} ({haneda_location['lat']}, {haneda_location['lon']})")

        haneda_hourly_forecast, haneda_api_info, haneda_question = fetcher.fetch_hourly_forecast(
            location_key="tokyo_haneda_airport",
            include_metadata=True
        )

        result = create_test_result(
            identifier="hourly_tokyo_haneda_airport",
            question=haneda_question,
            api_info=haneda_api_info,
            data=haneda_hourly_forecast,
            data_key="hourly_forecast",
            location=location_name,
            location_key="tokyo_haneda_airport"
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(haneda_hourly_forecast)} 小时的预报数据（预设地点）")

        if haneda_hourly_forecast:
            first_entry = haneda_hourly_forecast[0]
            print(
                "    示例: {dt}, 温度 {temp}°C, 湿度 {humidity}%".format(
                    dt=first_entry.get('datetime', 'N/A'),
                    temp=first_entry.get('temp', 'N/A'),
                    humidity=first_entry.get('humidity', 'N/A')
                )
            )

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Save All Results
    # ========================================
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)

    summary = {
        "api_name": "OpenWeatherMap One Call API 3.0",
        "requires_auth": True,
        "auth_type": "API Key",
        "config": config,
        "total_tests": len(all_results),
        "tests": all_results
    }

    save_result("openweathermap", summary)

    print(f"\n总测试数: {len(all_results)}")
    print("所有测试已完成！")
    print(f"\n注意: 本次测试使用了约 {len(all_results) * 2} 个API调用")
    print("免费套餐限制: 1000 次调用/天")

    return all_results


if __name__ == "__main__":
    run()
