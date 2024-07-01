import unittest
from unittest.mock import patch
from app import (
    pruned_sd_request,
    sdxl_sd_request,
    generate_image_based_on_model,
)


class TestPrunedSdRequest(unittest.TestCase):

    @patch("runpod_sd_proxy.app.requests.post")
    def test_pruned_sd_request(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"images": ["some_base64_encoded_data"]},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        sd_request = {"input": {"prompt": "Test prompt", "steps": 5, "batch_size": 1}}
        headers = {"Authorization": "Bearer testtoken"}
        result_image = pruned_sd_request(sd_request, headers)
        print(result_image)
        expected_image = "some_base64_encoded_data"
        self.assertEqual(result_image, expected_image)

    @patch("runpod_sd_proxy.app.requests.post")
    def test_pruned_sd_request_error_on_invalid_response(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"bad_response": "malformed"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        sd_request = {"input": {"prompt": "Test prompt", "steps": 5, "batch_size": 1}}
        headers = {"Authorization": "Bearer testtoken"}
        result_image = pruned_sd_request(sd_request, headers)
        print(result_image)
        expected_output = {"error": "Invalid response from runpod"}
        self.assertEqual(result_image, expected_output)


class TestSDXLSdRequest(unittest.TestCase):

    @patch("runpod_sd_proxy.app.requests.post")
    def test_sdxl_sd_request(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"image_url": "data:image/png;base64,some_base64_encoded_data"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        sd_request = {"input": {"prompt": "Test prompt", "steps": 5, "batch_size": 1}}
        headers = {"Authorization": "Bearer testtoken"}
        result_image = sdxl_sd_request(sd_request, headers)
        print(result_image)
        expected_image = "some_base64_encoded_data"
        self.assertEqual(result_image, expected_image)

    @patch("runpod_sd_proxy.app.requests.post")
    def test_sdxl_sd_request_error_on_invalid_response(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"bad_response": "malformed"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        sd_request = {"input": {"prompt": "Test prompt", "steps": 5, "batch_size": 1}}
        headers = {"Authorization": "Bearer testtoken"}
        result_image = sdxl_sd_request(sd_request, headers)
        print(result_image)
        expected_output = {"error": "Invalid response from runpod"}
        self.assertEqual(result_image, expected_output)


class TestGenerateImageBasedOnModel(unittest.TestCase):

    @patch("runpod_sd_proxy.app.requests.post")
    def test_generate_image_based_on_model_sd(self, mock_post):
        mock_response_data = {
            "output": {"images": ["some_base64_encoded_data"]},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        request_body = {"prompt": "Test prompt", "steps": 5, "batch_size": 1}

        output = generate_image_based_on_model(pruned_sd_request, request_body)
        expected_output = "some_base64_encoded_data"

        self.assertEqual(output, expected_output)

    @patch("runpod_sd_proxy.app.requests.post")
    def test_generate_image_based_on_model_sdxl(self, mock_post):
        mock_response_data = {
            "output": {"image_url": "data:image/png;base64,some_base64_encoded_data"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        request_body = {"prompt": "Test prompt", "steps": 5, "batch_size": 1}

        output = generate_image_based_on_model(sdxl_sd_request, request_body)
        expected_output = "some_base64_encoded_data"

        self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()
