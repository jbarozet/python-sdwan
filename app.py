#! /usr/bin/env python3

import cmd
import json
import os
import sys

import click
import requests
import tabulate
import urllib3

# Import the new function from session.py
from session import get_authenticated_session_details


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
    Example command: python app.py app-list
    """

    print("Application List ")

    api_url = "/device/dpi/application-mapping"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, "applications_all")
        save_json(data, "applications_data")
        app_headers = ["App name", "Family", "ID"]
    else:
        click.echo("Failed to get list of Apps " + str(response.text))
        exit()

    table = list()
    cli = cmd.Cmd()

    for item in data:
        tr = [item["name"], item["family"], item["appId"]]
        table.append(tr)

    click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))


# -----------------------------------------------------------------------------
@click.command()
def app_list2():
    """
    Retrieve the list of Applications.
    Display app-name and family in multi-column view
    Example command: python app.py app-list2
    """
    print("Application List (2)")

    api_url = "/device/dpi/application-mapping"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)

    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, "applications_all")
        save_json(data, "applications_data")
    else:
        click.echo("Failed to get list of Apps " + str(response.text))
        exit()

    table = list()
    cli = cmd.Cmd()

    for item in data:
        # print(item['name'])
        table.append(item["name"] + "(" + item["family"] + ")")

    click.echo(cli.columnize(table, displaywidth=120))


# -----------------------------------------------------------------------------
@click.command()
def app_qosmos():
    """
    Retrieve the list of Qosmos Applications (original Viptela classification engine)
    Example command: python app.py app-qosmos
    """
    print("Application List (qosmos)")

    api_url = "/device/dpi/qosmos-static/applications"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        payload = response.json()
        data = payload["data"]
        # Save the payload and data to files
        save_json(payload, "qosmos_applications_all")
        save_json(data, "qosmos_applications_data")
        app_headers = ["App name", "Family", "ID"]
    else:
        click.echo("Failed to get list of Apps " + str(response.text))
        exit()

    table = list()
    cli = cmd.Cmd()

    for item in data:
        tr = [item["name"], item["family"], item["appId"]]
        table.append(tr)

    click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))


# -----------------------------------------------------------------------------
@click.command()
def approute_fields():
    """
    Retrieve App route Aggregation API Query fields.
    Example command: python app.py approute-fields
    """

    try:
        api_url = "/statistics/approute/fields"
        url = base_url + api_url

        response = requests.get(url=url, headers=header, verify=False)

        if response.status_code == 200:
            payload = response.json()
            # Save the payload and data to files
            save_json(payload, "approute-fields")
        else:
            click.echo(
                "Failed to get list of App route Query fields " + str(response.text)
            )
            exit()

        tags = list()
        cli = cmd.Cmd()

        for item in payload:
            tags.append(item["property"] + "(" + item["dataType"] + ")")

        click.echo(cli.columnize(tags, displaywidth=120))

    except Exception as e:
        print(
            "Exception line number: {}".format(sys.exc_info()[-1].tb_lineno),
            type(e).__name__,
            e,
        )


# -----------------------------------------------------------------------------
@click.command()
def approute_stats():
    """
    Create Average Approute statistics for all tunnels between provided 2 routers for last 1 hour.
    Example command: python app.py approute-stats
    """

    try:
        rtr1_systemip = input("Enter Router-1 System IP address : ")
        rtr2_systemip = input("Enter Router-2 System IP address : ")

        # Get app route statistics for tunnels from router-1 to router-2

        api_url = "/statistics/approute/aggregation"

        payload = {
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

        url = base_url + api_url

        response = requests.post(
            url=url, headers=header, data=json.dumps(payload), verify=False
        )

        if response.status_code == 200:
            app_route_stats = response.json()["data"]
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
            try:
                click.echo(
                    tabulate.tabulate(
                        table, app_route_stats_headers, tablefmt="fancy_grid"
                    )
                )
            except UnicodeEncodeError:
                click.echo(
                    tabulate.tabulate(table, app_route_stats_headers, tablefmt="grid")
                )

        else:
            click.echo("Failed to retrieve app route statistics\n")

        # Get app route statistics for tunnels from router-2 to router-1

        payload = {
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

        response = requests.post(
            url=url, headers=header, data=json.dumps(payload), verify=False
        )

        if response.status_code == 200:
            app_route_stats = response.json()["data"]
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
            try:
                click.echo(
                    tabulate.tabulate(
                        table, app_route_stats_headers, tablefmt="fancy_grid"
                    )
                )
            except UnicodeEncodeError:
                click.echo(
                    tabulate.tabulate(table, app_route_stats_headers, tablefmt="grid")
                )

        else:
            click.echo("Failed to retrieve app route statistics\n")

    except Exception as e:
        print(
            "Exception line number: {}".format(sys.exc_info()[-1].tb_lineno),
            type(e).__name__,
            e,
        )


# -----------------------------------------------------------------------------
@click.command()
def approute_device():
    """
    Get Realtime Approute statistics for a specific tunnel for provided router and remote.
    Example command: python app.py approute-device
    """

    try:
        rtr1_systemip = input("Enter System IP address : ")
        rtr2_systemip = input("Enter Remote System IP address : ")
        color = input("Enter color : ")

        # api_url = "/device/app-route/statistics?remote-system-ip=10.0.0.101&local-color=public-internet&remote-color=public-internet&deviceId=10.0.0.108"
        api_url = (
            "/device/app-route/statistics?remote-system-ip=%s&local-color=%s&remote-color=%s&deviceId=%s"
            % (rtr2_systemip, color, color, rtr1_systemip)
        )
        # api_url = "/device/app-route/statistics?deviceId=%s&local-color=%s"%(rtr1_systemip,color)

        url = base_url + api_url

        response = requests.get(url=url, headers=header, verify=False)

        if response.status_code == 200:
            app_route_stats = response.json()["data"]
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
                    tabulate.tabulate(
                        table, app_route_stats_headers, tablefmt="fancy_grid"
                    )
                )
            except UnicodeEncodeError:
                click.echo(
                    tabulate.tabulate(table, app_route_stats_headers, tablefmt="grid")
                )

        else:
            click.echo("Failed to retrieve app route statistics\n")

        # click.echo("\n\nRaw data\n\n")
        # click.echo(app_route_stats)

    except Exception as e:
        print(
            "Exception line number: {}".format(sys.exc_info()[-1].tb_lineno),
            type(e).__name__,
            e,
        )


# -----------------------------------------------------------------------------
# Global variables for base_url and header, obtained from session.py
# This will be executed once when the script starts
# -----------------------------------------------------------------------------
base_url, header = get_authenticated_session_details()


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
