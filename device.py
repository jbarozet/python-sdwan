#! /usr/bin/env python

import json
import os

import click
import requests
import tabulate
import urllib3

from session import Authentication

urllib3.disable_warnings()


# ----------------------------------------------------------------------------------------------------
# Click CLI
# ----------------------------------------------------------------------------------------------------


@click.group()
def cli():
    """Command line tool for to collect application names)."""
    pass


# ----------------------------------------------------------------------------------------------------
# Save JSON payloads
# ----------------------------------------------------------------------------------------------------


def save_json(payload: str, data: str, filename_prefix: str = "payload"):
    """Save json response payload to a file

    Args:
        payload: Full JSON response payload
        data: Data portion of JSON response
        filename_prefix: Prefix for saved files (default: "payload")
    """

    data_dir = "./payloads/"
    filename_data = "".join([data_dir, f"{filename_prefix}_data.json"])
    filename_payload = "".join([data_dir, f"{filename_prefix}_all.json"])

    # Create payload folder
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
        print("~~~ Folder %s created!" % data_dir)
    else:
        print("~~~ Folder %s already exists" % data_dir)

    # Dump entire payload to file
    print(f"~~~ Saving full payload in {filename_payload}")
    with open(filename_payload, "w") as file:
        json.dump(payload, file, indent=4)

    # Dump payload data (device list) to file
    print(f"~~~ Saving data payload in {filename_data}")
    with open(filename_data, "w") as file:
        json.dump(data, file, indent=4)


# ----------------------------------------------------------------------------------------------------
# Get Device by IP
# /system/device/{type}?deviceIP={ip_address}
# ----------------------------------------------------------------------------------------------------


@click.command()
def get_devices():
    type = "vedges"

    api_url = "/system/device/%s" % (type)
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)

    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, data, "devices")
        app_headers = [
            "UUID",
            "Model",
            "Certificate",
            "Configured Hostname",
            "System IP",
            "Configured Site ID",
        ]
    else:
        click.echo("Failed to get device list " + str(response.text))
        exit()

    table = list()

    for item in data:
        tr = [
            item.get("uuid", "N/A"),
            item.get("deviceModel", "N/A"),
            item.get("vedgeCertificateState", "N/A"),
            item.get("host-name", "N/A"),
            item.get("configuredSystemIP", "N/A"),  # Using .get() with default value
            item.get("siteId", "N/A"),
        ]
        table.append(tr)

    click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))


# ----------------------------------------------------------------------------------------------------
# Get Device by IP
# /system/device/{type}?deviceIP={ip_address}
# ----------------------------------------------------------------------------------------------------


@click.command()
def get_device_by_ip():
    type = "vedges"
    systemip = input("Enter System IP address : ")

    api_url = "/system/device/%s?deviceIP=%s" % (type, systemip)
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, data, "device_by_ip")
    else:
        click.echo("Failed to get device " + str(response.text))
        exit()

    for item in data:
        tr = [
            item["configStatusMessage"],
            item["uuid"],
            item["deviceModel"],
            item["vedgeCertificateState"],
            item["deviceIP"],
            item["host-name"],
            item["version"],
            item["vmanageConnectionState"],
        ]

    print("\nDevice Information:")
    print("------------------")
    print("Device name: ", tr[5])
    print("Device IP: ", tr[4])
    print("UUID: ", tr[1])
    print("Device Model: ", tr[2])
    print("vManage Connection State: ", tr[7])
    print("Certificate state: ", tr[3])
    print("Version: ", tr[6])
    print("Config status: ", tr[0])


# ----------------------------------------------------------------------------------------------------
# Get Device Configuration
# dataservice/template/config/running/CSR-212D9E25-AD84-4E18-9725-B3CDEABFE1A8
# ----------------------------------------------------------------------------------------------------


@click.command()
def get_device_config():
    api_url = "/template/config/running/CSR-212D9E25-AD84-4E18-9725-B3CDEABFE1A8"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, data, "device_config")
        running_config = payload["config"]
    else:
        click.echo("Failed to get device configuration " + str(response.text))
        exit()
    print(running_config)


# ----------------------------------------------------------------------------------------------------
# Get Parameters
# ----------------------------------------------------------------------------------------------------

vmanage_host = os.environ.get("vmanage_host")
vmanage_port = os.environ.get("vmanage_port")
vmanage_username = os.environ.get("vmanage_username")
vmanage_password = os.environ.get("vmanage_password")

if (
    vmanage_host is None
    or vmanage_port is None
    or vmanage_username is None
    or vmanage_password is None
):
    print(
        "For Windows Workstation, vManage details must be set via environment variables using below commands"
    )
    print("set vmanage_host=198.18.1.10")
    print("set vmanage_port=8443")
    print("set vmanage_username=admin")
    print("set vmanage_password=admin")
    print(
        "For MAC OSX Workstation, vManage details must be set via environment variables using below commands"
    )
    print("export vmanage_host=198.18.1.10")
    print("export vmanage_port=8443")
    print("export vmanage_username=admin")
    print("export vmanage_password=admin")
    exit()

# ----------------------------------------------------------------------------------------------------
# Authenticate with vManage
# ----------------------------------------------------------------------------------------------------

vmanage = Authentication(vmanage_host, vmanage_port, vmanage_username, vmanage_password)
jsessionid = vmanage.login()
token = vmanage.get_token()

if token is not None:
    header = {
        "Content-Type": "application/json",
        "Cookie": jsessionid,
        "X-XSRF-TOKEN": token,
    }
else:
    header = {"Content-Type": "application/json", "Cookie": jsessionid}

base_url = "https://%s:%s/dataservice" % (vmanage_host, vmanage_port)


# ----------------------------------------------------------------------------------------------------
# Run commands
# ----------------------------------------------------------------------------------------------------

cli.add_command(get_devices)
cli.add_command(get_device_config)
cli.add_command(get_device_by_ip)

if __name__ == "__main__":
    cli()
