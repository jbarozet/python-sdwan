#! /usr/bin/env python

import json
import os

import click
import requests

# Import the new unified Manager class and the credentials function
from manager import Manager, get_manager_credentials_from_env


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

    api_path = "/settings/configuration/organization"

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "org_settings_all")
        save_json(data, "org_settings_data")
        for item in data:
            org = item["org"]
        click.echo(f"Organization: {org}")

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching users: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print("Error fetching users: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print(f"Error fetching users: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while fetching users: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def get_vbond():
    """
    Get vBond IP or name
    """

    api_path = "/settings/configuration/device"

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "vbond_settings_all")
        save_json(data, "vbond_settings_data")
        for item in data:
            vbond = item["domainIp"]
        click.echo(f"vBond: {vbond}")

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching users: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print("Error fetching users: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print(f"Error fetching users: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while fetching users: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
# Create session with Cisco Catalyst SD-WAN Manager
# -----------------------------------------------------------------------------
print("\n--- Authenticating to SD-WAN Manager ---")
host, port, user, password = get_manager_credentials_from_env()
manager = Manager(host, port, user, password)


# -----------------------------------------------------------------------------
# Run commands
# -----------------------------------------------------------------------------
cli.add_command(get_vbond)
cli.add_command(get_org)

if __name__ == "__main__":
    cli()
