"""API数据获取器模块"""

# 代码/开发相关
from .code_ecosystem import (
    NPMFetcher,
    PyPIFetcher,
    GitHubFetcher,
    CratesFetcher,
    RubyGemsFetcher,
    NuGetFetcher,
    GoProxyFetcher,
    CondaFetcher,
    CRANFetcher,
    HomebrewFetcher,
)
# Maven Central removed - cannot enumerate all versions (max 1000 limit)

# 学术/科研相关
from .academic_research import DBLPFetcher, PubMedFetcher, ZenodoFetcher
# USPTO Patents removed - inventor name search not precise

# 媒体/娱乐相关
from .media_entertainment import (
    SpotifyFetcher,
    YouTubeFetcher,
    TMDbFetcher,
    IMDbFetcher,
    OpenLibraryFetcher,
)

# 知识/信息相关
from .wikipedia import WikipediaFetcher

# 商业/金融相关
from .sec_edgar import SECEdgarFetcher

# 基础设施/地理相关
from .openstreetmap import OpenStreetMapFetcher
from .crtsh import CrtShFetcher

# 政府/开放数据
from .datagov import DataGovFetcher

# 天气/气候相关
from .weather_climate import OpenMeteoFetcher
# OpenWeatherMap removed - completeness issues (only ~5 days of historical data)

# AI/ML相关
from .ai_ml import HuggingFaceFetcher

# 所有可用的fetchers
ALL_FETCHERS = [
    # 代码生态系统
    NPMFetcher,
    PyPIFetcher,
    GitHubFetcher,
    CratesFetcher,
    RubyGemsFetcher,
    NuGetFetcher,
    GoProxyFetcher,
    CondaFetcher,
    CRANFetcher,
    HomebrewFetcher,
    # 学术科研
    DBLPFetcher,
    PubMedFetcher,
    ZenodoFetcher,
    # 媒体娱乐
    SpotifyFetcher,
    YouTubeFetcher,
    TMDbFetcher,
    IMDbFetcher,
    # OpenLibraryFetcher removed - data quality issues
    # 知识信息
    WikipediaFetcher,
    # 商业金融
    SECEdgarFetcher,
    # 基础设施/地理
    OpenStreetMapFetcher,
    CrtShFetcher,
    # 政府/开放数据
    DataGovFetcher,
    # 天气/气候
    OpenMeteoFetcher,
    # AI/ML
    HuggingFaceFetcher,
]

__all__ = [
    'NPMFetcher',
    'PyPIFetcher',
    'GitHubFetcher',
    'CratesFetcher',
    'RubyGemsFetcher',
    'NuGetFetcher',
    'GoProxyFetcher',
    'CondaFetcher',
    'CRANFetcher',
    'HomebrewFetcher',
    'DBLPFetcher',
    'PubMedFetcher',
    'ZenodoFetcher',
    'SpotifyFetcher',
    'YouTubeFetcher',
    'TMDbFetcher',
    'IMDbFetcher',
    # 'OpenLibraryFetcher',  # Removed - data quality issues
    'WikipediaFetcher',
    'SECEdgarFetcher',
    'OpenStreetMapFetcher',
    'CrtShFetcher',
    'DataGovFetcher',
    'OpenMeteoFetcher',
    'HuggingFaceFetcher',
    'ALL_FETCHERS',
]
