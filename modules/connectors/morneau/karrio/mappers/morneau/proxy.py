"""Karrio Groupe Morneau client proxy."""
import typing
import karrio.providers.morneau.error as provider_error

import karrio.api.proxy as proxy
import karrio.lib as lib
import karrio.mappers.morneau.settings as provider_settings
import json


import requests  # Ensure you have this imported if lib.request is not abstracting requests

from huey import RedisHuey
from huey.contrib.djhuey import task

# Initialize Huey
huey = RedisHuey()

# Generate a unique UUID to be used for FreightBillNumber
FreightBillNumber = "123456"#generate_unique_id()
print("Freinght: ", FreightBillNumber)


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

    def create_shipment_old(self, request: lib.Serializable) -> lib.Deserializable[str]:
        shipment_request_data = request.serialize()
        # Send the POST request
        response = lib.request(
            url=f"{self.settings.server_url}/LoadTender/{self.settings.caller_id}",
            data=lib.to_json(shipment_request_data),
            trace=self.trace_as("json"),
            method="POST",
            on_error=provider_error.parse_http_response,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-API-VERSION": "1",
                "Authorization": f"Bearer {self.settings.shipment_jwt_token}"
            },
        )
        # Check the response
        if response == "": # status = 202
            poll_tender_status.schedule(args=(FreightBillNumber, self.settings.server_url, self.settings.caller_id,  self.settings.shipment_jwt_token), delay=120)  # Planifier la première vérification pour 2 minutes plus tard
            # Build a simulated response from the request data

            simulated_response = {
                "ShipmentIdentifier": shipment_request_data.get("ShipmentIdentifier"),
                "LoadTenderConfirmations": [
                    {
                        "FreightBillNumber": "HGJGJE",  # Example, this should be extracted if available
                        "IsAccepted": False,  # default value
                        "Status": "New",
                        "PurchaseOrderNumbers": [],
                        "References": shipment_request_data.get("References"),
                    },
                ]
            }
            return  lib.Deserializable(simulated_response, lib.to_dict)
        else:
            raise Exception(f"Failed to create shipment")



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

        # Check the response
        if  response=="":  # Checking if response is empty assuming response is a Response object
            poll_tender_status.schedule(args=(FreightBillNumber, self.settings.server_url, self.settings.caller_id, self.settings.shipment_jwt_token), delay=120)

            # Build a simulated response from the request data
            print("je suis arrivé à la simulation")
            #code = shipment_request_data.get("ShipmentIdentifier")
            #Convert the string representation of a dictionary to an actual dictionary

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
            # Use the provider's error parsing utility to provide a detailed error
            error_message = provider_error.parse_http_response(response)
            print(f"Error processing the shipment request: {error_message}")
            raise Exception(f"Failed to create shipment: {error_message}")

        # Assuming a successful case handling if not empty and HTTP 200
        return lib.Deserializable(response.json(), lib.to_dict)


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

@task(retries=3, retry_delay=60)
def poll_tender_status(tender_id, server_url, caller_id, shipment_jwt_token):
    print("Starting polling for tender status...")
    try:
        response = lib.request(
            url=f"{server_url}/LoadTender/{caller_id}/{tender_id}/status",
            headers={"Authorization": f"Bearer {shipment_jwt_token}"},
            method="GET"
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("IsAccepted", False):
                print("Tender accepted!")
            else:
                raise ValueError("Tender not yet accepted")
        elif response.status_code == 500:
            print("Server error, will retry...")
            raise Exception("Server error")  # Trigger retry
        else:
            print(f"Failed with status code {response.status_code}, not retrying.")
            raise Exception("Critical error, not retrying")
    except Exception as e:
        print(f"Exception during request: {str(e)}")
        raise  # Raise exception to trigger retry
