
import unittest
from unittest.mock import patch, ANY
from .fixture import gateway

import karrio
import karrio.lib as lib
import karrio.core.models as models


class Testfreightcomv2Tracking(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.TrackingRequest = models.TrackingRequest(**TrackingPayload)

    def test_create_tracking_request(self):
        request = gateway.mapper.create_tracking_request(self.TrackingRequest)
        self.assertEqual(request.serialize(), TrackingRequest)

    def test_get_tracking(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
            mock.return_value = "{}"
            karrio.Tracking.fetch(self.TrackingRequest).from_(gateway)

            self.assertEqual(
                mock.call_args[1]["url"],
                f"{gateway.settings.server_url}/shipment/{self.TrackingRequest.tracking_numbers[0]}/tracking-events",
            )

    def test_parse_tracking_response(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
            mock.return_value = TrackingResponse
            parsed_response = (
                karrio.Tracking.fetch(self.TrackingRequest).from_(gateway).parse()
            )

            self.assertListEqual(
                lib.to_dict(parsed_response), ParsedTrackingResponse
            )

    def test_parse_error_response(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
            mock.return_value = ErrorResponse
            parsed_response = (
                karrio.Tracking.fetch(self.TrackingRequest).from_(gateway).parse()
            )

            self.assertListEqual(
                lib.to_dict(parsed_response), ParsedErrorResponse
            )

if __name__ == "__main__":
    unittest.main()

TrackingPayload = {
    "tracking_numbers": ["89108749065090"],
}

ParsedTrackingResponse = [
    {
        "carrier_id": "freightcomv2",
        "carrier_name": "Freightcom",
        "tracking_number": "89108749065090",
        "events": [
            {
                "date": "2024-01-01",
                "description": "Label Created",
                "code": "label-created",
                "time": "10:00",
                "location": "Waterloo, ON, CA"
            }
        ],
        "estimated_delivery": "2024-01-05",
        "delivered": False,
    }
]

ParsedErrorResponse = [
    {
        "carrier_id": "freightcomv2",
        "carrier_name": "Freightcom",
        "code": "error_code",
        "message": "error_message",
        "details": {},
    }
]

TrackingRequest = {
    "tracking_numbers": ["89108749065090"]
}

TrackingResponse = """{
    "events": [
        {
            "type": "label-created",
            "when": "2024-01-01T10:00:00",
            "where": {
                "city": "Waterloo",
                "region": "ON",
                "country": "CA"
            },
            "message": "Label Created"
        }
    ],
    "tracking_number": "89108749065090",
    "estimated_delivery": "2024-01-05",
    "delivered": false
}"""

ErrorResponse = """{
    "errors": [
        {
            "code": "error_code",
            "message": "error_message"
        }
    ]
}"""
