import pytest
from unittest.mock import patch
from main import prepare_url, encode_credentials, send_request


def test_prepare_url():
    base_url = "https://example.com"
    owner_slug = "owner"
    dataset_slug = "dataset"
    dataset_version = 1

    expected_url = "https://example.com/datasets/download/owner/dataset?datasetVersionNumber=1"
    assert prepare_url(base_url, owner_slug, dataset_slug,
                       dataset_version) == expected_url


def test_encode_credentials():
    username = "user"
    key = "key"

    # base64 encoding of "user:key"
    expected_auth_header = {"Authorization": "Basic dXNlcjprZXk="}
    assert encode_credentials(username, key) == expected_auth_header


@patch('main.requests.get')
def test_send_request(mock_get):
    url = "https://example.com/test"
    headers = {"Authorization": "Basic dXNlcjprZXk="}  # Mocked header

    # Mock the response object
    mock_response = mock_get.return_value
    mock_response.status_code = 200  # Simulate a successful response
    mock_response.content = b"Mocked content"

    response = send_request(url, headers)

    # Assertions
    mock_get.assert_called_once_with(url, headers=headers)
    assert response.status_code == 200
    assert response.content == b"Mocked content"
