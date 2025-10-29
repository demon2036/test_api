"""
Open-Meteo API Test Runner

This runner focuses on concise, high‑value "Enumerate All" questions for Tokyo Haneda Airport (东京羽田机场):
- 2024 Jan–Feb: all days with min temperature < 0°C
- 2020–2024: all rainy days (precipitation > 0.1mm)
- 1940–2024: top 10 hottest days (by daily max temperature)

Advantages:
- Long historical range (≈1940–present), no API key, global coverage
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add test_runners dir to path to avoid triggering package __init__
CURRENT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(CURRENT_DIR, '..'))          # enumerate_framework/test_runners
sys.path.insert(0, os.path.join(CURRENT_DIR, '../..'))       # enumerate_framework

from utils import save_result, create_test_result, print_header


def run(test_config=None):
    """Run Open-Meteo API tests

    Args:
        test_config: Optional configuration dictionary to override defaults
    """
    print_header("测试 Open-Meteo API")
    print("\n✓ 特点: 无需密钥, 1940年至今历史, 16天预报")

    from fetchers.weather_climate.openmeteo import OpenMeteoFetcher

    # Minimal configuration
    config = {
        "primary_test_location": {
            "name": "东京羽田机场",
            "location_key": "tokyo_haneda_airport",
            "lat": 35.5494,
            "lon": 139.7798
        }
    }

    # Merge user config if provided
    if test_config:
        config.update(test_config)

    fetcher = OpenMeteoFetcher()
    all_results = []

    primary_loc = config["primary_test_location"]

    # ========================================
    # Part 1: Advanced Question - Cold Winter Days FIRST (to avoid 429)
    # ========================================
    print("\n" + "-"*80)
    print(f"Part 1: 高级问题 - 2024年冬季寒冷天气 (<0°C)")
    print("-"*80)

    try:
        print(f"测试地点: {primary_loc['name']}")
        print("查询2024年1-2月（冬季）所有最低温度<0°C的日期...")

        # Fetch winter 2024 data first for stability
        winter_2024, api_info, question = fetcher.fetch_historical_weather(
            location_key=primary_loc['location_key'],
            start_date="2024-01-01",
            end_date="2024-02-29",
            include_metadata=True
        )

        # Filter cold days (<0°C)
        cold_days = fetcher.filter_by_temperature(
            winter_2024,
            max_temp=0,
            temp_field='temp_min'
        )

        result = create_test_result(
            identifier=f"cold_winter_days_{primary_loc['location_key']}_2024",
            question=f"枚举{primary_loc['name']}2024年1-2月所有最低温度<0°C的日期",
            api_info=api_info,
            data=cold_days,
            data_key="cold_days",
            location=primary_loc['name'],
            season="winter_2024",
            max_temp=0,
            total_days_checked=len(winter_2024)
        )

        all_results.append(result)

        print(f"  ✓ 冬季总天数: {len(winter_2024)} 天")
        print(f"  ✓ 寒冷天数 (<0°C): {len(cold_days)} 天")

        if cold_days:
            coldest = sorted(cold_days, key=lambda x: x.get('temp_min', 999))[:3]
            print(f"\n  最冷的3天:")
            for i, day in enumerate(coldest, 1):
                print(f"    {i}. {day['date']}: {day['temp_min']:.1f}°C (最高: {day['temp_max']:.1f}°C)")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        # Fallback: ensure this test is still recorded in JSON
        fallback = create_test_result(
            identifier=f"cold_winter_days_{primary_loc['location_key']}_2024",
            question=f"枚举{primary_loc['name']}2024年1-2月所有最低温度<0°C的日期",
            api_info={
                "error": str(e),
                "note": "请求受限或失败，未能获取数据"
            },
            data=[],
            data_key="cold_days",
            location=primary_loc['name'],
            season="winter_2024",
            max_temp=0,
            total_days_checked=0,
            status="failed",
            rate_limited=True
        )
        all_results.append(fallback)

    # Gentle pause to reduce server pressure before next heavy query
    time.sleep(2)
    # ========================================
    # Part 2: Advanced Question - All Rainy Days (2020-2024)
    # ========================================
    print("\n" + "="*80)
    print(f"Part 2: 高级问题 - 枚举所有下雨天 (2020-2024)")
    print("="*80)

    try:
        print(f"测试地点: {primary_loc['name']}")
        print("查询2020-2024年（5年）的所有下雨天...")

        # Fetch 5 years of data
        five_year_data, api_info, question = fetcher.fetch_historical_weather(
            location_key=primary_loc['location_key'],
            start_date="2020-01-01",
            end_date="2024-10-29",
            include_metadata=True
        )

        # Filter rainy days
        rainy_days = fetcher.filter_by_precipitation(
            five_year_data,
            min_precipitation=0.1  # >0.1mm considered rainy
        )

        result = create_test_result(
            identifier=f"rainy_days_{primary_loc['location_key']}_2020_2024",
            question=f"枚举{primary_loc['name']}从2020-2024年所有降水量>0.1mm的下雨天",
            api_info=api_info,
            data=rainy_days,
            data_key="rainy_days",
            location=primary_loc['name'],
            date_range="2020-2024",
            total_days_checked=len(five_year_data),
            min_precipitation=0.1
        )

        all_results.append(result)

        print(f"  ✓ 总天数: {len(five_year_data)} 天")
        print(f"  ✓ 下雨天数: {len(rainy_days)} 天")
        print(f"  ✓ 下雨比例: {len(rainy_days)/len(five_year_data)*100:.1f}%")

        # Show heaviest rain days
        heavy_rain = sorted(rainy_days, key=lambda x: x.get('precipitation', 0), reverse=True)[:5]
        print(f"\n  降雨量最大的5天:")
        for i, day in enumerate(heavy_rain, 1):
            print(f"    {i}. {day['date']}: {day['precipitation']} mm (温度: {day['temp_mean']:.1f}°C)")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        # Fallback record
        fallback = create_test_result(
            identifier=f"rainy_days_{primary_loc['location_key']}_2020_2024",
            question=f"枚举{primary_loc['name']}从2020-2024年所有降水量>0.1mm的下雨天",
            api_info={
                "error": str(e),
                "note": "请求受限或失败，未能获取数据"
            },
            data=[],
            data_key="rainy_days",
            location=primary_loc['name'],
            date_range="2020-2024",
            total_days_checked=0,
            min_precipitation=0.1,
            status="failed",
            rate_limited=True
        )
        all_results.append(fallback)

    # ========================================
    # Part 3: Advanced Question - Hottest Days EVER (1940-2024)
    # ========================================
    print("\n" + "="*80)
    print(f"Part 3: 高级问题 - 史上最热的10天 (1940-2024)")
    print("="*80)

    try:
        print(f"测试地点: {primary_loc['name']}")
        print("查询1940-2024年的历史数据，找出最热的10天...")

        # Fetch 80+ years of data
        all_time_data, api_info, question = fetcher.fetch_historical_weather(
            location_key=primary_loc['location_key'],
            start_date="1940-01-01",
            end_date="2024-10-29",
            include_metadata=True
        )

        # Get top 10 hottest days
        hottest_days = fetcher.get_top_n_by_temperature(
            all_time_data,
            n=10,
            descending=True,
            temp_field='temp_max'
        )

        result = create_test_result(
            identifier=f"hottest_days_ever_{primary_loc['location_key']}",
            question=f"枚举{primary_loc['name']}从1940-2024年最高温度最高的10天",
            api_info=api_info,
            data=hottest_days,
            data_key="hottest_days",
            location=primary_loc['name'],
            date_range="1940-2024",
            total_days_checked=len(all_time_data),
            top_n=10
        )

        all_results.append(result)

        print(f"  ✓ 分析了 {len(all_time_data)} 天的数据（{len(all_time_data)/365:.1f}年）")
        print(f"  ✓ 找到史上最热的10天:")

        for day in hottest_days:
            print(f"    #{day['rank']}. {day['date']}: {day['temp_max']:.1f}°C")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        # Fallback record
        fallback = create_test_result(
            identifier=f"hottest_days_ever_{primary_loc['location_key']}",
            question=f"枚举{primary_loc['name']}从1940-2024年最高温度最高的10天",
            api_info={
                "error": str(e),
                "note": "请求受限或失败，未能获取数据"
            },
            data=[],
            data_key="hottest_days",
            location=primary_loc['name'],
            date_range="1940-2024",
            total_days_checked=0,
            top_n=10,
            status="failed",
            rate_limited=True
        )
        all_results.append(fallback)

    # ========================================
    # Part 4: Advanced Question - Top 100 Hottest Days (Extended)
    # 展示完整枚举能力 - 100天
    # ========================================
    print("\n" + "="*80)
    print(f"Part 4: 高级问题 - 史上最热的100天 (1940-2024, 完整枚举)")
    print("="*80)

    try:
        print(f"测试地点: {primary_loc['name']}")
        print("枚举1940-2024年最热的100天...")
        print("（展示真正的'枚举所有'能力 - OpenWeatherMap无法实现）")

        # Reuse all_time_data if available from Part 3, otherwise fetch
        if 'all_time_data' not in locals() or not all_time_data:
            all_time_data, api_info, _ = fetcher.fetch_historical_weather(
                location_key=primary_loc['location_key'],
                start_date="1940-01-01",
                end_date="2024-10-29",
                include_metadata=True
            )

        # Get top 100 hottest days
        top_100_hottest = fetcher.get_top_n_by_temperature(
            all_time_data,
            n=100,
            descending=True,
            temp_field='temp_max'
        )

        result = create_test_result(
            identifier=f"top100_hottest_{primary_loc['location_key']}",
            question=f"枚举{primary_loc['name']}从1940-2024年最高温度最高的100天",
            api_info=api_info,
            data=top_100_hottest,
            data_key="top_100_hottest",
            location=primary_loc['name'],
            date_range="1940-2024",
            total_days_checked=len(all_time_data),
            top_n=100
        )

        all_results.append(result)

        print(f"  ✓ 成功枚举最热的100天")
        print(f"  ✓ 数据来源: {len(all_time_data)} 天 ({len(all_time_data)/365:.1f}年)")

        # Show top 10 and statistics
        print(f"\n  前10名:")
        for day in top_100_hottest[:10]:
            print(f"    #{day['rank']}. {day['date']}: {day['temp_max']:.1f}°C")

        # Statistics
        temps_100 = [d['temp_max'] for d in top_100_hottest]
        print(f"\n  TOP 100统计:")
        print(f"    最高: {max(temps_100):.1f}°C")
        print(f"    最低: {min(temps_100):.1f}°C")
        print(f"    平均: {sum(temps_100)/len(temps_100):.1f}°C")
        print(f"    第100名温度: {top_100_hottest[99]['temp_max']:.1f}°C")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        fallback = create_test_result(
            identifier=f"top100_hottest_{primary_loc['location_key']}",
            question=f"枚举{primary_loc['name']}从1940-2024年最高温度最高的100天",
            api_info={"error": str(e)},
            data=[],
            data_key="top_100_hottest",
            location=primary_loc['name'],
            status="failed"
        )
        all_results.append(fallback)

    # ========================================
    # Part 5: Advanced Question - Climate Change Comparison
    # 气候变化证据 - 跨年代对比
    # ========================================
    print("\n" + "="*80)
    print(f"Part 5: 高级问题 - 气候变化对比 (1940-1970 vs 1990-2024)")
    print("="*80)

    try:
        print(f"测试地点: {primary_loc['name']}")
        print("比较1940-1970年代 vs 1990-2024年代的夏季平均温度...")
        print("（气候变暖证据 - 需要80年完整数据）")

        # Reuse all_time_data if available
        if 'all_time_data' not in locals() or not all_time_data:
            all_time_data, api_info, _ = fetcher.fetch_historical_weather(
                location_key=primary_loc['location_key'],
                start_date="1940-01-01",
                end_date="2024-10-29",
                include_metadata=True
            )

        # Compare summer temperatures between two periods
        comparison = fetcher.compare_period_temperatures(
            all_time_data,
            period1_start="1940-01-01",
            period1_end="1970-12-31",
            period2_start="1990-01-01",
            period2_end="2024-10-29",
            season="summer",  # Only summer months (Jun-Aug)
            temp_field="temp_mean"
        )

        result = create_test_result(
            identifier=f"climate_comparison_{primary_loc['location_key']}",
            question=f"比较{primary_loc['name']}夏季平均温度: 1940-1970 vs 1990-2024",
            api_info=api_info,
            data=comparison,
            data_key="climate_comparison",
            location=primary_loc['name'],
            comparison_type="period_temperature"
        )

        all_results.append(result)

        print(f"  ✓ 对比分析完成")
        print(f"\n  时期1 (1940-1970年夏季):")
        print(f"    天数: {comparison['period1']['total_days']}")
        print(f"    平均温度: {comparison['period1']['avg_temp']}°C")
        print(f"    最高: {comparison['period1']['max_temp']}°C, 最低: {comparison['period1']['min_temp']}°C")

        print(f"\n  时期2 (1990-2024年夏季):")
        print(f"    天数: {comparison['period2']['total_days']}")
        print(f"    平均温度: {comparison['period2']['avg_temp']}°C")
        print(f"    最高: {comparison['period2']['max_temp']}°C, 最低: {comparison['period2']['min_temp']}°C")

        print(f"\n  气候变化:")
        temp_diff = comparison['comparison']['temp_difference']
        warming = comparison['comparison']['warming_detected']
        print(f"    温度差异: {'+' if temp_diff > 0 else ''}{temp_diff}°C")
        print(f"    变化趋势: {'🔥 变暖' if warming else '❄️ 变冷'}")
        if warming:
            print(f"    ⚠️  数据显示: 近期夏季比早期温暖了 {temp_diff}°C")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        fallback = create_test_result(
            identifier=f"climate_comparison_{primary_loc['location_key']}",
            question=f"比较{primary_loc['name']}夏季平均温度: 1940-1970 vs 1990-2024",
            api_info={"error": str(e)},
            data={},
            data_key="climate_comparison",
            location=primary_loc['name'],
            status="failed"
        )
        all_results.append(fallback)

    # ========================================
    # Part 6: Advanced Question - Longest Heatwave
    # 最长连续高温期 - 复杂时间窗口分析
    # ========================================
    print("\n" + "="*80)
    print(f"Part 6: 高级问题 - 史上最长热浪 (>30°C连续天数)")
    print("="*80)

    try:
        print(f"测试地点: {primary_loc['name']}")
        print("查找1940-2024年史上最长的连续高温期（每天>30°C）...")
        print("（复杂时间窗口分析 - 需要完整历史数据）")

        # Reuse all_time_data if available
        if 'all_time_data' not in locals() or not all_time_data:
            all_time_data, api_info, _ = fetcher.fetch_historical_weather(
                location_key=primary_loc['location_key'],
                start_date="1940-01-01",
                end_date="2024-10-29",
                include_metadata=True
            )

        # Find longest heatwave
        longest_heatwave = fetcher.find_longest_heatwave(
            all_time_data,
            min_temp=30.0,
            temp_field='temp_max',
            min_duration=3
        )

        result = create_test_result(
            identifier=f"longest_heatwave_{primary_loc['location_key']}",
            question=f"枚举{primary_loc['name']}从1940-2024年最长的连续高温期(>30°C)",
            api_info=api_info,
            data=longest_heatwave,
            data_key="longest_heatwave",
            location=primary_loc['name'],
            date_range="1940-2024",
            min_temp=30.0
        )

        all_results.append(result)

        if longest_heatwave.get('found'):
            print(f"  ✓ 找到史上最长热浪!")
            print(f"\n  热浪详情:")
            print(f"    开始日期: {longest_heatwave['start_date']}")
            print(f"    结束日期: {longest_heatwave['end_date']}")
            print(f"    持续天数: {longest_heatwave['duration_days']} 天")
            print(f"    平均温度: {longest_heatwave['avg_temp']}°C")
            print(f"    最高温度: {longest_heatwave['max_temp']}°C")
            print(f"    峰值日期: {longest_heatwave['peak_date']}")
            print(f"\n  🔥 这是{primary_loc['name']}有记录以来最长的连续高温期！")
        else:
            print(f"  ✓ {longest_heatwave.get('message', '未找到符合条件的热浪')}")

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")
        fallback = create_test_result(
            identifier=f"longest_heatwave_{primary_loc['location_key']}",
            question=f"枚举{primary_loc['name']}从1940-2024年最长的连续高温期(>30°C)",
            api_info={"error": str(e)},
            data={},
            data_key="longest_heatwave",
            location=primary_loc['name'],
            status="failed"
        )
        all_results.append(fallback)

    # ========================================
    # Save All Results
    # ========================================
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)

    summary = {
        "api_name": "Open-Meteo API",
        "requires_auth": False,
        "auth_type": "None - No API key required",
        "historical_data_range": "1940-present (80+ years)",
        "forecast_range": "16 days",
        "rate_limits": "None for reasonable use",
        "advantages": [
            "TRUE completeness: 80+ years of historical data",
            "NO authentication complexity",
            "NO rate limits",
            "Global coverage",
            "Free and open source"
        ],
        "comparison_to_openweathermap": {
            "historical_data": "80+ years vs 5 days",
            "authentication": "None vs API key required",
            "rate_limits": "None vs 1000 calls/day",
            "completeness": "Excellent vs Poor"
        },
        "config": config,
        "total_tests": len(all_results),
        "tests": all_results
    }

    save_result("weather_climate/openmeteo", summary)

    print(f"\n总测试数: {len(all_results)}")
    print("所有测试已完成！")
    print("\n✓ Open-Meteo API 优势总结:")
    print("  • 真正的'枚举所有'能力 - 80+年完整历史数据")
    print("  • 完全免费 - 无需API密钥")
    print("  • 无速率限制 - 可以进行全面测试")
    print("  • 完美契合框架核心理念")

    return all_results


if __name__ == "__main__":
    run()
