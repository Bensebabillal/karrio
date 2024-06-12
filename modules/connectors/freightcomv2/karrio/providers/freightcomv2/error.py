
import typing
import karrio.lib as lib
import karrio.core.models as models
import karrio.providers.freightcomv2.utils as provider_utils

def parse_error_response(
    response: dict,
    settings: provider_utils.Settings,
    **kwargs,
) -> typing.List[models.Message]:
    errors = response.get("data", {})
    message = response.get("message", "Unknown error")

    return [
        models.Message(
            carrier_id=settings.carrier_id,
            carrier_name=settings.carrier_name,
            code=field,
            message=description,
            details={**kwargs},
        )
        for field, description in errors.items()
    ] or [
        models.Message(
            carrier_id=settings.carrier_id,
            carrier_name=settings.carrier_name,
            code="unknown_error",
            message=message,
            details={**kwargs},
        )
    ]
