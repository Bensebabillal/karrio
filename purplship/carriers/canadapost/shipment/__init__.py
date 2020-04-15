from typing import Tuple, List
from purplship.core.utils.xml import Element
from purplship.core.utils.serializable import Serializable
from purplship.core.models import ShipmentRequest, ShipmentDetails, Message
from purplship.carriers.canadapost.utils import Settings
from purplship.carriers.canadapost.shipment.contract_shipment import (
    parse_contract_shipment_response,
    contract_shipment_request,
)
from purplship.carriers.canadapost.shipment.non_contract_shipment import (
    parse_non_contract_shipment_response,
    non_contract_shipment_request,
)


def parse_shipment_response(
    response: Element, settings: Settings
) -> Tuple[ShipmentDetails, List[Message]]:
    if settings.contract_id is None or settings.contract_id == "":
        return parse_non_contract_shipment_response(response, settings)
    return parse_contract_shipment_response(response, settings)


def shipment_request(
    payload: ShipmentRequest, settings: Settings
) -> Serializable[Element]:
    if settings.contract_id is None or settings.contract_id == "":
        return non_contract_shipment_request(payload, settings)
    return contract_shipment_request(payload, settings)