
import threading
import time
import karrio.lib as lib
import karrio.providers.freightcomv2.error as error
import karrio.providers.freightcomv2.shipment.poll_shipment_status as poll_shipment_status
import karrio.mappers.freightcomv2.settings as provider_settings
import karrio.providers.freightcomv2.utils as provider_utils


def poll_shipment_status(shipment_id: str, settings: provider_utils.Settings):
    url = f"{settings.server_url}/shipments/{shipment_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"{settings.apiKey}",
    }

    for _ in range(120):  # Polling for up to 2 hours
        response = lib.request(
            url=url,
            method="GET",
            headers=headers,
        )
        response_data = lib.to_dict(response)

        if "shipment" in response_data:
            # Notify the user or update the shipment status in the database
            settings.notify_user_of_shipment_status(response_data)
            return response_data

        time.sleep(60)  # Wait for 1 minute before polling again

    # If polling fails after 2 hours, notify the user
    settings.notify_user_of_shipment_status({
        "status": "error",
        "message": "Shipment processing timeout after 2 hours",
        "shipment_id": shipment_id
    })
    return {"status": "error", "message": "Shipment processing timeout after 2 hours"}
