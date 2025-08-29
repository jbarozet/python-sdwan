#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Managing users on SD-WAN Manager
#
# Description:
#   List, add, and delete users on Cisco Catalyst SD-WAN Manager.
#
# =========================================================================

import json
import os
import sys

import click
import requests
import tabulate

# Import the new unified Manager class and the credentials function
from manager import Manager, get_manager_credentials_from_env


# -----------------------------------------------------------------------------
@click.group()
def cli():
    """Command line tool for managing users on SD-WAN Manager."""
    pass


# -----------------------------------------------------------------------------
def save_json(payload: dict, filename: str = "payload"):
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
        print(f"~~~ Folder {data_dir} created!")
    else:
        print(f"~~~ Folder {data_dir} already exists")

    # Dump entire payload to file
    print(f"~~~ Saving payload in {filename}")
    with open(filename, "w") as file:
        json.dump(payload, file, indent=4)


# -----------------------------------------------------------------------------
@click.command()
def ls():
    """List all users"""

    # API endpoint for users
    api_path = "/admin/user"

    # Fetch users
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "users_headers_and_data")
        save_json(data, "users_data")

        headers = ["Username", "Group"]
        table = []
        for item in data:
            tr = [
                item.get("userName", "N/A"),
                ", ".join(item.get("group", ["N/A"])),
            ]
            table.append(tr)

        if table:
            click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
        else:
            click.echo("No users found or data is empty.")

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching users: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print(f"Error fetching users: Connection failed.")
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
def add():
    """Add a user"""

    api_path = "/admin/user"

    print("\n~~~ Adding user")

    username_input = click.prompt("Enter username to add", type=str)
    password = click.prompt(
        "Enter password for the new user", type=str, hide_input=True
    )
    group_input = click.prompt(
        "Enter user group(s) (comma-separated, e.g., netadmin,admin)",
        type=str,
        default="netadmin",
    )
    groups = [g.strip() for g in group_input.split(",")]

    user_payload = {
        "userName": username_input,
        "description": f"User {username_input} created via CLI",
        "locale": "en_US",
        "group": groups,
        "password": password,
        "resGroupName": "global",
    }

    try:
        response = manager._api_post(api_path, payload=user_payload)

        confirmed_username = (
            response.get("userName") if isinstance(response, dict) else None
        )

        if confirmed_username:
            click.echo(f"User '{confirmed_username}' successfully created.")
        else:
            click.echo(f"User '{username_input}' successfully created.")

    except requests.exceptions.HTTPError as e:
        print(
            f"Error adding user '{username_input}': HTTP Error {e.response.status_code}"
        )
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print(f"Error adding user '{username_input}': Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print(f"Error adding user '{username_input}': The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while adding user '{username_input}': {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def delete():
    """Delete a user"""

    print("\n~~~ Deleting user")
    username = click.prompt("Enter username to delete", type=str)

    api_path = f"/admin/user/{username}"

    try:
        response = manager._api_delete(api_path)
        click.echo(f"User '{username}' successfully deleted.")
        # The _api_delete method returns a dict with a 'message' key if no JSON content
        if "message" in response:
            click.echo(f"API Confirmation: {response['message']}")

    except requests.exceptions.HTTPError as e:
        print(f"Error deleting user '{username}': HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        sys.exit(1)  # Exit on critical failure for delete
    except requests.exceptions.ConnectionError:
        print(f"Error deleting user '{username}': Connection failed.")
        print("Please check network connectivity or manager host/port.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"Error deleting user '{username}': The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while deleting user '{username}': {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        sys.exit(1)


# -----------------------------------------------------------------------------
# Create session with Cisco Catalyst SD-WAN Manager
# -----------------------------------------------------------------------------
print("\n--- Authenticating to SD-WAN Manager ---")
host, port, user, password = get_manager_credentials_from_env()
manager = Manager(host, port, user, password)

# -----------------------------------------------------------------------------
# Run commands
# -----------------------------------------------------------------------------
cli.add_command(ls)
cli.add_command(add)
cli.add_command(delete)

if __name__ == "__main__":
    cli()
