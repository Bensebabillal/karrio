
import karrio.core as core
import karrio.lib as lib
import karrio.providers.morneau.units as units
import requests
import secrets
import string



class Settings(core.Settings):
    """freightcom v2 connection settings."""
    # username: str  # carrier specific api credential key
    apiKey: str = "mNlJ5Vwj5jn70YURDbksWyNdbrh08u24HnY0tJOn0Tz9wZdiCvfjktWDRXhFQtzb"
    @property
    def carrier_name(self):
        return "freightcomv2"

    @property
    def server_url(self):
        return (
            "https://customer-external-api.ssd-test.freightcom.com"
            if self.test_mode
            else "https://external-api.freightcom.com"
        )


    def notify_user_of_shipment_status(self, shipment_data: dict):
        karrio_update_url = "https://api.karrio.io/v1/shipments/{shipment_id}/status"

        shipment_id = shipment_data.get("id")
        if not shipment_id:
            print("Shipment ID not found in the response data")
            return

        # Données à envoyer pour mettre à jour le statut
        status_update_data = {
            "status": "purchased" if "shipment" in shipment_data else "error",
            "details": shipment_data
        }

        # En-têtes de la requête
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.apiKey,
        }

        try:
            response = requests.post(
                karrio_update_url.format(shipment_id=shipment_id),
                json=status_update_data,
                headers=headers
            )
            response.raise_for_status()
            print("Successfully updated shipment status in Karrio")
        except requests.exceptions.RequestException as e:
            print(f"Failed to update shipment status in Karrio: {str(e)}")

    def _generate_unique_id(self, prefix="Go", length=10):
            # Calculate the number of additional characters needed
            num_additional_chars = length - len(prefix)

            # Generate the additional random characters
            random_chars = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(num_additional_chars))

            # Combine prefix with the random characters
            unique_id = prefix + random_chars
            print(f"UNIQUE GENEREE {unique_id}")
            return unique_id


    @property
    def connection_config(self) -> lib.units.Options:
        from karrio.providers.freightcomv2.units import ConnectionConfig
        return lib.to_connection_config(
            self.config or {},
            option_type=ConnectionConfig,
        )
