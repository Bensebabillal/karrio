
import typing
import karrio.lib as lib
import karrio.core.units as units
import karrio.core.models as models
import karrio.providers.freightcom_com_v2.error as error
import karrio.providers.freightcom_com_v2.utils as provider_utils
import karrio.providers.freightcom_com_v2.units as provider_units


def parse_rate_response(
    _response: lib.Deserializable[dict],
    settings: provider_utils.Settings,
) -> typing.Tuple[typing.List[models.RateDetails], typing.List[models.Message]]:
    response = _response.deserialize()

    messages = error.parse_error_response(response, settings)
    rates = [_extract_details(rate, settings) for rate in response]

    return rates, messages


def _extract_details(
    data: dict,
    settings: provider_utils.Settings,
) -> models.RateDetails:
    rate = None  # parse carrier rate type

    return models.RateDetails(
        carrier_id=settings.carrier_id,
        carrier_name=settings.carrier_name,
        service="",  # extract service from rate
        total_charge=0.0,  # extract the rate total rate cost
        currency="",  # extract the rate pricing currency
        transit_days=0,  # extract the rate transit days
        meta=dict(
            service_name="",  # extract the rate service human readable name
        ),
    )


def rate_request(
    payload: models.RateRequest,
    settings: provider_utils.Settings,
) -> lib.Serializable:
    packages = lib.to_packages(payload.parcels)  # preprocess the request parcels
    services = lib.to_services(payload.services, units.ShippingService)  # preprocess the request services
    options = lib.to_shipping_options(
        payload.options,
        package_options=packages.options,
    )   # preprocess the request options

    request = None  # map data to convert karrio model to freightcom_com_v2 specific type

    return lib.Serializable(request)


def rate_request(payload: models.RateRequest, settings: provider_utils.Settings) -> lib.Serializable:
    packages = lib.to_packages(payload.parcels)
    services = lib.to_services(payload.services, provider_units.ShippingService)
    options = lib.to_shipping_options(
        payload.options,
        package_options=packages.options,
    )

    origin = {
        "name": payload.shipper.company_name,
        "address": {
            "address_line_1": payload.shipper.address_line1,
            "address_line_2": payload.shipper.address_line2,
            "unit_number": payload.shipper.street_number,
            "city": payload.shipper.city,
            "region": payload.shipper.state_code,
            "country": payload.shipper.country_code,
            "postal_code": payload.shipper.postal_code
        },
        "residential": options.residential_delivery.state == provider_units.ResidentialDeliveryType.YES,
        "tailgate_required": options.tailgate.state == provider_units.TailgateRequiredType.YES,
        "instructions": options.special_instructions.state,
        "contact_name": payload.shipper.person_name,
        "phone_number": {
            "number": payload.shipper.phone_number,
            "extension": payload.shipper.phone_extension
        },
        "email_addresses": [payload.shipper.email_address]
    }

    destination = {
        "name": payload.recipient.company_name,
        "address": {
            "address_line_1": payload.recipient.address_line1,
            "address_line_2": payload.recipient.address_line2,
            "unit_number": payload.recipient.street_number,
            "city": payload.recipient.city,
            "region": payload.recipient.state_code,
            "country": payload.recipient.country_code,
            "postal_code": payload.recipient.postal_code
        },
        "residential": options.residential_delivery.state == provider_units.ResidentialDeliveryType.YES,
        "tailgate_required": options.tailgate.state == provider_units.TailgateRequiredType.YES,
        "instructions": options.special_instructions.state,
        "contact_name": payload.recipient.person_name,
        "phone_number": {
            "number": payload.recipient.phone_number,
            "extension": payload.recipient.phone_extension
        },
        "email_addresses": [payload.recipient.email_address]
    }

    pallets = [
        {
            "measurements": {
                "unit": pkg.weight_unit,
                "value": pkg.weight
            },
            "cuboid": {
                "unit": pkg.dimension_unit,
                "l": pkg.length,
                "w": pkg.width,
                "h": pkg.height
            },
            "description": pkg.description,
            "freight_class": pkg.freight_class,
            "nmfc": pkg.nmfc,
            "contents_type": pkg.contents_type,
            "num_pieces": pkg.num_pieces
        } for pkg in packages
    ]

    packaging_properties = {
        "pallet_type": options.pallet_type.state,
        "has_stackable_pallets": options.stackable_pallets.state,
        "dangerous_goods": options.dangerous_goods.state,
        "dangerous_goods_details": {
            "packaging_group": options.dangerous_goods_packaging_group.state,
            "goods_class": options.dangerous_goods_class.state,
            "description": options.dangerous_goods_description.state,
            "united_nations_number": options.dangerous_goods_un_number.state,
            "emergency_contact_name": options.emergency_contact_name.state,
            "emergency_contact_phone_number": {
                "number": options.emergency_contact_phone_number.state,
                "extension": options.emergency_contact_phone_extension.state
            }
        } if options.dangerous_goods.state else None,
        "pallets": pallets,
        "pallet_service_details": {
            "limited_access_delivery_type": options.limited_access_delivery_type.state,
            "limited_access_delivery_other_name": options.limited_access_delivery_other_name.state,
            "in_bond": options.in_bond.state,
            "in_bond_details": {
                "type": options.in_bond_type.state,
                "name": options.in_bond_name.state,
                "address": options.in_bond_address.state,
                "contact_method": options.in_bond_contact_method.state,
                "contact_email_address": options.in_bond_contact_email.state,
                "contact_phone_number": {
                    "number": options.in_bond_contact_phone.state,
                    "extension": options.in_bond_contact_phone_extension.state
                }
            } if options.in_bond.state else None,
            "appointment_delivery": options.appointment_delivery.state,
            "protect_from_freeze": options.protect_from_freeze.state,
            "threshold_pickup": options.threshold_pickup.state,
            "threshold_delivery": options.threshold_delivery.state
        }
    }

    shipping_details = {
        "origin": origin,
        "destination": destination,
        "expected_ship_date": {
            "year": payload.ship_date.year,
            "month": payload.ship_date.month,
            "day": payload.ship_date.day
        },
        "packaging_type": options.packaging_type.state,
        "packaging_properties": packaging_properties,
        "insurance": {
            "type": options.insurance_type.state,
            "total_cost": {
                "unit": options.insurance_currency.state,
                "value": options.insurance_value.state
            }
        } if options.insurance_type.state else None
    }

    request = {
        "services": services,
        "excluded_services": [],
        "details": shipping_details
    }

    return lib.Serializable(request)
