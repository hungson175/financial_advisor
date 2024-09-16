import unittest

from dotenv import load_dotenv
from fad.tools.websearch_tools import web_search

load_dotenv()


class TestWebSearch(unittest.TestCase):
    def test_search(self):
        docs = web_search("Should I invest in FPT stock right now ?", max_results=5)
        print(docs)
        self.assertTrue(len(docs) <= 5)
        self.assertIsInstance(docs[0]["url"], str)
        self.assertIsInstance(docs[0]["content"], str)
