import enum
import base64
import typing
import functools
import strawberry
import dataclasses
from django import conf as django
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _

import karrio.server.manager.models as manager
import karrio.server.providers.models as providers
import karrio.server.core.permissions as permissions
import karrio.server.core.serializers as serializers


Cursor = str
T = typing.TypeVar("T")
GenericType = typing.TypeVar("GenericType")

JSON: typing.Any = strawberry.scalar(
    typing.NewType("JSON", object),
    description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
)

CurrencyCodeEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("CurrencyCodeEnum", serializers.CURRENCIES)
)
CountryCodeEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("CountryCodeEnum", serializers.COUNTRIES)
)
DimensionUnitEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("DimensionUnitEnum", serializers.DIMENSION_UNIT)
)
WeightUnitEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("WeightUnitEnum", serializers.WEIGHT_UNIT)
)
CustomsContentTypeEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("CustomsContentTypeEnum", serializers.CUSTOMS_CONTENT_TYPE)
)
IncotermCodeEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("IncotermCodeEnum", serializers.INCOTERMS)
)
PaidByEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("PaidByEnum", serializers.PAYMENT_TYPES)
)
LabelTypeEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("LabelTypeEnum", serializers.LABEL_TYPES)
)
LabelTemplateTypeEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("LabelTemplateTypeEnum", serializers.LABEL_TEMPLATE_TYPES)
)
ShipmentStatusEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("ShipmentStatusEnum", serializers.SHIPMENT_STATUS)
)
TrackerStatusEnum: typing.Any = strawberry.enum(  # type: ignore
    enum.Enum("TrackerStatusEnum", serializers.TRACKER_STATUS)
)


def metadata_object_types() -> enum.Enum:
    _types = [
        ("carrier", providers.Carrier),
        ("commodity", manager.Commodity),
        ("shipment", manager.Shipment),
        ("tracker", manager.Tracking),
    ]

    if django.settings.ORDERS_MANAGEMENT:
        import karrio.server.orders.models as orders

        _types.append(("order", orders.Order))

    if django.settings.APPS_MANAGEMENT:
        import karrio.server.apps.models as apps

        _types.append(("app", apps.App))

    return enum.Enum("MetadataObjectType", _types)


MetadataObjectTypeEnum: typing.Any = strawberry.enum(metadata_object_types())  # type: ignore

def authentication_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        *__, info = args
        if info.context.request.user.is_anonymous:
            raise exceptions.AuthenticationFailed(
                _("You are not authenticated"), code="authentication_required"
            )

        if not info.context.request.user.is_verified():
            raise exceptions.AuthenticationFailed(
                _("Authentication Token not verified"), code="two_factor_required"
            )

        return func(*args, **kwargs)

    return wrapper


def password_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        *__, info = args
        password = kwargs.get("password")

        if not info.context.request.user.check_password(password):
            raise exceptions.ValidationError({"password": "Invalid password"})

        return func(*args, **kwargs)

    return wrapper


def authorization_required(keys: typing.List[str] = None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            *__, info = args
            permissions.check_permissions(
                context=info.context.request,
                keys=keys or [],
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


@strawberry.type
class ErrorType:
    field: str
    messages: typing.List[str]

    @staticmethod
    def from_errors(errors):
        return []


@strawberry.input
class BaseInput:
    def pagination(self) -> typing.Dict[str, typing.Any]:
        return {
            k: v
            for k, v in dataclasses.asdict(self).items()
            if k in ["offset", "before", "after", "first", "last"]
        }

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            k: v
            for k, v in dataclasses.asdict(self).items()
            if v is not strawberry.UNSET
        }


@strawberry.type
class BaseMutation:
    errors: typing.Optional[typing.List[ErrorType]] = None


@dataclasses.dataclass
@strawberry.type
class Connection(typing.Generic[GenericType]):
    """Represents a paginated relationship between two entities
    This pattern is used when the relationship itself has attributes.
    In a Facebook-based domain example, a friendship between two people
    would be a connection that might have a `friendshipStartTime`
    """

    page_info: "PageInfo"
    edges: typing.List["Edge[GenericType]"]


@dataclasses.dataclass
@strawberry.type
class PageInfo:
    """Pagination context to navigate objects with cursor-based pagination
    Instead of classic offset pagination via `page` and `limit` parameters,
    here we have a cursor of the last object and we fetch items starting from that one
    Read more at:
        - https://graphql.org/learn/pagination/#pagination-and-edges
        - https://relay.dev/graphql/connections.htm
    """

    has_next_page: bool
    has_previous_page: bool
    start_cursor: typing.Optional[str]
    end_cursor: typing.Optional[str]


@dataclasses.dataclass
@strawberry.type
class Edge(typing.Generic[GenericType]):
    """An edge may contain additional information of the relationship. This is the trivial case"""

    node: GenericType
    cursor: str


@strawberry.input
class Paginated(BaseInput):
    offset: typing.Optional[int] = strawberry.UNSET
    first: typing.Optional[int] = strawberry.UNSET


def build_entity_cursor(entity: T):
    """Adapt this method to build an *opaque* ID from an instance"""
    entityid = f"{getattr(entity, 'id', id(entity))}".encode("utf-8")
    return base64.b64encode(entityid).decode()


def paginated_connection(
    queryset,
    first: int = 25,
    offset: int = 0,
) -> Connection[T]:
    """A non-trivial implementation should efficiently fetch only
    the necessary books after the offset.
    For simplicity, here we build the list and then slice it accordingly
    """

    # Fetch the requested results plus one, just to calculate `has_next_page`
    # fmt: off
    results = queryset[offset:offset+first+1]
    # fmt: on

    edges: typing.List[typing.Any] = [
        Edge(node=typing.cast(T, entity), cursor=build_entity_cursor(entity))
        for entity in results
    ]
    return Connection(
        page_info=PageInfo(
            has_previous_page=False,
            has_next_page=len(results) > first,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-2].cursor if len(edges) > 1 else None,
        ),
        edges=edges[:-1],
    )
