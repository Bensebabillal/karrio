import time
import requests
from requests.exceptions import RequestException
from threading import Lock
import karrio.lib as lib


def poll_tender_status(FreightBillNumber, settings, cancel_callback, lock):
    url = f"{settings.server_url}/LoadTender/{settings.caller_id}/{FreightBillNumber}/status"
    while True:
        try:
            with lock:
                # Refresh the JWT token if needed
                jwt_token = settings.shipment_jwt_token
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {jwt_token}"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if len(response.content) == 0:
                print(f"waiting Morneau approval: {response.content}")
                request = lib.Serializable({'reference': f"{{'Number': '{FreightBillNumber}'}}"})
                cancel_callback(request)
                #continue
                break
            status_data = response.json()
            print(f"Polled status: {status_data}")
            load_tender_confirmations = status_data.get("LoadTenderConfirmations", [])
            if load_tender_confirmations:
                confirmation = load_tender_confirmations[0]
                if confirmation.get("IsAccepted"):
                    print("Tender accepted.")
                    # shipment_request_data
                    # shipment_request_data.get("ShipmentIdentifier", {}).get("Number")
                    # request = lib.Serializable({'reference': f"{{'Number': '{tmp}'}}"})
                    # cancel_callback(request)
                    break
                elif confirmation.get("Status") is not None:
                    print(f"Tender status: {confirmation.get('Status')}. Ending poll.")
                    if confirmation.get('Status') == 'NEW' and not confirmation.get("IsAccepted"):
                        cancel_callback(FreightBillNumber)
                    break
        except RequestException as e:
            print(f"Failed to poll status: {e}")
            if e.response.status_code == 401:  # Unauthorized
                try:
                    with lock:
                        settings.shipment_jwt_token = settings._retrieve_jwt_token(settings.server_url, settings.ServiceType.shipping_service)
                except Exception as refresh_e:
                    print(f"Failed to refresh JWT token: {refresh_e}")
                    break

        time.sleep(120)
