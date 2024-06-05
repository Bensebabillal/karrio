import unittest
from unittest.mock import patch, ANY
from .fixture import gateway

import karrio
import karrio.lib as lib
import karrio.core.models as models


class TestFrieghtcomv2Shipping(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.ShipmentRequest = models.ShipmentRequest(**ShipmentPayload)
        self.ShipmentCancelRequest = models.ShipmentCancelRequest(**ShipmentCancelPayload)

    def test_create_shipment_request(self):
        request = gateway.mapper.create_shipment_request(self.ShipmentRequest)
        self.assertEqual(request.serialize(), ShipmentRequest)

    def test_create_cancel_shipment_request(self):
        request = gateway.mapper.create_cancel_shipment_request(
            self.ShipmentCancelRequest
        )
        self.assertEqual(request.serialize(), ShipmentCancelRequest)

    def test_create_shipment(self):
        with patch("karrio.mappers.freightcom_com_v2.proxy.lib.request") as mock:
            mock.return_value = "{}"
            karrio.Shipment.create(self.ShipmentRequest).from_(gateway)
            self.assertEqual(
                mock.call_args[1]["url"],
                f"{gateway.settings.server_url}/shipment",
            )

    def test_cancel_shipment(self):
        with patch("karrio.mappers.freightcom_com_v2.proxy.lib.request") as mock:
            mock.return_value = "{}"
            karrio.Shipment.cancel(self.ShipmentCancelRequest).from_(gateway)
            self.assertEqual(
                mock.call_args[1]["url"],
                f"{gateway.settings.server_url}/shipment",
            )

    def test_parse_shipment_response(self):
        with patch("karrio.mappers.freightcom_com_v2.proxy.lib.request") as mock:
            mock.return_value = ShipmentResponse
            parsed_response = (
                karrio.Shipment.create(self.ShipmentRequest).from_(gateway).parse()
            )
            self.assertListEqual(lib.to_dict(parsed_response), ParsedShipmentResponse)

    def test_parse_cancel_shipment_response(self):
        with patch("karrio.mappers.freightcom_com_v2.proxy.lib.request") as mock:
            mock.return_value = ShipmentCancelResponse
            parsed_response = (
                karrio.Shipment.cancel(self.ShipmentCancelRequest).from_(gateway).parse()
            )
            self.assertListEqual(
                lib.to_dict(parsed_response), ParsedCancelShipmentResponse
            )


if __name__ == "__main__":
    unittest.main()


ShipmentPayload = {
    "service": "express",
    "shipper": {
        "company_name": "Shipper Company",
        "person_name": "John Doe",
        "phone_number": "1234567890",
        "address_line1": "123 Shipper St",
        "address_line2": "Suite 100",
        "city": "Shipper City",
        "state_code": "CA",
        "country_code": "US",
        "postal_code": "12345"
    },
    "recipient": {
        "company_name": "Recipient Company",
        "person_name": "Jane Smith",
        "phone_number": "0987654321",
        "address_line1": "456 Recipient Ave",
        "address_line2": "Apt 200",
        "city": "Recipient City",
        "state_code": "NY",
        "country_code": "US",
        "postal_code": "67890"
    },
    "parcels": [
        {
            "weight": 10.0,
            "weight_unit": "lb",
            "length": 10.0,
            "width": 10.0,
            "height": 10.0,
            "dimension_unit": "in"
        }
    ]
}

ShipmentCancelPayload = {
    "shipment_identifier": "794947717776",
}

ParsedShipmentResponse = [
    {
        "carrier_id": "freightcom",
        "carrier_name": "Freightcom",
        "service": "express",
        "total_charge": 225.47,
        "transit_days": 5,
        "currency": "CAD"
    }
]

ParsedCancelShipmentResponse = [
    {
        "carrier_id": "freightcom",
        "carrier_name": "Freightcom",
        "service": "express",
        "total_charge": 0.0,
        "currency": "CAD"
    }
]

ShipmentRequest = {
    "service": "express",
    "shipper": {
        "company_name": "Shipper Company",
        "person_name": "John Doe",
        "phone_number": "1234567890",
        "address_line1": "123 Shipper St",
        "address_line2": "Suite 100",
        "city": "Shipper City",
        "state_code": "CA",
        "country_code": "US",
        "postal_code": "12345"
    },
    "recipient": {
        "company_name": "Recipient Company",
        "person_name": "Jane Smith",
        "phone_number": "0987654321",
        "address_line1": "456 Recipient Ave",
        "address_line2": "Apt 200",
        "city": "Recipient City",
        "state_code": "NY",
        "country_code": "US",
        "postal_code": "67890"
    },
    "parcels": [
        {
            "weight": 10.0,
            "weight_unit": "lb",
            "length": 10.0,
            "width": 10.0,
            "height": 10.0,
            "dimension_unit": "in"
        }
    ]
}

ShipmentCancelRequest = {
    "shipment_identifier": "794947717776",
}

ShipmentResponse = """{
    "status": {
        "done": true,
        "total": 1,
        "complete": 1
    },
    "shipments": [
        {
            "carrier_name": "Freightcom",
            "service_name": "express",
            "service_id": "express",
            "tracking_number": "123456789",
            "total": {
                "currency": "CAD",
                "value": 225.47
            },
            "base": {
                "currency": "CAD",
                "value": 200.00
            },
            "surcharges": [
                {
                    "type": "fuel",
                    "amount": {
                        "currency": "CAD",
                        "value": 25.47
                    }
                }
            ],
            "taxes": [],
            "transit_time_days": 5,
            "transit_time_not_available": false
        }
    ]
}"""

ShipmentCancelResponse = """{
    "status": {
        "done": true,
        "total": 1,
        "complete": 1
    },
    "shipments": [
        {
            "carrier_name": "Freightcom",
            "service_name": "express",
            "service_id": "express",
            "tracking_number": "123456789",
            "total": {
                "currency": "CAD",
                "value": 0.0
            },
            "base": {
                "currency": "CAD",
                "value": 0.0
            },
            "surcharges": [],
            "taxes": [],
            "transit_time_days": 5,
            "transit_time_not_available": false
        }
    ]
}"""
