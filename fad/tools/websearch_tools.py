from langchain_community.tools import TavilySearchResults
from langchain_community.utilities import GoogleSearchAPIWrapper, GoogleSerperAPIWrapper


def google_search(query: str, max_results: int = 5):
    search = GoogleSerperAPIWrapper()
    docs = search.results(query)
    ll = docs['organic']
    ret = []
    for i in range(min(len(ll), max_results)):
        ret.append({'url': ll[i]['link'], 'content': ll[i]['snippet']})
    return ret


def tavily_search(query: str, max_results: int = 5):
    tool = TavilySearchResults(k=max_results)
    docs = tool.invoke({"query": query})
    # doc: url: str, content: str
    return docs


def web_search(query: str, max_results: int = 5):
    """Search the web for the given query."""
    return tavily_search(query, max_results)


def search_queries(queries: list, max_results: int = 5):
    """Search the web for the given queries."""
    results = {}
    for query in queries:
        results[query] = web_search(query, max_results)
    return results
