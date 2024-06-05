
from karrio.core.metadata import Metadata

from karrio.mappers.freightcom_com_v2.mapper import Mapper
from karrio.mappers.freightcom_com_v2.proxy import Proxy
from karrio.mappers.freightcom_com_v2.settings import Settings
import karrio.providers.freightcom_com_v2.units as units


METADATA = Metadata(
    id="freightcom_com_v2",
    label="Frieghtcom v2",
    # Integrations
    Mapper=Mapper,
    Proxy=Proxy,
    Settings=Settings,
    options=units.ShippingOption,
    services=units.ShippingService,
    # Data Units
    is_hub=False
)
