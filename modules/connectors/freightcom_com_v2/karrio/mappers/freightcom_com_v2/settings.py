
"""Karrio Frieghtcom v2 client settings."""

import attr
import karrio.providers.freightcom_com_v2.utils as provider_utils


@attr.s(auto_attribs=True)
class Settings(provider_utils.Settings):
    """Frieghtcom v2 connection settings."""

    # required carrier specific properties
    # generic properties
    id: str = None
    test_mode: bool = False
    carrier_id: str = "freightcom_com_v2"
    account_country_code: str = None
    apiKey: str = None
    metadata: dict = {}
    config: dict = {}
