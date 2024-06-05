
import karrio.lib as lib
import karrio.core.units as units

class PackagingType(lib.StrEnum):
    """ Carrier specific packaging type """
    PACKAGE = "PACKAGE"
    """ Unified Packaging type mapping """
    envelope = PACKAGE
    pakage = PACKAGE
    pallet = PACKAGE
    courier_pak = PACKAGE

class PalletType(lib.Enum):
    LTL = "ltl"
    FULL_LOAD = "full-load"

class DangerousGoodsType(lib.Enum):
    NONE = "none"
    LIMITED_QUANTITY = "limited-quantity"
    FULLY_REGULATED = "fully-regulated"

class LimitedAccessDeliveryType(lib.Enum):
    CONSTRUCTION_SITE = "construction-site"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    OTHER = "other"

class ContactMethodType(lib.Enum):
    EMAIL = "email-address"
    PHONE = "phone-number"

class ShippingService(lib.StrEnum):
     """Freightcom shipping services enumeration"""
     EXPRESS = "express"
     STANDARD = "standard"

class ResidentialDeliveryType(lib.Enum):
    YES = "yes"
    NO = "no"

class TailgateRequiredType(lib.Enum):
    YES = "yes"
    NO = "no"

class SignatureRequirementType(lib.Enum):
    NOT_REQUIRED = "not-required"
    REQUIRED = "required"

class InsuranceType(lib.Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    """ Unified Option type mapping """
    # insurance = freightcom_com_v2_coverage  #  maps unified karrio option to carrier specific
    pass


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

    return units.ShippingOptions(options, ShippingOption, items_filter=items_filter)


class TrackingStatus(lib.Enum):
    on_hold = ["on_hold"]
    delivered = ["delivered"]
    in_transit = ["in_transit"]
    delivery_failed = ["delivery_failed"]
    delivery_delayed = ["delivery_delayed"]
    out_for_delivery = ["out_for_delivery"]
    ready_for_pickup = ["ready_for_pickup"]


class ShippingOption(lib.Enum):
      """Carrier specific options"""
      residential_delivery = lib.OptionEnum("residential_delivery", ResidentialDeliveryType)
      tailgate = lib.OptionEnum("tailgate", TailgateRequiredType)
      special_instructions = lib.OptionEnum("special_instructions", str)
      ready_at_hour = lib.OptionEnum("ready_at_hour", int)
      ready_at_minute = lib.OptionEnum("ready_at_minute", int)
      ready_until_hour = lib.OptionEnum("ready_until_hour", int)
      ready_until_minute = lib.OptionEnum("ready_until_minute", int)
      signature_requirement = lib.OptionEnum("signature_requirement", SignatureRequirementType)
      packaging_type = lib.OptionEnum("packaging_type", PackagingType)
      pallet_type = lib.OptionEnum("pallet_type", PalletType)
      stackable_pallets = lib.OptionEnum("stackable_pallets", bool)
      dangerous_goods = lib.OptionEnum("dangerous_goods", DangerousGoodsType)
      dangerous_goods_packaging_group = lib.OptionEnum("dangerous_goods_packaging_group", str)
      dangerous_goods_class = lib.OptionEnum("dangerous_goods_class", str)
      dangerous_goods_description = lib.OptionEnum("dangerous_goods_description", str)
      dangerous_goods_un_number = lib.OptionEnum("dangerous_goods_un_number", str)
      emergency_contact_name = lib.OptionEnum("emergency_contact_name", str)
      emergency_contact_phone_number = lib.OptionEnum("emergency_contact_phone_number", str)
      emergency_contact_phone_extension = lib.OptionEnum("emergency_contact_phone_extension", str)
      limited_access_delivery_type = lib.OptionEnum("limited_access_delivery_type", LimitedAccessDeliveryType)
      limited_access_delivery_other_name = lib.OptionEnum("limited_access_delivery_other_name", str)
      in_bond = lib.OptionEnum("in_bond", bool)
      in_bond_type = lib.OptionEnum("in_bond_type", str)
      in_bond_name = lib.OptionEnum("in_bond_name", str)
      in_bond_address = lib.OptionEnum("in_bond_address", str)
      in_bond_contact_method = lib.OptionEnum("in_bond_contact_method", ContactMethodType)
      in_bond_contact_email = lib.OptionEnum("in_bond_contact_email", str)
      in_bond_contact_phone = lib.OptionEnum("in_bond_contact_phone", str)
      in_bond_contact_phone_extension = lib.OptionEnum("in_bond_contact_phone_extension", str)
      appointment_delivery = lib.OptionEnum("appointment_delivery", bool)
      protect_from_freeze = lib.OptionEnum("protect_from_freeze", bool)
      threshold_pickup = lib.OptionEnum("threshold_pickup", bool)
      threshold_delivery = lib.OptionEnum("threshold_delivery", bool)
      insurance_type = lib.OptionEnum("insurance_type", InsuranceType)
      insurance_currency = lib.OptionEnum("insurance_currency", str)
      insurance_value = lib.OptionEnum("insurance_value", float)
