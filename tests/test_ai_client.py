"""Unit tests for modules/ai_client.py"""

import unittest
from unittest.mock import MagicMock, patch

from modules import ai_client


class TestTokenEstimation(unittest.TestCase):
    """Test token estimation in ai_client."""

    def test_estimate_prompt_tokens_empty(self):
        """Empty prompts should estimate to 0 tokens."""
        result = ai_client.estimate_prompt_tokens("", "")
        self.assertEqual(result, 0)

    def test_estimate_prompt_tokens_small(self):
        """Small prompts should estimate to small token count."""
        system = "You are an AI."
        user = "Hello, how are you?"
        result = ai_client.estimate_prompt_tokens(system, user)
        self.assertGreater(result, 0)
        self.assertLess(result, 100)

    def test_estimate_prompt_tokens_1kb(self):
        """~1 KB should estimate to ~224 tokens."""
        system = "You are an AI." * 10
        user = "x" * 900
        result = ai_client.estimate_prompt_tokens(system, user)
        # Should be approximately 200-250 tokens
        self.assertGreater(result, 150)
        self.assertLess(result, 300)


class TestCompleteFunction(unittest.TestCase):
    """Test the complete() function."""

    def setUp(self):
        """Set up mock client."""
        self.mock_client = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message.content = "Test response"
        self.mock_response.usage = MagicMock()
        self.mock_response.usage.prompt_tokens = 100
        self.mock_response.usage.completion_tokens = 50
        self.mock_response.usage.total_tokens = 150

    def test_complete_success(self):
        """successful completion should return content and usage."""
        self.mock_client.chat.completions.create.return_value = self.mock_response

        result = ai_client.complete(
            client=self.mock_client,
            deployment="gpt-4",
            system_prompt="You are an expert.",
            user_prompt="Analyze this data.",
            max_tokens=1000,
        )

        self.assertEqual(result["content"], "Test response")
        self.assertEqual(result["usage"]["prompt_tokens"], 100)
        self.assertEqual(result["usage"]["completion_tokens"], 50)
        self.assertEqual(result["usage"]["total_tokens"], 150)

    def test_complete_with_custom_temperature(self):
        """Completion should accept custom temperature."""
        self.mock_client.chat.completions.create.return_value = self.mock_response

        ai_client.complete(
            client=self.mock_client,
            deployment="gpt-4",
            system_prompt="You are an expert.",
            user_prompt="Analyze this data.",
            max_tokens=1000,
            temperature=0.5,
        )

        # Check that temperature was passed correctly
        call_args = self.mock_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs["temperature"], 0.5)

    def test_complete_respects_max_input_tokens_default(self):
        """Completion should use default max_input_tokens of 272000."""
        self.mock_client.chat.completions.create.return_value = self.mock_response

        # Small prompts should pass
        ai_client.complete(
            client=self.mock_client,
            deployment="gpt-4",
            system_prompt="Small prompt",
            user_prompt="Small user",
            max_tokens=1000,
        )

        # Should not raise
        self.mock_client.chat.completions.create.assert_called_once()

    def test_complete_respects_custom_max_input_tokens(self):
        """Completion should respect custom max_input_tokens."""
        # Create a large user prompt (will exceed 1000 token limit)
        large_prompt = "x" * 5000

        with self.assertRaises(ValueError) as context:
            ai_client.complete(
                client=self.mock_client,
                deployment="gpt-4",
                system_prompt="System",
                user_prompt=large_prompt,
                max_tokens=1000,
                max_input_tokens=1000,  # Very restrictive limit
            )

        self.assertIn("exceeds limit", str(context.exception))
        # Should not have called the API
        self.mock_client.chat.completions.create.assert_not_called()

    def test_complete_raises_on_oversized_prompt(self):
        """Completion should raise ValueError for oversized prompts."""
        # Create prompts that together exceed 272K tokens
        # ~1.3 MB of text should exceed 272K tokens (224 tokens/KB)
        oversized_prompt = "x" * (2 * 1024 * 1024)  # 2 MB

        with self.assertRaises(ValueError) as context:
            ai_client.complete(
                client=self.mock_client,
                deployment="gpt-4",
                system_prompt="System",
                user_prompt=oversized_prompt,
                max_tokens=1000,
                max_input_tokens=272000,
            )

        self.assertIn("exceeds limit", str(context.exception))
        self.assertIn("272000", str(context.exception))

    def test_complete_with_none_usage(self):
        """Completion should handle None usage gracefully."""
        self.mock_response.usage = None

        self.mock_client.chat.completions.create.return_value = self.mock_response

        result = ai_client.complete(
            client=self.mock_client,
            deployment="gpt-4",
            system_prompt="System",
            user_prompt="User",
            max_tokens=1000,
        )

        self.assertEqual(result["usage"]["prompt_tokens"], 0)
        self.assertEqual(result["usage"]["completion_tokens"], 0)
        self.assertEqual(result["usage"]["total_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
