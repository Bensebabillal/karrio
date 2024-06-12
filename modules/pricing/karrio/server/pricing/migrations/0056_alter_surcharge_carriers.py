# Generated by Django 4.2.11 on 2024-06-12 13:19

from django.db import migrations
import karrio.server.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0055_alter_surcharge_carriers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="surcharge",
            name="carriers",
            field=karrio.server.core.fields.MultiChoiceField(
                blank=True,
                choices=[
                    ("allied_express", "allied_express"),
                    ("allied_express_local", "allied_express_local"),
                    ("amazon_shipping", "amazon_shipping"),
                    ("aramex", "aramex"),
                    ("asendia_us", "asendia_us"),
                    ("australiapost", "australiapost"),
                    ("boxknight", "boxknight"),
                    ("bpost", "bpost"),
                    ("canadapost", "canadapost"),
                    ("canpar", "canpar"),
                    ("chronopost", "chronopost"),
                    ("colissimo", "colissimo"),
                    ("dhl_express", "dhl_express"),
                    ("dhl_parcel_de", "dhl_parcel_de"),
                    ("dhl_poland", "dhl_poland"),
                    ("dhl_universal", "dhl_universal"),
                    ("dicom", "dicom"),
                    ("dpd", "dpd"),
                    ("dpdhl", "dpdhl"),
                    ("easypost", "easypost"),
                    ("eshipper", "eshipper"),
                    ("fedex", "fedex"),
                    ("fedex_ws", "fedex_ws"),
                    ("freightcom", "freightcom"),
                    ("freightcomv2", "freightcomv2"),
                    ("generic", "generic"),
                    ("geodis", "geodis"),
                    ("laposte", "laposte"),
                    ("locate2u", "locate2u"),
                    ("morneau", "morneau"),
                    ("nationex", "nationex"),
                    ("purolator", "purolator"),
                    ("roadie", "roadie"),
                    ("royalmail", "royalmail"),
                    ("sendle", "sendle"),
                    ("tge", "tge"),
                    ("tnt", "tnt"),
                    ("ups", "ups"),
                    ("usps", "usps"),
                    ("usps_international", "usps_international"),
                    ("zoom2u", "zoom2u"),
                ],
                help_text="\n        The list of carriers you want to apply the surcharge to.\n        <br/>\n        Note that by default, the surcharge is applied to all carriers\n        ",
                null=True,
            ),
        ),
    ]
