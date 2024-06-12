
import datetime
import typing
import karrio.lib as lib
import karrio.core.units as units
import karrio.core.models as models
import karrio.providers.freightcomv2.error as error
import karrio.providers.freightcomv2.utils as provider_utils
import karrio.providers.freightcomv2.units as provider_units

def parse_shipment_response(
    _response: lib.Deserializable[dict], settings: provider_utils.Settings
) -> typing.Tuple[typing.List[models.ShipmentDetails], typing.List[models.Message]]:
    response_data = _response.deserialize()

    messages = error.parse_error_response(response_data, settings)
    shipment = response_data.get("shipment")

    if shipment:
        shipment_details = _extract_shipment_details(shipment, settings)
        return [shipment_details], messages

    return [], messages


def _extract_shipment_details(
    shipment: dict,
    settings: provider_utils.Settings
) -> models.ShipmentDetails:
    return models.ShipmentDetails(
        carrier_id=settings.carrier_id,
        carrier_name=settings.carrier_name,
        shipment_identifier=shipment.get("id"),
        label_type=shipment["labels"][0]["format"] if shipment.get("labels") else None,
        tracking_number=shipment.get("primary_tracking_number"),
        tracking_url=shipment.get("tracking_url"),
        selected_rate=models.RateDetails(
            service=shipment["rate"]["service_id"],
            total_charge=lib.to_money(shipment["rate"]["total"]["value"], shipment["rate"]["total"]["currency"]),
            currency=shipment["rate"]["total"]["currency"],
            transit_days=shipment["rate"]["transit_time_days"],
            extra_charges=[
                models.ChargeDetails(
                    name=surcharge["type"],
                    amount=lib.to_money(surcharge["amount"]["value"], surcharge["amount"]["currency"]),
                    currency=surcharge["amount"]["currency"]
                )
                for surcharge in shipment["rate"]["surcharges"]
            ],
            meta={
                "carrier_name": shipment["rate"]["carrier_name"],
                "service_name": shipment["rate"]["service_name"],
                "valid_until": shipment["rate"]["valid_until"]
            }
        ),
        label_url=shipment["labels"][0]["url"] if shipment.get("labels") else None,
    )

def shipment_request(
    payload: models.ShipmentRequest,
    settings: provider_utils.Settings,
) -> lib.Serializable:
    print(f"shipment request: {payload}")
    payment_method_id = "RfxtDWXCMLCNPdeTSQcoMrTXyH7cZV5n"
    unique_id = settings._generate_unique_id("GoL", 15)
    packages = lib.to_packages(payload.parcels)  # preprocess the request parcels
    service = provider_units.ShippingService.map(payload.service).value_or_key  # preprocess the request services
    options = lib.to_shipping_options(
        payload.options,
        package_options=packages.options,
    )   # preprocess the request options

    def get_address(contact):
        return {
            "name": contact.person_name,
            "address": {
                "address_line_1": contact.address_line1,
                "unit_number": contact.address_line2,
                "city": contact.city,
                "region": contact.state_code,
                "country": contact.country_code,
                "postal_code": contact.postal_code
            },
            "phone_number": {
                "number": contact.phone_number
            },
            "contact_name": contact.person_name
        }
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    request = {
        "unique_id": unique_id,
        "payment_method_id": payment_method_id,
        "service_id": service,
        "details": {
            "origin": get_address(payload.shipper),
            "destination": get_address(payload.recipient),
            "expected_ship_date": {
                "year": tomorrow.year,
                "month": tomorrow.month,
                "day": tomorrow.day
            },
            "packaging_type": "pallet",
            "packaging_properties": {
                "pallet_type": "ltl",
                "pallets": [
                    {
                        "measurements": {
                            "cuboid": {
                                "l": packages[0].length,
                                "w": packages[0].width,
                                "h": packages[0].height,
                                "unit": "in"
                            },
                            "weight": {
                                "value": packages[0].weight,
                                "unit": "lb"
                            }
                        },
                        "description": "test",
                        "contents_type": "pallet",
                        "num_pieces": packages[0].items
                    }
                ]
            }
        },
        "dispatch_details": {
            "date": {
                "year": tomorrow.year,
                "month": tomorrow.month,
                "day": tomorrow.day
            }
        }
    }

    return lib.Serializable(request)
