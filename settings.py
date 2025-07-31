#! /usr/bin/env python

import json
import logging
import os

import click
import requests
import urllib3

from session import Authentication

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
urllib3.disable_warnings()  # Disable warning


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
# Commands
# ----------------------------------------------------------------------------------------------------


@click.command()
def get_org():
    """
    Get vManage organization
    """

    api_url = "/settings/configuration/organization"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)

    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, data, "org_settings")
        for item in data:
            org = item["org"]
        click.echo(f"Organization: {org}")
    else:
        click.echo("Failed to get org name " + str(response.text))
        exit()


@click.command()
def get_vbond():
    """
    Get vBond IP or name
    """

    api_url = "/settings/configuration/device"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        save_json(payload, data, "vbond_settings")
        for item in data:
            vbond = item["domainIp"]
        click.echo(f"vBond: {vbond}")
    else:
        click.echo("Failed to get vBond IP or name " + str(response.text))
        exit()


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

cli.add_command(get_vbond)
cli.add_command(get_org)

if __name__ == "__main__":
    cli()
