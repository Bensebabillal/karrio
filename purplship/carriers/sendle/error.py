from typing import List
from pysendle.validation_error import ValidationError
from purplship.core.models import Message
from purplship.carriers.sendle.utils import Settings


def parse_error_response(response: List[dict], settings: Settings) -> List[Message]:
    errors: List[ValidationError] = [
        ValidationError(**e) for e in response if "error" in e
    ]
    return [
        Message(
            code=error.error,
            carrier=settings.carrier,
            carrier_name=settings.carrier_name,
            message=error.error_description,
            details=error.messages,
        )
        for error in errors
    ]