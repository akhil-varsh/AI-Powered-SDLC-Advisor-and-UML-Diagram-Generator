import unittest
from claude.core import model_api

class TestModelAPI(unittest.TestCase):
    def test_call_model_success(self):
        # This test assumes Ollama is running and the model is available
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello."}
        ]
        response = model_api.call_model(messages)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_call_model_with_system(self):
        # This test assumes Ollama is running and the model is available
        response = model_api.call_model_with_system(
            system_prompt="You are a helpful assistant.",
            user_message="Say hello."
        )
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_call_model_invalid_url(self):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello."}
        ]
        response = model_api.call_model(messages, api_base="http://localhost:9999")
        self.assertIsNone(response)

if __name__ == "__main__":
    unittest.main()
