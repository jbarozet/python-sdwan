#! /usr/bin/env python

import json
import os

import click
import requests
import tabulate
import urllib3

# Import the new function from session.py
from session import get_authenticated_session_details


# -----------------------------------------------------------------------------
@click.group()
def cli():
    """Command line tool for to collect application names)."""
    pass


# -----------------------------------------------------------------------------
def save_json(payload: str, filename: str = "payload"):
    """Save json response payload to a file

    Args:
        payload: JSON response payload
        filename: filename for saved files (default: "payload")
    """

    data_dir = "./payloads/"
    filename = "".join([data_dir, f"{filename}.json"])

    # Create payload folder
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
        print("~~~ Folder %s created!" % data_dir)
    else:
        print("~~~ Folder %s already exists" % data_dir)

    # Dump entire payload to file
    print(f"~~~ Saving payload in {filename}")
    with open(filename, "w") as file:
        json.dump(payload, file, indent=4)


# -----------------------------------------------------------------------------
@click.command()
def ls():
    """
    Get Device by IP
    /system/device/{type}?deviceIP={ip_address}
    """
    type = "vedges"

    api_url = "/system/device/%s" % (type)
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)

    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, "devices_all")
        save_json(data, "devices_data")
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


# -----------------------------------------------------------------------------
@click.command()
def get_device_by_ip():
    """
    Get Device by IP
    /system/device/{type}?deviceIP={ip_address}
    """

    type = "vedges"
    systemip = click.prompt("Enter device system-ip", type=str)
    api_url = f"/system/device/{type}?deviceIP={systemip}"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, "device_by_ip_all")
        save_json(data, "device_by_ip_data")
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


# -----------------------------------------------------------------------------
@click.command()
def get_config():
    """
    Get Device Configuration
    dataservice/template/config/running/{uuid}
    """

    uuid = click.prompt("Enter device uuid", type=str)
    api_url = f"/template/config/running/{uuid}"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        payload = response.json()
        # Save the payload and data to files
        save_json(payload, "device_config_all")
        running_config = payload["config"]
    else:
        click.echo("Failed to get device configuration " + str(response.text))
        exit()
    print(running_config)


# -----------------------------------------------------------------------------
# Global variables for base_url and header, obtained from session.py
# This will be executed once when the script starts
# -----------------------------------------------------------------------------
base_url, header = get_authenticated_session_details()

# ----------------------------------------------------------------------------------------------------
# Run commands
# ----------------------------------------------------------------------------------------------------
cli.add_command(ls)
cli.add_command(get_config)
cli.add_command(get_device_by_ip)

if __name__ == "__main__":
    cli()
