from langchain_community.tools import TavilySearchResults
from langchain_community.utilities import GoogleSearchAPIWrapper, GoogleSerperAPIWrapper


def web_search(query: str, max_results: int = 5):
    """Search the web for the given query."""
    # tool = TavilySearchResults(k=max_results)
    # docs = tool.invoke({"query": query})
    # doc: url: str, content: str
    # search = GoogleSearchAPIWrapper()
    search = GoogleSerperAPIWrapper()

    docs = search.results(query)
    ll = docs['organic']
    ret = []
    for i in range(min(len(ll), max_results)):
        ret.append({'url': ll[i]['link'], 'content': ll[i]['snippet']})
    return ret


def search_queries(queries: list, max_results: int = 5):
    """Search the web for the given queries."""
    results = {}
    for query in queries:
        results[query] = web_search(query, max_results)
    return results
