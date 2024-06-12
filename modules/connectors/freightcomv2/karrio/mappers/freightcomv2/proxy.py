
"""Karrio freightcom v2 client proxy."""
import typing
import karrio.lib as lib
import karrio.api.proxy as proxy
import karrio.mappers.freightcomv2.settings as provider_settings
import threading
import time
import karrio.providers.freightcomv2.error as error
import karrio.providers.freightcomv2.shipment.poll_shipment_status as poll_shipment_status
import json

class Proxy(proxy.Proxy):
    settings: provider_settings.Settings
    def get_rates(self, request: lib.Serializable) -> lib.Deserializable[str]:
        response = lib.request(
            url=f"{self.settings.server_url}/rate",
            data=lib.to_json(request.serialize()),  # Ensure data is serialized to a JSON string
            trace=self.trace_as("json"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"{self.settings.apiKey}"
            },
        )
        print(f"data: {lib.to_json(request.serialize())}")
        print(f"response: {response}")


        # Check if response contains an ID
        if "request_id" in response:
                # Deserialize the response correctly
            if isinstance(response, str):
                response_data = json.loads(response)
            elif isinstance(response, dict):
                response_data = response
            else:
                response_data = lib.to_dict(response)

            # Check if response contains a request_id
            request_id = response_data.get("request_id")

            # Fetch rate details using the rate ID
            rate_details_response = lib.request(
                url=f"{self.settings.server_url}/rate/{request_id}",
                trace=self.trace_as("json"),
                method="GET",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"{self.settings.apiKey}"
                },
            )
            print(f"rate_details_response: {rate_details_response}")
            rate_details_data = lib.to_dict(rate_details_response)
            return lib.Deserializable(rate_details_data, lib.to_dict)

        return lib.Deserializable(response, lib.to_dict)


    def create_shipment(self, request: lib.Serializable) -> lib.Deserializable[dict]:
        response = lib.request(
            url=f"{self.settings.server_url}/shipment",
            data=lib.to_json(request.serialize()),
            trace=self.trace_as("json"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"{self.settings.apiKey}",
            },
        )
        print("HALALA")
        response_data = lib.to_dict(response)

        print(f"response_data : {response_data}")

        print(f"create shipment response: {response_data}")
        shipment_id = response_data.get("id")
        if shipment_id:
            shipment_response = lib.request(
                url=f"{self.settings.server_url}/shipment/{shipment_id}",
                method="GET",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"{self.settings.apiKey}",
                },
            )
            shipment_data = lib.to_dict(shipment_response)
            if "shipment" in shipment_data:
                return lib.Deserializable(shipment_data, lib.to_dict)

        messages = error.parse_error_response(response_data, self.settings)
        return lib.Deserializable({"messages": messages}, lib.to_dict)

    def cancel_shipment(self, request: lib.Serializable) -> lib.Deserializable[str]:
        response = lib.request(
            url=f"{self.settings.server_url}/shipment/{request.serialize()['shipment_identifier']}",
            data=request.serialize(),
            trace=self.trace_as("json"),
            method="DELETE",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"{self.settings.apiKey}"
            },
        )
        return lib.Deserializable(response, lib.to_dict)

    def get_tracking(self, request: lib.Serializable) -> lib.Deserializable[typing.Tuple[str, dict]]:
        payload = request.serialize()
        shipment_id = payload['shipment_id']
        response = lib.request(
            url=f"{self.settings.server_url}/shipment/{shipment_id}/tracking-events",
            trace=self.trace_as("json"),
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"{self.settings.apiKey}"
            },
        )
        # Ajoutez le shipment_id dans la réponse pour l'utiliser dans le parsing
        response_data = lib.to_dict(response)
        return lib.Deserializable((shipment_id, response_data))



    # def create_shipment_asynchrone(self, request: lib.Serializable) -> lib.Deserializable[dict]:
    #     response = lib.request(
    #         url=f"{self.settings.server_url}/shipments",
    #         data=request.serialize(),
    #         trace=self.trace_as("json"),
    #         method="POST",
    #         headers={
    #             "Content-Type": "application/json",
    #             "Accept": "application/json",
    #             "Authorization": f"{self.settings.apiKey}",
    #         },
    #     )
    #     response_data = lib.to_dict(response)

    #     if response.status_code == 200 and "shipment" in response_data:
    #         return lib.Deserializable(response_data, lib.to_dict)

    #     if response.status_code == 202:
    #         shipment_id = response_data.get("id")
    #         if shipment_id:
    #             thread = threading.Thread(target=poll_shipment_status, args=(shipment_id, self.settings))
    #             thread.start()
    #             return lib.Deserializable({
    #                 "status": "processing",
    #                 "message": "Shipment is being processed. You will be notified once it's complete.",
    #                 "shipment_id": shipment_id
    #             }, lib.to_dict)

    #     messages = error.parse_error_response(response_data, self.settings)
    #     return lib.Deserializable({"messages": messages}, lib.to_dict)
