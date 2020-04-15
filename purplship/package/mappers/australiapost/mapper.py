from typing import List, Tuple
from pyaustraliapost.shipping_price_request import ShippingPriceRequest
from purplship.carriers.australiapost.shipping import (
    shipping_price_request,
    parse_shipping_price_response,
    track_items_request,
    parse_track_items_response,
)
from purplship.core.utils.serializable import Deserializable, Serializable
from purplship.package.mapper import Mapper as BaseMapper
from purplship.core.models import (
    RateRequest,
    TrackingRequest,
    Message,
    RateDetails,
    TrackingDetails,
)
from purplship.package.mappers.australiapost.settings import Settings


class Mapper(BaseMapper):
    settings: Settings

    """Request Mappers"""

    def create_rate_request(
        self, payload: RateRequest
    ) -> Serializable[ShippingPriceRequest]:
        return shipping_price_request(payload)

    def create_tracking_request(
        self, payload: TrackingRequest
    ) -> Serializable[List[str]]:
        return track_items_request(payload)

    """Response Parsers"""

    def parse_rate_response(
        self, response: Deserializable[str]
    ) -> Tuple[List[RateDetails], List[Message]]:
        return parse_shipping_price_response(response.deserialize(), self.settings)

    def parse_tracking_response(
        self, response: Deserializable[str]
    ) -> Tuple[List[TrackingDetails], List[Message]]:
        return parse_track_items_response(response.deserialize(), self.settings)