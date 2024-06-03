import typing

import karrio.core.models as models
import karrio.lib as lib
import karrio.providers.morneau.error as provider_error
import karrio.providers.morneau.utils as provider_utils
import karrio.providers.morneau.units as provider_units
import karrio.schemas.morneau.shipment_purchase_response as shipping

def parse_shipment_response(
    response: lib.Deserializable[dict],
    settings: provider_utils.Settings,
) -> typing.Tuple[models.ShipmentDetails, typing.List[models.Message]]:
    response_dict = response.deserialize()
    errors = provider_error.parse_error_response(response_dict, settings)
    shipment = _extract_details(response_dict, settings) if "error" not in response_dict else None

    return shipment, errors

def _extract_details(
    data: dict,
    settings: provider_utils.Settings,
) -> models.ShipmentDetails:
    shipment = lib.to_object(shipping.ShipmentPurchaseResponseType, data)
    shipment_identifier = shipment.ShipmentIdentifier
    # Assuming the first LoadTenderConfirmation contains the primary details
    load_tender_confirmation = shipment.LoadTenderConfirmations[0]
    freight_bill_number = load_tender_confirmation.FreightBillNumber
    status = load_tender_confirmation.Status
    is_accepted = load_tender_confirmation.IsAccepted
    label = "PDF", # Placeholder: replace with actual label extraction logic if applicable
    tracking_number = freight_bill_number  # Assuming the FreightBillNumber is used as the tracking number
    meta = {
        "status": status,
        "is_accepted": is_accepted
    }
    return models.ShipmentDetails(
        carrier_id=settings.carrier_id,
        carrier_name=settings.carrier_name,
        tracking_number=tracking_number,
        shipment_identifier=shipment_identifier,
        label_type="PDF",
        docs=models.Documents(label="PDF"),
        meta=meta,
    )

def shipment_request(
    payload: models.ShipmentRequest,
    settings: provider_utils.Settings,
) -> lib.Serializable:
    _commodities = settings.get_selected_commodities(payload.options)
    code = settings._generate_unique_id("GoL", 15)
    # Construct the Loads
    loads = [
        {
            "Company": {
                "Name": payload.shipper.company_name,
                "Address": {
                    "Address1": payload.shipper.address_line1,
                    "Address2": payload.shipper.address_line2,
                    "PostalCode": payload.shipper.postal_code,
                    "City": payload.shipper.city,
                    "ProvinceCode": f"{payload.shipper.country_code}_{payload.shipper.state_code}"
                },
                "EmergencyContact": {
                    "FaxNumber": "",
                    "CellPhoneNumber": "",
                    "PhoneNumber": payload.shipper.phone_number,
                    "PhoneNumberExtension": "",
                    "ContactName": payload.shipper.person_name,
                    "Email": payload.shipper.email
                },
                "IsInvoicee": True
            },
            "ExpectedArrivalTimeSlot": settings._get_time_slot(),
            "Commodities": _commodities
        }
        for parcel in payload.parcels
    ]
    # Construct the Unloads
    unloads = [
        {
            "Number": 1,
            "Company": {
                "Name": payload.recipient.company_name,
                "Address": {
                    "Address1": payload.recipient.address_line1,
                    "Address2": payload.recipient.address_line2,
                    "PostalCode": payload.recipient.postal_code,
                    "City": payload.recipient.city,
                    "ProvinceCode": f"{payload.recipient.country_code}_{payload.recipient.state_code}"
                },
                "IsInvoicee": False
            },
            "ExpectedArrivalTimeSlot": settings._get_time_slot(),
            "Commodities": [{"Code": item.title} for item in payload.parcels[0].items],
            "SpecialInstructions": "",
            "FloorPallets": {},
            "Freight": [
                {
                    "Description": freight.description,
                    "ClassCode": "",
                    "Weight": {
                        "Quantity": freight.weight,
                        "Unit": "Pound" if freight.weight_unit == "LB" else "Kilogram"
                    },
                    "Unit": "Pallets", #freight.packaging_type,
                    "Quantity": len(payload.parcels),  #1,
                    "PurchaseOrderNumbers": []
                }
                for freight in payload.parcels
            ]
        }

    ]
    # Construct the LoadTender payload
    load_tender_payload = {
        "ServiceLevel": payload.service,
        "Stops": {
            "Loads": loads,
            "Unloads": unloads
        },
        "Notes": "",
        "ShipmentIdentifier": {
            "Type": "ProBill",
            "Number": code,
        },
        "References": [
            {
                "Type": "ProBill",
                "Value": code
            }
        ],

        "ThirdPartyInvoicee": {
            "Name":  payload.billing_address.company_name if payload.billing_address else payload.shipper.company_name ,
            "Address": {
               "Address1": payload.billing_address.address_line1 if payload.billing_address else payload.shipper.address_line1,
                "Address2": payload.billing_address.address_line2 if payload.billing_address else payload.shipper.address_line2,
                "PostalCode": payload.billing_address.postal_code if payload.billing_address else payload.shipper.postal_code,
                "City": payload.billing_address.city if payload.billing_address else payload.shipper.city,
                "ProvinceCode": f"{payload.billing_address.country_code}_{payload.billing_address.state_code}" if payload.billing_address else f"{payload.shipper.country_code}_{payload.shipper.state_code}"
            }
        }
        , "EmergencyContact": {},
        "IsInvoicee": True
    }

    return lib.Serializable(load_tender_payload)


