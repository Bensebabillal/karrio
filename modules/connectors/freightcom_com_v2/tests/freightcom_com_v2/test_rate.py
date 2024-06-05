
import unittest
from unittest.mock import patch, ANY
from .fixture import gateway
import karrio
import karrio.lib as lib
import karrio.core.models as models
from karrio.providers.freightcom_com_v2.units import (
    ResidentialDeliveryType, TailgateRequiredType, PackagingType, PalletType, DangerousGoodsType,
    LimitedAccessDeliveryType, ContactMethodType, InsuranceType, SignatureRequirementType,
)

class TestFrieghtcomv2Rating(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.RateRequest = models.RateRequest(**RatePayload)
    def test_create_rate_request(self):
            request = gateway.mapper.create_rate_request(self.RateRequest)
            self.assertEqual(request.serialize(), RateRequest)

    def test_get_rate(self):
        with patch("karrio.mappers.freightcom_com_v2.proxy.lib.request") as mock:
            mock.return_value = "{}"
            karrio.Rating.fetch(self.RateRequest).from_(gateway)

            self.assertEqual(
                mock.call_args[1]["url"],
                f"{gateway.settings.rates_server_url}/rate"
            )

    def test_parse_rate_response(self):
        with patch("karrio.mappers.freightcom_com_v2.proxy.lib.request") as mock:
            mock.return_value = RateResponse
            parsed_response = karrio.Rating.fetch(self.RateRequest).from_(gateway).parse()
            self.assertListEqual(lib.to_dict(parsed_response), ParsedRateResponse)

if __name__ == "__main__":
    unittest.main()

RatePayload = {
    "shipper": {
        "company_name": "Shipper Company",
        "person_name": "John Doe",
        "phone_number": "1234567890",
        "phone_extension": "111",
        "email_address": "shipper@example.com",
        "address_line1": "123 Shipper St",
        "address_line2": "Suite 100",
        "street_number": "100",
        "city": "Shipper City",
        "state_code": "CA",
        "country_code": "US",
        "postal_code": "12345"
    },
    "recipient": {
        "company_name": "Recipient Company",
        "person_name": "Jane Smith",
        "phone_number": "0987654321",
        "phone_extension": "222",
        "email_address": "recipient@example.com",
        "address_line1": "456 Recipient Ave",
        "address_line2": "Apt 200",
        "street_number": "200",
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
    ],
    "services": ["express"],
    "options": {
        "residential_delivery": ResidentialDeliveryType.YES.value,
        "tailgate": TailgateRequiredType.YES.value,
        "special_instructions": "Leave at the front door",
        "ready_at_hour": 9,
        "ready_at_minute": 0,
        "ready_until_hour": 17,
        "ready_until_minute": 0,
        "signature_requirement": SignatureRequirementType.NOT_REQUIRED.value,
        "packaging_type": PackagingType.pallet.value,
        "pallet_type": PalletType.LTL.value,
        "stackable_pallets": True,
        "dangerous_goods": DangerousGoodsType.LIMITED_QUANTITY.value,
        "dangerous_goods_packaging_group": "II",
        "dangerous_goods_class": "3",
        "dangerous_goods_description": "Flammable liquid",
        "dangerous_goods_un_number": "1993",
        "emergency_contact_name": "John Emergency",
        "emergency_contact_phone_number": "1234567890",
        "emergency_contact_phone_extension": "123",
        "limited_access_delivery_type": LimitedAccessDeliveryType.CONSTRUCTION_SITE.value,
        "limited_access_delivery_other_name": "Other Site",
        "in_bond": True,
        "in_bond_type": "immediate-exportation",
        "in_bond_name": "In Bond Name",
        "in_bond_address": "In Bond Address",
        "in_bond_contact_method": ContactMethodType.EMAIL.value,
        "in_bond_contact_email": "inbond@example.com",
        "in_bond_contact_phone": "0987654321",
        "in_bond_contact_phone_extension": "321",
        "appointment_delivery": True,
        "protect_from_freeze": True,
        "threshold_pickup": True,
        "threshold_delivery": True,
        "insurance_type": InsuranceType.INTERNAL.value,
        "insurance_currency": "CAD",
        "insurance_value": 4250.0
    }
}

ParsedRateResponse = [
    {
        "carrier_id": "freightcom",
        "carrier_name": "Freightcom",
        "service": "express",
        "total_charge": 225.47,
        "transit_days": 5,
        "currency": "CAD"
    }
]

RateRequest = {
    "services": ["express"],
    "excluded_services": [],
    "details": {
        "origin": {
            "name": "Shipper Company",
            "address": {
                "address_line_1": "123 Shipper St",
                "address_line_2": "Suite 100",
                "unit_number": "100",
                "city": "Shipper City",
                "region": "CA",
                "country": "US",
                "postal_code": "12345"
            },
            "residential": True,
            "tailgate_required": True,
            "instructions": "Leave at the front door",
            "contact_name": "John Doe",
            "phone_number": {
                "number": "1234567890",
                "extension": "111"
            },
            "email_addresses": ["shipper@example.com"]
        },
        "destination": {
            "name": "Recipient Company",
            "address": {
                "address_line_1": "456 Recipient Ave",
                "address_line_2": "Apt 200",
                "unit_number": "200",
                "city": "Recipient City",
                "region": "NY",
                "country": "US",
                "postal_code": "67890"
            },
            "residential": True,
            "tailgate_required": True,
            "instructions": "Leave at the front door",
            "contact_name": "Jane Smith",
            "phone_number": {
                "number": "0987654321",
                "extension": "222"
            },
            "email_addresses": ["recipient@example.com"],
            "ready_at": {
                "hour": 9,
                "minute": 0
            },
            "ready_until": {
                "hour": 17,
                "minute": 0
            },
            "signature_requirement": "not-required"
        },
        "expected_ship_date": {
            "year": 2023,
            "month": 12,
            "day": 13
        },
        "packaging_type": "pallet",
        "packaging_properties": {
            "pallet_type": "ltl",
            "has_stackable_pallets": True,
            "dangerous_goods": "limited-quantity",
            "dangerous_goods_details": {
                "packaging_group": "II",
                "goods_class": "3",
                "description": "Flammable liquid",
                "united_nations_number": "1993",
                "emergency_contact_name": "John Emergency",
                "emergency_contact_phone_number": {
                    "number": "1234567890",
                    "extension": "123"
                }
            },
            "pallets": [
                {
                    "measurements": {
                        "weight": {
                            "unit": "lb",
                            "value": 10.0
                        },
                        "cuboid": {
                            "unit": "in",
                            "l": 10.0,
                            "w": 10.0,
                            "h": 10.0
                        }
                    },
                    "description": "Parcel",
                    "freight_class": "50",
                    "nmfc": "123456",
                    "contents_type": "general",
                    "num_pieces": 1
                }
            ],
            "pallet_service_details": {
                "limited_access_delivery_type": "construction-site",
                "limited_access_delivery_other_name": "Other Site",
                "in_bond": True,
                "in_bond_details": {
                    "type": "immediate-exportation",
                    "name": "In Bond Name",
                    "address": "In Bond Address",
                    "contact_method": "email-address",
                    "contact_email_address": "inbond@example.com",
                    "contact_phone_number": {
                        "number": "0987654321",
                        "extension": "321"
                    }
                },
                "appointment_delivery": True,
                "protect_from_freeze": True,
                "threshold_pickup": True,
                "threshold_delivery": True
            }
        },
        "insurance": {
            "type": "internal",
            "total_cost": {
                "currency": "CAD",
                "value": 4250.0
            }
        }
    }
}

RateResponse = """{
    "status": {
        "done": true,
        "total": 1,
        "complete": 1
    },
    "rates": [
        {
            "carrier_name": "Freightcom",
            "service_name": "express",
            "service_id": "express",
            "valid_until": {
                "year": 2024,
                "month": 1,
                "day": 13
            },
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
