import unittest
from unittest.mock import patch, ANY
from .fixture import gateway
import karrio
import karrio.lib as lib
import karrio.core.models as models


class Testfreightcomv2Shipping(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.ShipmentRequest = models.ShipmentRequest(**ShipmentPayload)
        self.ShipmentCancelRequest = models.ShipmentCancelRequest(**ShipmentCancelPayload)

    # def test_create_shipment_request(self):
    #     request = gateway.mapper.create_shipment_request(self.ShipmentRequest)
    #     print(f"\n\nrequest.serialize(): {request.serialize()}\n\n")
    #     print(f"\n\nShipmentRequest: {ShipmentRequest}\n\n")
    #     self.assertEqual(request.serialize(), self.ShipmentRequest)


    def test_create_cancel_shipment_request(self):
        request = gateway.mapper.create_cancel_shipment_request(self.ShipmentCancelRequest)
        self.assertEqual(request.serialize(), ShipmentCancelRequest)

    def test_create_shipment(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
            mock.return_value = "{}"
            karrio.Shipment.create(self.ShipmentRequest).from_(gateway)
            self.assertEqual(
                mock.call_args[1]["url"],
                f"{gateway.settings.server_url}/shipment",
            )

    def test_cancel_shipment(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
            mock.return_value = "{}"
            karrio.Shipment.cancel(self.ShipmentCancelRequest).from_(gateway)
            self.assertEqual(
                mock.call_args[1]["url"],
                f"{gateway.settings.server_url}/shipment/{self.ShipmentCancelRequest.shipment_identifier}",
            )

    def test_parse_shipment_response(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
            mock.return_value = ShipmentResponse
            parsed_response = (
                karrio.Shipment.create(self.ShipmentRequest).from_(gateway).parse()
            )
            self.assertListEqual(lib.to_dict(parsed_response), ParsedShipmentResponse)

    # def test_parse_shipment_response(self):
    #     with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
    #         mock.return_value = lib.Serializable(ShipmentResponse)
    #         parsed_response = (
    #             karrio.Shipment.create(self.ShipmentRequest).from_(gateway).parse()
    #         )
    #         self.assertListEqual(lib.to_dict(parsed_response), ParsedShipmentResponse)


    def test_parse_cancel_shipment_response(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
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
    "service": "apex.standard",
    "shipper": {
        "address_line1": "184 Rue Jean-Proulx",
        "city": "Gatineau",
        "state_code": "QC",
        "postal_code": "J8Z 1V8",
        "country_code": "CA",
        "person_name": "Gauvin2",
        "phone_number": "8002685201",
    },
    "recipient": {
        "address_line1": "200 University Ave W",
        "city": "Waterloo",
        "state_code": "ON",
        "postal_code": "N2L 3G1",
        "country_code": "CA",
        "person_name": "Gauvin",
        "phone_number": "8002685201",
    },
    "parcels": [
        {
            "length": 30,
            "width": 20,
            "height": 10,
            "weight": 20,
            "packaging_type": "pallet"
        }
    ]
}

ShipmentCancelPayload = {
    "shipment_identifier": "794947717776",
}

ParsedShipmentResponse = [
    {
        "carrier_id": "freightcomv2",
        "carrier_name": "Apex",
        "shipment_identifier": "CQvDuMXWFm6dB7lgwAYTZdZdlQa7rKbd",
        "label_type": "pdf",
        "tracking_number": "",
        "tracking_url": "",
        "selected_rate": {
            "service": "apex.standard",
            "total_charge": 11859.0,
            "currency": "CAD",
            "transit_days": 1,
            "extra_charges": [
                {"name": "fuel", "amount": 2612.0, "currency": "CAD"},
                {"name": "tax-hst-on", "amount": 1364.0, "currency": "CAD"}
            ],
            "meta": {
                "carrier_name": "Apex",
                "service_id": "apex.standard",
                "service_name": "Standard",
                "valid_until": {"year": 2024, "month": 6, "day": 17}
            }
        },
        "label_url": "https://s3.us-east-2.amazonaws.com/ssd-test-external/labels/4402YXLfxDciLyN08JosAWVCV1BJ8j8D/Ei8cUXLsB59aecNDOMypUrT5ZjNzggJd/shipping-label-19935415-BOL.pdf"
    }
]

ParsedCancelShipmentResponse = [
    {
        "carrier_id": "freightcomv2",
        "carrier_name": "Freightcom",
        "success": True,
        "operation": "Cancel Shipment",
        "messages": []
    }
]

ShipmentRequest = {
    "service": "apex.standard",
    "shipper": {
        "address_line1": "184 Rue Jean-Proulx",
        "city": "Gatineau",
        "state_code": "QC",
        "postal_code": "J8Z 1V8",
        "country_code": "CA",
        "person_name": "Gauvin2",
        "phone_number": "8002685201",
    },
    "recipient": {
        "address_line1": "200 University Ave W",
        "city": "Waterloo",
        "state_code": "ON",
        "postal_code": "N2L 3G1",
        "country_code": "CA",
        "person_name": "Gauvin",
        "phone_number": "8002685201",
    },
    "parcels": [
        {
            "length": 30,
            "width": 20,
            "height": 10,
            "weight": 20,
            "packaging_type": "pallet"
        }
    ]
}

ShipmentCancelRequest = {
    "shipment_identifier": "794947717776",
}

ShipmentResponse = """
{
    "shipment": {
        "id": "O5ah4SE9NP7HQmpn924dJWthUltGFveE",
        "tracking_number": "string",
        "label_url": "string",
        "shipment_cost": {
            "currency": "CAD",
            "amount": 10475.0
        }
    }
}
"""

ShipmentCancelResponse = """
{
    "success": true
}
"""
