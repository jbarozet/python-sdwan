#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Managing App Route Statistics and Applications
#
# Description:
#   List applications
#   List App route statistics between two routers
#
# =========================================================================

import cmd
import json
import os

import click
import requests
import tabulate

# Import the new unified Manager class and the credentials function
from manager import Manager, get_manager_credentials_from_env


# -----------------------------------------------------------------------------
@click.group()
def cli():
    """Command line tool for to collect application names and tunnel performances"""
    pass


# -----------------------------------------------------------------------------
def save_json(payload: str, filename: str = "payload"):
    """
    Save json response payload to a file

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
def app_list():
    """
    Retrieve the list of Applications.
    Example command: python approute.py app-list
    """

    print("Application List ")

    api_path = "/device/dpi/application-mapping"

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "applications_all")
        save_json(data, "applications_data")
        app_headers = ["App name", "Family", "ID"]

        table = list()
        cli = cmd.Cmd()

        for item in data:
            tr = [item["name"], item["family"], item["appId"]]
            table.append(tr)

        click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching apps: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print("Error fetching apps: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print("Error fetching apps: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while fetching apps: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def app_list2():
    """
    Retrieve the list of Applications (alternative display).
    Display app-name and family in multi-column view
    Example command: python approute.py app-list2
    """
    print("Application List (2)")

    api_path = "/device/dpi/application-mapping"

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "applications_all")
        save_json(data, "applications_data")

        table = list()
        cli = cmd.Cmd()

        for item in data:
            # print(item['name'])
            table.append(item["name"] + "(" + item["family"] + ")")

        click.echo(cli.columnize(table, displaywidth=120))

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching apps: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print("Error fetching apps: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print("Error fetching apps: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while fetching apps: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def app_qosmos():
    """
    Retrieve the list of Qosmos Applications (original Viptela classification engine)
    Example command: python approute.py app-qosmos
    """
    print("Application List (qosmos)")

    api_path = "/device/dpi/qosmos-static/applications"

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "qosmos_applications_all")
        save_json(data, "qosmos_applications_data")
        app_headers = ["App name", "Family", "ID"]

        table = list()
        cli = cmd.Cmd()

        for item in data:
            tr = [item["name"], item["family"], item["appId"]]
            table.append(tr)

        click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching apps: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print("Error fetching apps: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print("Error fetching apps: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while fetching apps: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def approute_fields():
    """
    Retrieve App route Aggregation API Query fields.
    Example command: python approute.py approute-fields
    """

    api_path = "/statistics/approute/fields"

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        save_json(payload, "approute-fields")

        tags = list()
        cli = cmd.Cmd()

        for item in payload:
            tags.append(item["property"] + "(" + item["dataType"] + ")")

        click.echo(cli.columnize(tags, displaywidth=120))

    except requests.exceptions.HTTPError as e:
        print(f"Error fetching approute fields: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print("Error fetching approute fields: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print("Error fetching approute fields: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while fetching approute fields: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def approute_stats():
    """
    Create Average Approute statistics for all tunnels between provided 2 routers for last 1 hour.
    Example command: python approute.py approute-stats
    """

    api_path = "/statistics/approute/aggregation"

    # Routers System IPs

    rtr1_systemip = input("Enter Router-1 System IP address : ")
    rtr2_systemip = input("Enter Router-2 System IP address : ")

    # Query payloads

    payload_r1_r2 = {
        "query": {
            "condition": "AND",
            "rules": [
                {
                    "value": ["1"],
                    "field": "entry_time",
                    "type": "date",
                    "operator": "last_n_hours",
                },
                {
                    "value": [rtr1_systemip],
                    "field": "local_system_ip",
                    "type": "string",
                    "operator": "in",
                },
                {
                    "value": [rtr2_systemip],
                    "field": "remote_system_ip",
                    "type": "string",
                    "operator": "in",
                },
            ],
        },
        "aggregation": {
            "field": [{"property": "name", "sequence": 1, "size": 6000}],
            "metrics": [
                {"property": "loss_percentage", "type": "avg"},
                {"property": "vqoe_score", "type": "avg"},
                {"property": "latency", "type": "avg"},
                {"property": "jitter", "type": "avg"},
            ],
        },
    }

    payload_r2_r1 = {
        "query": {
            "condition": "AND",
            "rules": [
                {
                    "value": ["1"],
                    "field": "entry_time",
                    "type": "date",
                    "operator": "last_n_hours",
                },
                {
                    "value": [rtr2_systemip],
                    "field": "local_system_ip",
                    "type": "string",
                    "operator": "in",
                },
                {
                    "value": [rtr1_systemip],
                    "field": "remote_system_ip",
                    "type": "string",
                    "operator": "in",
                },
            ],
        },
        "aggregation": {
            "field": [{"property": "name", "sequence": 1, "size": 6000}],
            "metrics": [
                {"property": "loss_percentage", "type": "avg"},
                {"property": "vqoe_score", "type": "avg"},
                {"property": "latency", "type": "avg"},
                {"property": "jitter", "type": "avg"},
            ],
        },
    }

    try:
        response = manager._api_post(api_path, payload=payload_r1_r2)
        app_route_stats = response.get("data")
        app_route_stats_headers = [
            "Tunnel name",
            "vQoE score",
            "Latency",
            "Loss percentage",
            "Jitter",
        ]
        table = list()

        click.echo(
            "\nAverage App route statistics between %s and %s for last 1 hour\n"
            % (rtr1_systemip, rtr2_systemip)
        )

        for item in app_route_stats:
            tr = [
                item["name"],
                item["vqoe_score"],
                item["latency"],
                item["loss_percentage"],
                item["jitter"],
            ]
            table.append(tr)

        click.echo(
            tabulate.tabulate(table, app_route_stats_headers, tablefmt="fancy_grid")
        )

        # Get app route statistics for tunnels from router-2 to router-1
        response = manager._api_post(api_path, payload=payload_r2_r1)
        app_route_stats = response.get("data")
        app_route_stats_headers = [
            "Tunnel name",
            "vQoE score",
            "Latency",
            "Loss percentage",
            "Jitter",
        ]
        table = list()

        click.echo(
            "\nAverage App route statistics between %s and %s for last 1 hour\n"
            % (rtr2_systemip, rtr1_systemip)
        )
        for item in app_route_stats:
            tr = [
                item["name"],
                item["vqoe_score"],
                item["latency"],
                item["loss_percentage"],
                item["jitter"],
            ]
            table.append(tr)
        click.echo(
            tabulate.tabulate(table, app_route_stats_headers, tablefmt="fancy_grid")
        )

    except requests.exceptions.HTTPError as e:
        print(f"Error posting request: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print("Error posting request: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print("Error posting request: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred while posting request: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def approute_device():
    """
    Get Realtime Approute statistics for a specific tunnel for provided router and remote.
    Example command: python approute.py approute-device
    """

    # Input parameters

    rtr1_systemip = input("Enter System IP address : ")
    rtr2_systemip = input("Enter Remote System IP address : ")
    color = input("Enter color : ")

    # API path with parameters

    api_path = (
        "/device/app-route/statistics?remote-system-ip=%s&local-color=%s&remote-color=%s&deviceId=%s"
        % (rtr2_systemip, color, color, rtr1_systemip)
    )

    # Fetch users
    try:
        payload = manager._api_get(api_path)
        app_route_stats = payload.get("data")
        app_route_stats_headers = [
            "vdevice-host-name",
            "remote-system-ip",
            "Index",
            "Mean Latency",
            "Mean Jitter",
            "Mean Loss",
            "average-latency",
            "average-jitter",
            "loss",
        ]
        table = list()

        click.echo(
            "\nRealtime App route statistics for %s to %s\n"
            % (rtr1_systemip, rtr2_systemip)
        )
        for item in app_route_stats:
            tr = [
                item["vdevice-host-name"],
                item["remote-system-ip"],
                item["index"],
                item["mean-latency"],
                item["mean-jitter"],
                item["mean-loss"],
                item["average-latency"],
                item["average-jitter"],
                item["loss"],
            ]
            table.append(tr)
        try:
            click.echo(
                tabulate.tabulate(table, app_route_stats_headers, tablefmt="fancy_grid")
            )
        except UnicodeEncodeError:
            click.echo(
                tabulate.tabulate(table, app_route_stats_headers, tablefmt="grid")
            )

    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP Error {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return
    except requests.exceptions.ConnectionError:
        print(f"Error: Connection failed.")
        print(
            "Please check network connectivity or ensure the SD-WAN Manager host/port is correct and reachable."
        )
        return
    except requests.exceptions.Timeout:
        print("Error: The request timed out.")
        print("The SD-WAN Manager might be slow to respond or unreachable.")
        return
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
# Create session with Cisco Catalyst SD-WAN Manager
# -----------------------------------------------------------------------------
print("\n--- Authenticating to SD-WAN Manager ---")
host, port, user, password = get_manager_credentials_from_env()
manager = Manager(host, port, user, password)


# ----------------------------------------------------------------------------------------------------
# Run commands
# ----------------------------------------------------------------------------------------------------
cli.add_command(app_list)
cli.add_command(app_list2)
cli.add_command(app_qosmos)
cli.add_command(approute_fields)
cli.add_command(approute_stats)
cli.add_command(approute_device)

if __name__ == "__main__":
    cli()
