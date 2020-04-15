import unittest
from unittest.mock import patch
from tests.sendle.fixture import gateway
from purplship.core.utils.helpers import to_dict
from purplship.core.models import TrackingRequest
from purplship.package import Tracking


class TestSendleTracking(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.TrackingRequest = TrackingRequest(tracking_numbers=TRACKING_REQUEST)

    def test_create_tracking_request(self):
        request = gateway.mapper.create_tracking_request(self.TrackingRequest)
        self.assertEqual(request.serialize(), TRACKING_REQUEST)

    @patch("purplship.package.mappers.sendle.proxy.http", return_value="{}")
    def test_get_tracking(self, http_mock):
        Tracking.fetch(self.TrackingRequest).from_(gateway)

        url = http_mock.call_args[1]["url"]
        self.assertEqual(url, TRACKING_REQUEST_QUERY_STR)

    def test_parse_tracking_response(self):
        with patch("purplship.package.mappers.sendle.proxy.exec_parrallel") as mock:
            mock.return_value = TRACKING_RESPONSE
            parsed_response = (
                Tracking.fetch(self.TrackingRequest).from_(gateway).parse()
            )

            self.assertEqual(
                to_dict(parsed_response), to_dict(PARSED_TRACKING_RESPONSE)
            )

    def test_parse_tracking_response_with_errors(self):
        with patch("purplship.package.mappers.sendle.proxy.exec_parrallel") as mock:
            mock.return_value = TRACKING_RESPONSE_WITH_ERROR
            parsed_response = (
                Tracking.fetch(self.TrackingRequest).from_(gateway).parse()
            )
            self.assertEqual(
                to_dict(parsed_response), to_dict(PARSED_TRACKING_RESPONSE_WITH_ERROR)
            )


if __name__ == "__main__":
    unittest.main()


TRACKING_REQUEST = ["S3ND73"]

PARSED_TRACKING_RESPONSE = [
    [
        {
            "carrier": "sendle",
            "carrier_name": "Sendle",
            "events": [
                {
                    "code": "Pickup Attempted",
                    "date": "2015-11-23",
                    "description": "We attempted to pick up the parcel but were unsuccessful",
                    "time": "01:04",
                },
                {
                    "code": "Pickup",
                    "date": "2015-11-24",
                    "description": "Parcel picked up",
                    "time": "20:31",
                },
                {
                    "code": "Info",
                    "date": "2015-11-25",
                    "description": "In transit between locations",
                    "time": "01:04",
                },
                {
                    "code": "In Transit",
                    "date": "2015-11-25",
                    "description": "In transit",
                    "location": "Brisbane",
                    "time": "01:14",
                },
                {
                    "code": "Info",
                    "date": "2015-11-26",
                    "description": "Arrived at the depot for processing",
                    "time": "19:46",
                },
                {
                    "code": "Info",
                    "date": "2015-11-26",
                    "description": "Parcel is loaded for delivery",
                    "time": "23:00",
                },
                {
                    "code": "Delivered",
                    "date": "2015-11-27",
                    "description": "Parcel delivered",
                    "time": "23:46",
                },
                {
                    "code": "Info",
                    "date": "2015-11-27",
                    "description": "Your parcel was signed for by JIMMY",
                    "time": "23:47",
                },
            ],
            "tracking_number": "S3ND73",
        }
    ],
    [],
]


PARSED_TRACKING_RESPONSE_WITH_ERROR = [
    [],
    [
        {
            "carrier": "sendle",
            "carrier_name": "Sendle",
            "code": "unprocessable_entity",
            "message": "The data you supplied is invalid. Error messages are in the messages section. Please fix those fields and try again.",
        }
    ],
]


TRACKING_REQUEST_QUERY_STR = f"{gateway.settings.server_url}/tracking/S3ND73"

TRACKING_RESPONSE = [
    {
        "ref": "S3ND73",
        "response": {
            "state": "Delivered",
            "tracking_events": [
                {
                    "event_type": "Pickup Attempted",
                    "scan_time": "2015-11-23T01:04:00Z",
                    "description": "We attempted to pick up the parcel but were unsuccessful",
                    "reason": "Parcel not ready",
                },
                {
                    "event_type": "Pickup",
                    "scan_time": "2015-11-24T20:31:00Z",
                    "description": "Parcel picked up",
                },
                {
                    "event_type": "Info",
                    "scan_time": "2015-11-25T01:04:00Z",
                    "description": "In transit between locations",
                },
                {
                    "event_type": "In Transit",
                    "scan_time": "2015-11-25T01:14:00Z",
                    "description": "In transit",
                    "origin_location": "Sydney",
                    "destination_location": "Brisbane",
                },
                {
                    "event_type": "Info",
                    "scan_time": "2015-11-26T19:46:00Z",
                    "description": "Arrived at the depot for processing",
                },
                {
                    "event_type": "Info",
                    "scan_time": "2015-11-26T23:00:00Z",
                    "description": "Parcel is loaded for delivery",
                },
                {
                    "event_type": "Delivered",
                    "scan_time": "2015-11-27T23:46:00Z",
                    "description": "Parcel delivered",
                },
                {
                    "event_type": "Info",
                    "scan_time": "2015-11-27T23:47:00Z",
                    "description": "Your parcel was signed for by JIMMY",
                },
            ],
        },
    }
]

TRACKING_RESPONSE_WITH_ERROR = [
    {
        "ref": "S3ND73",
        "response": {
            "error": "unprocessable_entity",
            "error_description": "The data you supplied is invalid. Error messages are in the messages section. Please fix those fields and try again.",
        },
    }
]