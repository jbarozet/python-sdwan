#! /usr/bin/env python

import json
import os

import click
import requests

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
def get_org():
    """
    Get SD_WAN Manager organization
    """

    api_url = "/settings/configuration/organization"
    url = base_url + api_url

    # Using session.verify for certificate validation, so verify=False might not be strictly needed here
    # but kept for consistency with original code's explicit disable.
    response = requests.get(url=url, headers=header, verify=False)

    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, "org_settings_all")
        save_json(data, "org_settings_data")
        for item in data:
            org = item["org"]
        click.echo(f"Organization: {org}")
    else:
        click.echo("Failed to get org name " + str(response.text))
        exit()


# -----------------------------------------------------------------------------
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
        save_json(payload, "vbond_settings_all")
        save_json(data, "vbond_settings_data")
        for item in data:
            vbond = item["domainIp"]
        click.echo(f"vBond: {vbond}")
    else:
        click.echo("Failed to get vBond IP or name " + str(response.text))
        exit()


# -----------------------------------------------------------------------------
# Global variables for base_url and header, obtained from session.py
# This will be executed once when the script starts
# -----------------------------------------------------------------------------
# Replaced the manual environment variable retrieval and authentication logic
# with the centralized function from session.py
base_url, header = get_authenticated_session_details()


# -----------------------------------------------------------------------------
# Run commands
# -----------------------------------------------------------------------------
cli.add_command(get_vbond)
cli.add_command(get_org)

if __name__ == "__main__":
    cli()
