
import unittest
from unittest.mock import patch, ANY
from .fixture import gateway

import karrio
import karrio.lib as lib
import karrio.core.models as models


class Testfreightcomv2Rating(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.RateRequest = models.RateRequest(**RatePayload)
    def test_create_rate_request(self):
        request = gateway.mapper.create_rate_request(self.RateRequest)
        self.assertEqual(request.serialize(), RateRequest)

    def test_get_rate(self):
            with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
                mock.return_value = "{}"
                karrio.Rating.fetch(self.RateRequest).from_(gateway)
                self.assertEqual(
                    mock.call_args[1]["url"],
                    f"{gateway.settings.server_url}/rate"
                )

    def test_parse_rate_response(self):
        with patch("karrio.mappers.freightcomv2.proxy.lib.request") as mock:
            mock.return_value = lib.Serializable(RateResponse)
            parsed_response = karrio.Rating.fetch(self.RateRequest).from_(gateway).parse()
            # Flatten the parsed response
            rates, errors = parsed_response
            self.assertListEqual(lib.to_dict(rates), ParsedRateResponse)
            self.assertListEqual(lib.to_dict(errors), [])
if __name__ == "__main__":
    unittest.main()

RatePayload = {
        "shipper": {
            "company_name": "Shipper Company",
            "address_line1": "Shipper Company",
            "city": "Shipper City",
            "state_code": "CA",
            "postal_code": "90210",
            "country_code": "US"
        },
        "recipient": {
            "company_name": "Recipient Company",
            "address_line1": "456 Recipient Ave",
            "city": "Recipient City",
            "state_code": "NY",
            "postal_code": "10001",
            "country_code": "US"
        },
        "parcels": [
            {
                "length": 10.0,
                "width": 10.0,
                "height": 10.0,
                "weight": 5.0
            }
        ],
        "services": [],
        "options": {}
    }
RateRequest = {
        "details": {
            "origin": {
            "name": "Shipper Company",
            "address": {
                "address_line_1": "Shipper Company",
                "unit_number": "",
                "city": "Shipper City",
                "region":  "CA",
                "country": "US",
                "postal_code": "90210"
            },
            "phone_number": {
                "number": None,
                "extension": ""
            },
            "contact_name": "Shipper Company"
            },
            "destination": {
            "name": "Recipient Company",
            "address": {
                "address_line_1": "456 Recipient Ave",
                "unit_number": "",
                "city": "Recipient City",
                "region": "NY",
                "country": "US",
                "postal_code": "10001"
            },
            "contact_name": "Recipient Company"
            },
            "expected_ship_date": {
            "year": 2024,
            "month": 6,
            "day": 6
            },
            "packaging_type": "pallet",
            "packaging_properties": {
            "pallet_type": "ltl",
            "has_stackable_pallets": False,
            "pallets": [
                {
                "measurements": {
                    "weight": {
                    "unit": "lb",
                    "value": 20
                    },
                    "cuboid": {
                    "unit": "in",
                    "l": 30,
                    "w": 20,
                    "h": 20
                    }
                },
                "description": "test",
                "contents_type": "pallet",
                "num_pieces": 1
                }
            ]
            },
        }
}



ParsedRateResponse = [
    {
        "carrier_id": "freightcomv2",
        "carrier_name": "Apex",
        "service": "apex.standard",
        "total_charge": 10475.0,
        "currency": "CAD",
        "transit_days": 1,
        "extra_charges": [
            {"name": "fuel", "amount": 1962.0, "currency": "CAD"},
            {"name": "tax-hst-on", "amount": 1205.0, "currency": "CAD"}
        ],
        "meta": {
            "service_id": "apex.standard",
            "valid_until": {
                "year": 2024,
                "month": 6,
                "day": 18
            },
            "carrier_name": "Apex",
            "service_name": "Standard"
        }
    }
]

RateResponse ={
    "status": {
        "done": True,
        "total": 1,
        "complete": 1
    },
    "rates": [
        {
            "service_id": "apex.standard",
            "valid_until": {
                "year": 2024,
                "month": 6,
                "day": 18
            },
            "total": {
                "value": "10475",
                "currency": "CAD"
            },
            "base": {
                "value": "7308",
                "currency": "CAD"
            },
            "surcharges": [
                {
                    "type": "fuel",
                    "amount": {
                        "value": "1962",
                        "currency": "CAD"
                    }
                }
            ],
            "taxes": [
                {
                    "type": "tax-hst-on",
                    "amount": {
                        "value": "1205",
                        "currency": "CAD"
                    }
                }
            ],
            "transit_time_days": 1,
            "transit_time_not_available": False,
            "carrier_name": "Apex",
            "service_name": "Standard"
        }
    ]
}
