"""Karrio Groupe Morneau client settings."""
import attr
import jstruct
import karrio.lib as lib
import os
from karrio.providers.morneau.utils import Settings as BaseSettings
from decouple import Config, RepositoryEnv
# Load environment variables from the .env file in the root of morneau directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
env_config = Config(RepositoryEnv(env_path))

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
    test_username: str = env_config("TEST_USERNAME")
    test_password: str = env_config("TEST_PASSWORD")
