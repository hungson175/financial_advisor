import unittest
from fad.generators.generate_sub_queries import generate_sub_queries, SubQueries
from dotenv import load_dotenv

load_dotenv()


class TestGenerateSubQueries(unittest.TestCase):

    def test_generate_subqueries_basic(self):
        # Arrange

        test_query = "Should I invest in FPT stock right now or in 6-12 months ?"
        qs = generate_sub_queries(test_query, 3)
        print(qs)
        self.assertIsInstance(qs, SubQueries)
        self.assertEquals(len(qs.list), 3)
        # assert that agent.server contains string "Finance"
        self.assertIsInstance(qs.list[0], str)

