import unittest
from unittest.mock import patch
from runpod_sd_proxy.models import SDRequest
from runpod_sd_proxy.routes import (
    pruned_sd_request,
    sdxl_sd_request,
    generate_image_based_on_model,
)
from pydantic import ValidationError


sd_request = SDRequest.model_validate(
    {"input": {"prompt": "Test prompt", "steps": 5, "batch_size": 1}}
)


class TestPrunedSdRequest(unittest.TestCase):

    @patch("runpod_sd_proxy.routes.requests.post")
    def test_pruned_sd_request(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"images": ["some_base64_encoded_data"]},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        headers = {"Authorization": "Bearer testtoken"}
        result_image = pruned_sd_request(sd_request, headers)
        print(result_image)
        expected_image = "some_base64_encoded_data"
        self.assertEqual(result_image, expected_image)

    @patch("runpod_sd_proxy.routes.requests.post")
    def test_pruned_sd_request_error_on_invalid_response(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"bad_response": "malformed"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        headers = {"Authorization": "Bearer testtoken"}
        with self.assertRaises(ValidationError):
            result_image = pruned_sd_request(sd_request, headers)


class TestSDXLSdRequest(unittest.TestCase):

    @patch("runpod_sd_proxy.routes.requests.post")
    def test_sdxl_sd_request(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"image_url": "data:image/png;base64,some_base64_encoded_data"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        headers = {"Authorization": "Bearer testtoken"}
        result_image = sdxl_sd_request(sd_request, headers)
        print(result_image)
        expected_image = "some_base64_encoded_data"
        self.assertEqual(result_image, expected_image)

    @patch("runpod_sd_proxy.routes.requests.post")
    def test_sdxl_sd_request_error_on_invalid_response(self, mock_post):
        # Mock response data
        mock_response_data = {
            "output": {"bad_response": "malformed"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        headers = {"Authorization": "Bearer testtoken"}
        with self.assertRaises(ValidationError):
            result_image = sdxl_sd_request(sd_request, headers)


class TestGenerateImageBasedOnModel(unittest.TestCase):

    @patch("runpod_sd_proxy.routes.requests.post")
    def test_generate_image_based_on_model_sd(self, mock_post):
        mock_response_data = {
            "output": {"images": ["some_base64_encoded_data"]},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        request_body = sd_request

        output = generate_image_based_on_model(pruned_sd_request, request_body)
        expected_output = "some_base64_encoded_data"

        self.assertEqual(output, expected_output)

    @patch("runpod_sd_proxy.routes.requests.post")
    def test_generate_image_based_on_model_sdxl(self, mock_post):
        mock_response_data = {
            "output": {"image_url": "data:image/png;base64,some_base64_encoded_data"},
        }
        mock_post.return_value.json.return_value = mock_response_data
        print(mock_post.return_value.json.return_value)
        # Define sample input for the test
        request_body = sd_request

        output = generate_image_based_on_model(sdxl_sd_request, request_body)
        expected_output = "some_base64_encoded_data"

        self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()
