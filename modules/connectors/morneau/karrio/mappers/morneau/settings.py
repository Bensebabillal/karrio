"""Karrio Groupe Morneau client settings."""

import attr
import jstruct
import karrio.lib as lib
from karrio.providers.morneau.utils import Settings as BaseSettings

@attr.s(auto_attribs=True)
class Settings(BaseSettings):
    """Groupe Morneau connection settings."""
    # required carrier specific properties
    billed_id: str
    caller_id: str
    division: str
    # generic properties
    username: str
    password: str
    carrier_id: str = "morneau"
    account_country_code: str = None

    cache: lib.Cache = jstruct.JStruct[lib.Cache, False, dict(default=lib.Cache())]
    test_mode: bool = False
    metadata: dict = {}
    id: str = None
    config: dict = {}

    test_username: str ="dev.imprimerieGauvin"
    test_password: str ="SFmFLAeKpx7K3WXoeJOCDhC74Y6TrvhE"
