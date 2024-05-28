import time
import requests
from requests.exceptions import RequestException

def poll_tender_status(FreightBillNumber, server_url, caller_id, jwt_token):
    url = f"{server_url}/LoadTender/{caller_id}/{FreightBillNumber}/status"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if len(response.content) == 0:
                print(f"Toujours pas de reponse de morneau: {response.content}")
                continue
            status_data = response.json()

            # Process the status_data as needed
            print(f"Polled status: {status_data}")

            # Extract the load tender confirmations
            load_tender_confirmations = status_data.get("LoadTenderConfirmations", [])
            if load_tender_confirmations:
                confirmation = load_tender_confirmations[0]
                if confirmation.get("IsAccepted"):
                    # Perform the task if the tender is accepted
                    print("Ajoutons notre tache ici")
                    # Insert any other task you want to perform here
                    break
                elif confirmation.get("Status") is not None:
                    print(f"Tender status: {confirmation.get('Status')}. Ending poll.")
                    break

        except RequestException as e:
            print(f"Failed to poll status: {e}")

        # Wait for 2 minutes before the next poll
        time.sleep(120)
