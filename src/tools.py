import os
from langchain_tavily import TavilySearch


def get_tavily_tool():
    return TavilySearch(max_results=5)
