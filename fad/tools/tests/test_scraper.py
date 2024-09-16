import unittest

from fad.tools.scrapers.scraper import Scraper


class TestScraper(unittest.TestCase):
    def test_scrape(self):
        urls = ["https://arxiv.org/abs/2305.04091",
                "https://vnexpress.net/giai-tri/phim/thu-vien-phim/love-next-door-730",
                "https://www.pdf995.com/samples/pdf.pdf"]
        results = Scraper.scrape_multiple_urls(urls)
        for result in results:
            print(result)
            self.assertIsNotNone(result["raw_content"])
            self.assertIsNotNone(result["url"])
            self.assertIsInstance(result["raw_content"], str)
            self.assertTrue(len(result["raw_content"]) > 0)

