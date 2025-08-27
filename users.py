import json
import os
import sys

import click
import requests
import tabulate

# Import the new function from session.py
from session import get_authenticated_session_details


# ---------------------------------------------------------
@click.group()
def cli():
    """Command line tool for managing users on SD-WAN Manager."""
    pass


# ---------------------------------------------------------
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


# ----------------------------------------------------------------------------------------------------
@click.command()
def ls():
    """List all users"""

    api_url = "/admin/user"
    url = base_url + api_url

    try:
        response = requests.get(url=url, headers=header, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        payload = response.json()
        data = payload.get("data", [])  # Use .get with default for safety

        save_json(payload, "users_all")
        save_json(data, "users_data")

        headers = ["Username", "Group"]
        table = []
        for item in data:
            tr = [
                item.get("userName", "N/A"),  # Use .get for safety
                ", ".join(item.get("group", ["N/A"])),  # Join list of groups
            ]
            table.append(tr)

        if table:  # Only print table if there's data
            click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
        else:
            click.echo("No users found or data is empty.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to get user list: {e}")
        if "response" in locals() and response is not None:
            click.echo(f"Status: {response.status_code}, Response: {response.text}")
        sys.exit(1)


@click.command()
def add():
    """Add a user"""

    api_url = "/admin/user"
    url = base_url + api_url

    print("\n~~~ Adding user")

    username = click.prompt("Enter username to add", type=str)
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
        "userName": username,
        "description": f"User {username} created via CLI",
        "locale": "en_US",
        "group": groups,
        "password": password,
        "resGroupName": "global",
    }

    try:
        response = requests.post(
            url=url, json=user_payload, headers=header, verify=False
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        click.echo(f"User '{username}' successfully created.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to add user '{username}': {e}")
        if "response" in locals() and response is not None:
            click.echo(f"Status: {response.status_code}, Response: {response.text}")
        sys.exit(1)


@click.command()
def delete():
    """Delete a user"""

    print("\n~~~ Deleting user")
    username = click.prompt("Enter username to delete", type=str)

    api_url = f"/admin/user/{username}"
    url = base_url + api_url

    try:
        response = requests.delete(url=url, headers=header, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors

        click.echo(f"User '{username}' successfully deleted.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to delete user '{username}': {e}")
        if "response" in locals() and response is not None:
            click.echo(f"Status: {response.status_code}, Response: {response.text}")
        sys.exit(1)


# -----------------------------------------------------------------------------
# Global variables for base_url and header, obtained from session.py
# This will be executed once when the script starts
# -----------------------------------------------------------------------------
base_url, header = get_authenticated_session_details()

# -----------------------------------------------------------------------------
# Run commands
# -----------------------------------------------------------------------------
cli.add_command(ls)
cli.add_command(add)
cli.add_command(delete)

if __name__ == "__main__":
    cli()
