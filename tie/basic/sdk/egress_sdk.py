"""Egress SDK for uploading data via HTTP POST."""

import requests


class EgressSDK:
    """Egress SDK for uploading data via HTTP POST."""

    def __init__(self, base_url: str = 'https://httpbin.org/post'):
        """Initialize the SDK.

        :param base_url: The endpoint where the data should be sent.
        """
        self.base_url = base_url

    def upload(self, json: dict) -> dict:
        """Upload data via HTTP POST.

        :param data: The payload to send.
        :param headers: Optional headers.
        :return: The JSON response from the server.
        """
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.base_url, json=json, headers=headers, timeout=5)
        response.raise_for_status()  # Raises an error if the request fails
        return response.json()
