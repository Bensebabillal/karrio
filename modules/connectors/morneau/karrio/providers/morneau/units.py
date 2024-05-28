import karrio.core.units as units
import karrio.lib as lib


class PackagingType(lib.StrEnum):
    """ Carrier specific packaging type """
    PACKAGE = "Pallet"
    """ Unified Packaging type mapping """
    pallet = PACKAGE


class ShippingService(lib.Enum):
    """ Carrier specific services """
    morneau_standard_service = "Groupe Morneau Standard Service"


class ShippingOption(lib.Enum):
    """ Carrier specific options """
    morneau_dangerous_good = lib.OptionEnum("DangerousGood", bool) # DangerousGood : dangerous goods are shipped
    morneau_heat = lib.OptionEnum("Heat", bool)  # Heat : Heating service
    morneau_tail_gate = lib.OptionEnum("Tailgate", bool) # Tailgate : a tail gate need to be lifted
    morneau_straigth_body_truck = lib.OptionEnum("StraigthBodyTruck", bool)  # StraigthBodyTruck : straight body truck needed
    morneau_barn_doors = lib.OptionEnum("BarnDoors", bool)  # BarnDoors : Pickup barn doors
    morneau_frozen = lib.OptionEnum("Frozen", bool) # Frozen : goods that need to be kept frozen are shipped
    morneau_fresh = lib.OptionEnum("Fresh", bool) # Fresh : goods that need to be kept freesh are shipped
    morneau_dry = lib.OptionEnum("Dry", bool) # Dry service
    morneau_flatbed = lib.OptionEnum("Flatbed", bool) # Flatbed : flat bed service
    morneau_pup_trailer = lib.OptionEnum("PupTrailer", bool) # PupTrailer : pup trailer needed
    morneau_food=lib.OptionEnum("Food", bool)  # Food : foods are shipped (special handling on our side)

    #mapping
    dangerous_good = morneau_dangerous_good# DangerousGood : dangerous goods are shipped

    """ Unified Option type mapping """
    # insurance = morneau_coverage  #  maps unified karrio option to carrier specific

class ConnectionConfig(lib.Enum):
    label_type = lib.OptionEnum("label_type")
    skip_service_filter = lib.OptionEnum("skip_service_filter")
    shipping_options = lib.OptionEnum("shipping_options", list)
    shipping_services = lib.OptionEnum("shipping_services", list)
    commodity_types = lib.OptionEnum("commodity_types", list)
    packaging_types = lib.OptionEnum("packaging_types", list)


@property
def connection_config(self) -> lib.units.Options:
    from karrio.providers.morneau.units import ConnectionConfig

    return lib.to_connection_config(
        self.config or {},
        option_type=ConnectionConfig,
    )


def shipping_options_initializer(
    options: dict,
    package_options: units.ShippingOptions = None,
) -> units.ShippingOptions:
    """
    Apply default values to the given options.
    """

    if package_options is not None:
        options.update(package_options.content)

    def items_filter(key: str) -> bool:
          return key in ShippingOption  # type: ignore

     # Define carrier option filter.
    # def items_filter(key: str) -> bool:
    #      return key in ShippingOption and key not in CUSTOM_OPTIONS  # type:ignore

    # return units.ShippingOptions(
    #      _options, ShippingOption, items_filter=items_filter)

    return units.ShippingOptions(options, ShippingOption, items_filter=items_filter)


class TrackingStatus(lib.Enum):
    on_hold = ["on_hold"]
    delivered = ["delivered"]
    in_transit = ["in_transit"]
    delivery_failed = ["delivery_failed"]
    delivery_delayed = ["delivery_delayed"]
    out_for_delivery = ["out_for_delivery"]
    ready_for_pickup = ["ready_for_pickup"]


class ServiceType(lib.Enum):
    """ Carrier specific service types """
    tracking_service = ["tracking_service"]
    shipping_service = ["shipping_service"]
    rates_service = ["rates_service"]


class CommodityType(lib.Enum):
    """ Carrier specific Commodities types """
    rendezvous = ["RENDEZVOUS"]
    pcamlivr = ["PCAMLIVR"]
    home = ["HOME"]



CUSTOM_OPTIONS = [
    #ShippingOption.caller_id.name,
    #ShippingOption.division.name,

]
