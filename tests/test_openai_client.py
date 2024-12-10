import unittest
from unittest.mock import patch, MagicMock
from ai.openai import OpenAIClient


class TestOpenAIClient(unittest.TestCase):
    @patch('ai.openai.OpenAI')
    def test_chat_completions(self, MockOpenAI):
        # Mock the OpenAI client and its methods
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message={"role": "assistant", "content": "Recursion is fun."})]
        mock_client.chat.completions.create.return_value = mock_response

        # Create an instance of OpenAIClient
        client = OpenAIClient()

        # Define test inputs
        messages = [{"role": "user", "content": "Write a haiku about recursion in programming."}]

        # Call the chat_completions method and collect results
        result = client.chat_completions(messages)

        # Verify the results
        self.assertEqual(result.choices[0].message["content"], "Recursion is fun.")


if __name__ == '__main__':
    unittest.main()
