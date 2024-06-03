import datetime
from urllib import request
import jstruct
import karrio.core as core
import karrio.lib as lib
import datetime
import karrio.providers.morneau.units as units
import secrets
import string
from enum import Enum
from django.http import HttpRequest
import os
import requests
from decouple import Config, RepositoryEnv

class Settings(core.Settings):
    """Groupe Morneau connection settings."""
    username: str
    password: str
    caller_id: str
    cache: lib.Cache = jstruct.JStruct[lib.Cache, False, dict(default=lib.Cache())]
    billed_id: int
    division: str = "Morneau"

    # Load environment variables from the .env file in the root of morneau directory
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
    env_config = Config(RepositoryEnv(env_path))
    KARRIO_PUBLIC_URL = env_config("KARRIO_PUBLIC_URL")
    PORT=env_config("PORT")
    API_KEY=env_config("API_KEY")

    @property
    def carrier_name(self):
        return "morneau"

    # Define URLs for different services
    @property
    def rates_server_url(self):
        return "https://cotation.groupemorneau.com/api"

    @property
    def tracking_url(self):
        return "https://dev-shippingapi.groupemorneau.com" if self.test_mode else "https://shippingapi.groupemorneau.com"

    @property
    def server_url(self):
        return "https://dev-tmorposttenderapi.groupemorneau.com" if self.test_mode else "https://tmorposttenderapi.groupemorneau.com"

    @property
    def rating_jwt_token(self):
        return self._retrieve_jwt_token(self.rates_server_url, units.ServiceType.rates_service)

    @property
    def tracking_jwt_token(self):
        return self._retrieve_jwt_token(self.tracking_url, units.ServiceType.tracking_service)

    @property
    def shipment_jwt_token(self):
        return self._retrieve_jwt_token(self.server_url, units.ServiceType.shipping_service)

    @property
    def connection_config(self) -> lib.units.Options:
        from karrio.providers.morneau.units import ConnectionConfig
        return lib.to_connection_config(
            self.config or {},
            option_type=ConnectionConfig,
        )

    def _retrieve_jwt_token(self, url: str, service: units.ServiceType) -> str:
        """Retrieve JWT token from the given URL."""
        # Determine if we need production credentials for the rates service in test mode
        use_prod_for_rates = self.test_mode and service == units.ServiceType.rates_service
        env = 'prod' if use_prod_for_rates else ('test' if self.test_mode else 'prod')
        cache_key = f"auth_token_{service.name}_{env}"
        now = datetime.datetime.now()

        # Check if a cached token exists and is still valid
        cached = self.cache.get(cache_key) or {}
        if cached and cached.get('expiry') > now:
            return cached.get('token')

        # Define credentials based on the environment and service
        username, password = self._select_credentials(service, use_prod_for_rates)

        # Define the request for obtaining a new token
        if service == units.ServiceType.rates_service:
            response = lib.request(
                url=f"{url}/auth/login",
                data=f"Username={username}&Password={password}",
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            expires_in_seconds = 600
        else:
            response = lib.request(
                url=f"{url}/api/auth/Token",
                data=lib.to_json({"UserName": username, "Password": password}),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            expires_in_seconds = 3600

        token_data = lib.to_dict(response)
        token = token_data.get("AccessToken")
        expiry_time = now + datetime.timedelta(seconds=expires_in_seconds)

        # Cache the token and its expiry time
        self.cache.set(cache_key, {"token": token, "expiry": expiry_time})
        return token

    def _select_credentials(self, service: units.ServiceType, use_prod_credentials: bool):
        if use_prod_credentials:
            return (self.username, self.password)
        elif self.test_mode:
            return (self.test_username, self.test_password)
        else:
            return (self.username, self.password)

    def _generate_unique_id(self, prefix="Go", length=10):
            # Calculate the number of additional characters needed
            num_additional_chars = length - len(prefix)

            # Generate the additional random characters
            random_chars = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(num_additional_chars))

            #Combine prefix with the random characters
            unique_id = prefix + random_chars
            print(f"UNIQUE GENEREE {unique_id}")
            return unique_id

    def _get_time_slot(self, start_delta=0, end_delta=1):
        """
        Generates a time slot starting from 'start_delta' days from now,
        ending 'end_delta' days from now.

        Args:
        start_delta (int): Number of days from today to start the time slot.
        end_delta (int): Number of days from today to end the time slot.

        Returns:
        dict: A dictionary containing the formatted start and end times in ISO 8601 format.
        """
        # Calculate the start and end times based on the current date and time in UTC
        now = datetime.datetime.utcnow()
        start_time = now + datetime.timedelta(days=start_delta)
        end_time = now + datetime.timedelta(days=end_delta)

        # Format the times into ISO 8601 strings
        start_iso = start_time.isoformat() + "Z"  # Append 'Z' to indicate UTC time
        end_iso = end_time.isoformat() + "Z"  # Same as above

        # Return the time slot information
        return {
                "Between": start_iso,
                "And": end_iso
        }

    # Function to get selected commodities based on provided options
    def get_selected_commodities(self, option):
        selected_commodities = []  # Initialize an empty list to hold selected commodities
        for shipping_option in units.ShippingOption:
            # Access the value of the option which is an instance of OptionEnum
            option_enum = shipping_option.value
            # Check if the current option is in the provided options dictionary and its value is True
            if option.get(shipping_option.name, False):
                # If the option is selected, add the code from OptionEnum to the list of selected commodities
                selected_commodities.append({"Code": option_enum.code})

        return selected_commodities  # Return the list of selected commodities

    def get_selected_commodities_for_cotations(self, option):
        selected_commodities = []  # Initialize an empty list to hold selected commodities

        # Iterate over each shipping option defined in ShippingOption
        for shipping_option in units.ShippingOption:
            option_enum = shipping_option.value

            # Check if the current option is in the provided options dictionary and its value is True
            if option.get(shipping_option.name, False):
                # If the option is selected and it is a cotation-specific option, add the code from OptionEnum to the list of selected commodities
                if option_enum.code in units.COTATION_OPTION_CODES:
                    selected_commodities.append(option_enum.code)
        return selected_commodities  # Return the list of selected commodities

    def get_shipment_id(self, tracking_number: str) -> str:
            url = f"{self.KARRIO_PUBLIC_URL}:{self.PORT}/v1/shipments"
            headers = {
                'Authorization': f'Token {self.API_KEY}',
                'Content-Type': 'application/json'            }
            params = {
                'tracking_number': tracking_number
            }

            try:
                response = requests.get(
                    url=url,
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()  # Will raise an HTTPError for bad responses

                # Assuming the response contains a JSON object with the 'id' field
                shipment_data = response.json()
                print(f"RESULT: {shipment_data}")
                shipment_id = shipment_data.get('results')[0].get('id')
                if shipment_id:
                    return shipment_id
                else:
                    raise ValueError("Shipment ID not found in the response")

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except Exception as err:
                print(f"Other error occurred: {err}")

    def cancel_shipment_in_karrio(self, shipment_id: str) -> None:
            url = f"{self.KARRIO_PUBLIC_URL}:{self.PORT}/v1/shipments/{shipment_id}/cancel"
            headers = {
                'Authorization': f'Token {self.API_KEY}',
                'Accept': 'application/json'
            }
            try:
                # Make the POST request
                response = requests.post(
                    url=url,
                    headers=headers,
                )
                response.raise_for_status()  # Raise an HTTPError for bad responses

                print(f"Shipment {shipment_id} has been successfully cancelled.")

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
                raise
            except Exception as err:
                print(f"Other error occurred: {err}")
                raise
