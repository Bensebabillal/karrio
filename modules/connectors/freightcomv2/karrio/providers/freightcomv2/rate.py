
import datetime
import typing
import karrio.lib as lib
import karrio.core.units as units
import karrio.core.models as models
import karrio.providers.freightcomv2.error as error
import karrio.providers.freightcomv2.utils as provider_utils
import karrio.providers.freightcomv2.units as provider_units


def parse_rate_response(
    _response: lib.Deserializable[dict],
    settings: provider_utils.Settings,
) -> typing.Tuple[typing.List[models.RateDetails], typing.List[models.Message]]:
    response = _response.deserialize()

    # Handle nested deserialization
    while isinstance(response, dict) and 'value' in response:
        response = response['value']

    rates = response.get("rates", [])

    if not rates:
        print("No rates found in response, processing errors...")  # Debugging statement
        return [], error.parse_error_response(response, settings)

    rate_details = [_extract_rate_details(rate, settings) for rate in rates]
    print(f"rate_len : {len(rate_details)}")
    return rate_details, []

def _extract_rate_details(rate: dict, settings: provider_utils.Settings) -> models.RateDetails:
    total_charge = rate["total"]["value"]
    currency = rate["total"]["currency"]
    surcharges = rate.get("surcharges", [])
    taxes = rate.get("taxes", [])

    extra_charges = [
        models.ChargeDetails(
            name=surcharge["type"],
            currency=surcharge["amount"]["currency"],
            amount=lib.to_decimal(surcharge["amount"]["value"])
        ) for surcharge in surcharges
    ] + [
        models.ChargeDetails(
            name=tax["type"],
            currency=tax["amount"]["currency"],
            amount=lib.to_decimal(tax["amount"]["value"])
        ) for tax in taxes
    ]

    return models.RateDetails(
        carrier_id=settings.carrier_id,
        carrier_name=rate.get("carrier_name", settings.carrier_name),
        service=rate["service_id"],
        total_charge=lib.to_decimal(total_charge),
        currency=currency,
        transit_days=rate.get("transit_time_days"),
        extra_charges=extra_charges,
        meta=dict(
            service_id=rate["service_id"],
            service_name=rate["service_name"],
            carrier_name=rate.get("carrier_name", settings.carrier_name),
            valid_until=rate["valid_until"]
        )
    )
def rate_request(
    payload: models.RateRequest,
    settings: provider_utils.Settings,
) -> lib.Serializable:
    packages = lib.to_packages(payload.parcels)  # preprocess the request parcels
    services = lib.to_services(payload.services, provider_units.ShippingService)  # preprocess the request services
    options = lib.to_shipping_options(
        payload.options,
        package_options=packages.options,
    )   # preprocess the request options
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    request = {
        "details": {
            "origin": {
            "name": payload.shipper.company_name,
            "address": {
                "address_line_1": payload.shipper.address_line1,
                "unit_number": "",
                "city": payload.shipper.city,
                "region": payload.shipper.state_code,
                "country": payload.shipper.country_code,
                "postal_code": payload.shipper.postal_code
            },
            "phone_number": {
                "number": payload.shipper.phone_number,
                "extension": ""
            },
            "contact_name": payload.shipper.company_name
            },
            "destination": {
            "name": payload.recipient.company_name,
            "address": {
                "address_line_1": payload.recipient.address_line1,
                "unit_number": "",
                "city": payload.recipient.city,
                "region": payload.recipient.state_code,
                "country": payload.recipient.country_code,
                "postal_code": payload.recipient.postal_code
            },
            "contact_name": payload.recipient.company_name
            },
             "expected_ship_date": {
                "year": tomorrow.year,
                "month": tomorrow.month,
                "day": tomorrow.day
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
    return lib.Serializable(request)
