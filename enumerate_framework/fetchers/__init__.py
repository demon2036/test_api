"""API数据获取器模块"""

# 代码/开发相关
from .npm import NPMFetcher
from .pypi import PyPIFetcher
from .github import GitHubFetcher
from .docker import DockerFetcher
from .crates import CratesFetcher
from .rubygems import RubyGemsFetcher
from .nuget import NuGetFetcher
from .go_proxy import GoProxyFetcher
from .conda import CondaFetcher
from .cran import CRANFetcher
# Maven Central removed - cannot enumerate all versions (max 1000 limit)
from .homebrew import HomebrewFetcher

# 学术/科研相关
from .dblp import DBLPFetcher
from .pubmed import PubMedFetcher
from .zenodo import ZenodoFetcher
# USPTO Patents removed - inventor name search not precise

# 媒体/娱乐相关
from .spotify import SpotifyFetcher
from .youtube import YouTubeFetcher
from .tmdb import TMDbFetcher
from .imdb import IMDbFetcher
from .goodreads import OpenLibraryFetcher

# 知识/信息相关
from .wikipedia import WikipediaFetcher

# 商业/金融相关
from .sec_edgar import SECEdgarFetcher

# 基础设施/地理相关
# OpenStreetMap removed - community data completeness not guaranteed
from .crtsh import CrtShFetcher

# AI/ML相关
from .huggingface import HuggingFaceFetcher

# 所有可用的fetchers
ALL_FETCHERS = [
    # 代码生态系统
    NPMFetcher,
    PyPIFetcher,
    GitHubFetcher,
    DockerFetcher,
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
    OpenLibraryFetcher,
    # 知识信息
    WikipediaFetcher,
    # 商业金融
    SECEdgarFetcher,
    # 基础设施
    CrtShFetcher,
    # AI/ML
    HuggingFaceFetcher,
]

__all__ = [
    'NPMFetcher',
    'PyPIFetcher',
    'GitHubFetcher',
    'DockerFetcher',
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
    'OpenLibraryFetcher',
    'WikipediaFetcher',
    'SECEdgarFetcher',
    'CrtShFetcher',
    'HuggingFaceFetcher',
    'ALL_FETCHERS',
]
