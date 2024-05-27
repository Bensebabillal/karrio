"""Karrio Groupe Morneau client proxy."""
from copyreg import constructor
import typing
import karrio.providers.morneau.error as provider_error
import karrio.api.proxy as proxy
import karrio.lib as lib
import karrio.mappers.morneau.settings as provider_settings
import requests  # Ensure you have this imported if lib.request is not abstracting requests


from threading import Thread
from karrio.providers.morneau.shipment.polling_service import poll_tender_status


class Proxy(proxy.Proxy):
    settings: provider_settings.Settings
    def get_rates(self, request: lib.Serializable) -> lib.Deserializable[str]:
        # Send request for quotation
        response = lib.request(
            url=f"{self.settings.rates_server_url}/quotes/add",
            data=lib.to_json(request.serialize()),
            trace=self.trace_as("json"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.rating_jwt_token}",
                "Content-Type": "application/json",
            },
        )
        print(response)
        return lib.Deserializable(response, lib.to_dict)

    def create_shipment(self, request: lib.Serializable) -> lib.Deserializable[str]:
        shipment_request_data = request.serialize()
        try:
            # Send the POST request
            response = lib.request(
                url=f"{self.settings.server_url}/LoadTender/{self.settings.caller_id}",
                data=lib.to_json(shipment_request_data),
                trace=self.trace_as("json"),
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-API-VERSION": "1",
                    "Authorization": f"Bearer {self.settings.shipment_jwt_token}"
                },
            )
        except requests.exceptions.RequestException as e:
            # Log error here or perform other error handling
            print(f"HTTP Request failed: {e}")
            raise Exception(f"HTTP Request failed: {e}")

        # Check if the response content is empty
        if len(response) == 0:
            FreightBillNumber=shipment_request_data.get("ShipmentIdentifier", {}).get("Number")
            #poll_tender_status.schedule(args=(FreightBillNumber, self.settings.server_url, self.settings.caller_id, self.settings.shipment_jwt_token), delay=120)

            # Create and start a thread for polling the tender status
            poll_thread = Thread(
                target=poll_tender_status,
                args=(FreightBillNumber, self.settings.server_url, self.settings.caller_id, self.settings.shipment_jwt_token)
            )
           # poll_thread.start()

            simulated_response = {
                "ShipmentIdentifier": shipment_request_data.get("ShipmentIdentifier"),
                "LoadTenderConfirmations": [
                    {
                        "FreightBillNumber": shipment_request_data.get("ShipmentIdentifier", {}).get("Number"),
                        "IsAccepted": False,
                        "Status": "New",
                        "PurchaseOrderNumbers": [],
                        "References": shipment_request_data.get("References"),
                    },
                ]
            }
            return lib.Deserializable(simulated_response, lib.to_dict)
        else:
            #Use the provider's error parsing utility to provide a detailed error
            #error_message = provider_error.parse_http_response(response)
            #print(f"Error processing the shipment request: {error_message}")
            raise Exception(f"Failed to create shipment: {response}")


    def cancel_shipment(self, request: lib.Serializable) -> lib.Deserializable[str]:
        payload = request.serialize()
        response = lib.request(
            url=f"{self.settings.server_url}/LoadTender/{self.settings.caller_id}/{payload['reference']}/cancel",
            method="GET",
            headers={
                "Accept": "application/json",
                "X-API-VERSION": "1",
                "Authorization": f"Bearer {self.settings.shipment_jwt_token}"
            },
            on_error=provider_error.parse_http_response,
        )

        return lib.Deserializable(response if any(response) else "{}", lib.to_dict)

    def get_tracking(self, request: lib.Serializable) -> lib.Deserializable[str]:
        def _get_tracking(reference: str):
            return reference, lib.request(
                url=f"{self.settings.tracking_url}/api/v1/tracking/en/MORNEAU/{reference}",
                trace=self.trace_as("json"),
                method="GET",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-API-VERSION": "1",
                    "Authorization": f"Bearer {self.settings.tracking_jwt_token}"
                },
            )

        responses: typing.List[typing.Tuple[str, str]] = lib.run_concurently(
            _get_tracking, request.serialize()
        )

        return lib.Deserializable(
            responses,
            lambda res: [
                (num, lib.to_dict(track))
                for num, track in res
                if any(track.strip())
            ],
        )
