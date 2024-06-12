
import typing
import karrio.lib as lib
import karrio.core.units as units
import karrio.core.models as models
import karrio.providers.freightcomv2.error as error
import karrio.providers.freightcomv2.utils as provider_utils
import karrio.providers.freightcomv2.units as provider_units


def parse_tracking_response(
    _response: lib.Deserializable[typing.Tuple[str, dict]],
    settings: provider_utils.Settings,
) -> typing.Tuple[typing.List[models.TrackingDetails], typing.List[models.Message]]:
    shipment_id, response = _response.deserialize()

    messages = error.parse_error_response(response, settings)
    tracking_details = _extract_details(response, settings, shipment_id)

    return [tracking_details], messages

def _extract_details(
    data: dict,
    settings: provider_utils.Settings,
    tracking_number: str,
) -> models.TrackingDetails:
    events = data.get("events", [])

    return models.TrackingDetails(
        carrier_id=settings.carrier_id,
        carrier_name=settings.carrier_name,
        tracking_number=tracking_number,
        events=[
            models.TrackingEvent(
                date=lib.fdate(event["when"], "%Y-%m-%dT%H:%M:%S"),
                description=event.get("message", ""),
                code=event.get("type", ""),
                time=lib.ftime(event["when"], "%Y-%m-%dT%H:%M:%S"),
                location=", ".join(filter(None, [
                    event["where"].get("city"),
                    event["where"].get("region"),
                    event["where"].get("country")
                ])),
            )
            for event in events
        ],
        estimated_delivery=None,
        delivered=any(event["type"] == "delivered" for event in events),
    )

def tracking_request(
    payload: models.TrackingRequest,
    settings: provider_utils.Settings,
) -> lib.Serializable:
    request = {
        "shipment_id": payload.shipment_id
    }

    return lib.Serializable(request)


# def parse_tracking_response(
#     _response: lib.Deserializable[typing.List[typing.Tuple[str, dict]]],
#     settings: provider_utils.Settings,
# ) -> typing.Tuple[typing.List[models.TrackingDetails], typing.List[models.Message]]:
#     responses = _response.deserialize()

#     messages = sum(
#         [
#             error.parse_error_response(response, settings, tracking_number=_)
#             for _, response in responses
#         ],
#         start=[],
#     )
#     tracking_details = [_extract_details(details, settings) for _, details in responses]

#     return tracking_details, messages


# def parse_tracking_response(
#     _response: lib.Deserializable[typing.List[typing.Tuple[str, dict]]],
#     settings: provider_utils.Settings,
# ) -> typing.Tuple[typing.List[models.TrackingDetails], typing.List[models.Message]]:
#     responses = _response.deserialize()

#     messages = sum(
#         [
#             error.parse_error_response(response, settings, tracking_number=_)
#             for _, response in responses
#         ],
#         start=[],
#     )
#     tracking_details = [_extract_details(details, settings, tracking_number) for tracking_number, details in responses]

#     return tracking_details, messages
