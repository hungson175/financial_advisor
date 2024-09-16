import unittest
from fad.generators.generate_agent import GeneratedAgent, choose_agent
from dotenv import load_dotenv

load_dotenv()


class TestChooseAgent(unittest.TestCase):

    def test_choose_agent_basic(self):
        # Arrange

        test_query = "How should I invest in the Vietnamese stock market?"
        agent = choose_agent(test_query)
        self.assertIsInstance(agent, GeneratedAgent)
        # assert that agent.server contains string "Finance"
        self.assertIn("Finance", agent.server)
        self.assertIsInstance(agent.agent_role_prompt, str)
        print(agent)


if __name__ == '__main__':
    unittest.main()
