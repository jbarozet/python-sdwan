#! /usr/bin/env python3

import requests
import sys
import os
import json
import cmd
import tabulate
import click
from vmanage import Authentication

requests.packages.urllib3.disable_warnings()


# ----------------------------------------------------------------------------------------------------
# Click CLI
# ----------------------------------------------------------------------------------------------------

@click.group()
def cli():
    """Command line tool for to collect application names.
    """
    pass


# ----------------------------------------------------------------------------------------------------
# app-list
# ----------------------------------------------------------------------------------------------------

@click.command()
def app_list():
    """ Retrieve the list of Applications.
        Example command: ./app.py app-list
    """
    print("app-list")

    api_url = "/device/dpi/application-mapping"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        items = response.json()
        app_headers = ["App name", "Family", "ID"]
    else:
        click.echo(
            "Failed to get list of Apps " + str(response.text))
        exit()

    table = list()
    cli = cmd.Cmd()

    for item in items['data']:
        tr = [item['name'], item['family'], item['appId']]
        table.append(tr)

    click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))


# ----------------------------------------------------------------------------------------------------
# app-list-2
# Display app-name and family in multi-column view
# ----------------------------------------------------------------------------------------------------

@click.command()
def app_list_2():
    """ Retrieve the list of Applications.
        Example command: ./app.py app-list-2
    """
    print("app-list-2")

    api_url = "/device/dpi/application-mapping"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)

    if response.status_code == 200:
        items = response.json()    
    else:
        click.echo("Failed to get list of Apps " + str(response.text))
        exit()

    table = list()
    cli = cmd.Cmd()

    for item in items['data']:
        #print(item['name'])
        table.append(item['name'] + "(" + item['family'] + ")")

    click.echo(cli.columnize(table, displaywidth=120))


# ----------------------------------------------------------------------------------------------------
# qosmos-list
# ----------------------------------------------------------------------------------------------------

@click.command()
def qosmos_list():
    """ Retrieve the list of Qosmos Applications.
        Example command: ./app.py qosmos-list
    """
    print("qosmos-list")

    api_url = "/device/dpi/qosmos-static/applications"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        items = response.json()
        app_headers = ["App name", "Family", "ID"]
    else:
        click.echo(
            "Failed to get list of Apps " + str(response.text))
        exit()
    
    table = list()
    cli = cmd.Cmd()

    for item in items['data']:
        tr = [item['name'], item['family'], item['appId']]
        table.append(tr)

    click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))



# ----------------------------------------------------------------------------------------------------
# approute-fields
# ----------------------------------------------------------------------------------------------------

@click.command()
def approute_fields():
    """ Retrieve App route Aggregation API Query fields.
        Example command: ./monitor-app-route-stats.py approute-fields
    """

    try:
        api_url = "/statistics/approute/fields"

        url = base_url + api_url

        response = requests.get(url=url, headers=header, verify=False)

        if response.status_code == 200:
            items = response.json()
        else:
            click.echo(
                "Failed to get list of App route Query fields " + str(response.text))
            exit()

        tags = list()
        cli = cmd.Cmd()

        for item in items:
            tags.append(item['property'] + "(" + item['dataType'] + ")")

        click.echo(cli.columnize(tags, displaywidth=120))

    except Exception as e:
        print('Exception line number: {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


# ----------------------------------------------------------------------------------------------------
# approute-stats
# ----------------------------------------------------------------------------------------------------

@click.command()
def approute_stats():
    """ Create Average Approute statistics for all tunnels between provided 2 routers for last 1 hour.
        Example command: ./monitor-app-route-stats.py approute-stats
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
                        "value": [
                            "1"
                        ],
                        "field": "entry_time",
                        "type": "date",
                        "operator": "last_n_hours"
                    },
                    {
                        "value": [
                            rtr1_systemip
                        ],
                        "field": "local_system_ip",
                        "type": "string",
                        "operator": "in"
                    },
                    {
                        "value": [
                            rtr2_systemip
                        ],
                        "field": "remote_system_ip",
                        "type": "string",
                        "operator": "in"
                    }
                ]
            },
            "aggregation": {
                "field": [
                    {
                        "property": "name",
                        "sequence": 1,
                        "size": 6000
                    }
                ],
                "metrics": [
                    {
                        "property": "loss_percentage",
                        "type": "avg"
                    },
                    {
                        "property": "vqoe_score",
                        "type": "avg"
                    },
                    {
                        "property": "latency",
                        "type": "avg"
                    },
                    {
                        "property": "jitter",
                        "type": "avg"
                    }
                ]
            }
        }

        url = base_url + api_url

        response = requests.post(
            url=url, headers=header, data=json.dumps(payload), verify=False)

        if response.status_code == 200:
            app_route_stats = response.json()["data"]
            app_route_stats_headers = [
                "Tunnel name", "vQoE score", "Latency", "Loss percentage", "Jitter"]
            table = list()

            click.echo("\nAverage App route statistics between %s and %s for last 1 hour\n" % (
                rtr1_systemip, rtr2_systemip))
            
            for item in app_route_stats:
                tr = [item['name'], item['vqoe_score'], item['latency'],
                      item['loss_percentage'], item['jitter']]
                table.append(tr)
            try:
                click.echo(tabulate.tabulate(
                    table, app_route_stats_headers, tablefmt="fancy_grid"))
            except UnicodeEncodeError:
                click.echo(tabulate.tabulate(
                    table, app_route_stats_headers, tablefmt="grid"))

        else:
            click.echo("Failed to retrieve app route statistics\n")

        # Get app route statistics for tunnels from router-2 to router-1

        payload = {
            "query": {
                "condition": "AND",
                "rules": [
                    {
                        "value": [
                            "1"
                        ],
                        "field": "entry_time",
                        "type": "date",
                                "operator": "last_n_hours"
                    },
                    {
                        "value": [
                            rtr2_systemip
                        ],
                        "field": "local_system_ip",
                        "type": "string",
                                "operator": "in"
                    },
                    {
                        "value": [
                            rtr1_systemip
                        ],
                        "field": "remote_system_ip",
                        "type": "string",
                                "operator": "in"
                    }
                ]
            },
            "aggregation": {
                "field": [
                    {
                        "property": "name",
                        "sequence": 1,
                        "size": 6000
                    }
                ],
                "metrics": [
                    {
                        "property": "loss_percentage",
                        "type": "avg"
                    },
                    {
                        "property": "vqoe_score",
                        "type": "avg"
                    },
                    {
                        "property": "latency",
                        "type": "avg"
                    },
                    {
                        "property": "jitter",
                        "type": "avg"
                    }
                ]
            }
        }

        response = requests.post(
            url=url, headers=header, data=json.dumps(payload), verify=False)

        if response.status_code == 200:
            app_route_stats = response.json()["data"]
            app_route_stats_headers = [
                "Tunnel name", "vQoE score", "Latency", "Loss percentage", "Jitter"]
            table = list()

            click.echo("\nAverage App route statistics between %s and %s for last 1 hour\n" % (
                rtr2_systemip, rtr1_systemip))
            for item in app_route_stats:
                tr = [item['name'], item['vqoe_score'], item['latency'],
                      item['loss_percentage'], item['jitter']]
                table.append(tr)
            try:
                click.echo(tabulate.tabulate(
                    table, app_route_stats_headers, tablefmt="fancy_grid"))
            except UnicodeEncodeError:
                click.echo(tabulate.tabulate(
                    table, app_route_stats_headers, tablefmt="grid"))

        else:
            click.echo("Failed to retrieve app route statistics\n")



    except Exception as e:
        print('Exception line number: {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


# ----------------------------------------------------------------------------------------------------
# approute-device
# ----------------------------------------------------------------------------------------------------

@click.command()
def approute_device():
    """ Get Realtime Approute statistics for a specific tunnel for provided router and remote.
        Example command: ./monitor-app-route-stats.py approute-device
    """

    try:

        rtr1_systemip = input("Enter System IP address : ")
        rtr2_systemip = input("Enter Remote System IP address : ")
        color = input("Enter color : ")

        # api_url = "/device/app-route/statistics?remote-system-ip=10.0.0.101&local-color=public-internet&remote-color=public-internet&deviceId=10.0.0.108"
        api_url = "/device/app-route/statistics?remote-system-ip=%s&local-color=%s&remote-color=%s&deviceId=%s" % (
            rtr2_systemip, color, color, rtr1_systemip)
        #api_url = "/device/app-route/statistics?deviceId=%s&local-color=%s"%(rtr1_systemip,color)

        url = base_url + api_url

        response = requests.get(url=url, headers=header, verify=False)

        if response.status_code == 200:
            app_route_stats = response.json()["data"]
            app_route_stats_headers = ["vdevice-host-name", "remote-system-ip", "Index",
                                       "Mean Latency", "Mean Jitter", "Mean Loss", "average-latency", "average-jitter", "loss"]
            table = list()

            click.echo("\nRealtime App route statistics for %s to %s\n" %
                       (rtr1_systemip, rtr2_systemip))
            for item in app_route_stats:
                tr = [item['vdevice-host-name'], item['remote-system-ip'], item['index'], item['mean-latency'],
                      item['mean-jitter'], item['mean-loss'], item['average-latency'], item['average-jitter'], item['loss']]
                table.append(tr)
            try:
                click.echo(tabulate.tabulate(
                    table, app_route_stats_headers, tablefmt="fancy_grid"))
            except UnicodeEncodeError:
                click.echo(tabulate.tabulate(
                    table, app_route_stats_headers, tablefmt="grid"))

        else:
            click.echo("Failed to retrieve app route statistics\n")

        # click.echo("\n\nRaw data\n\n")
        # click.echo(app_route_stats)

    except Exception as e:
        print('Exception line number: {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)



# ----------------------------------------------------------------------------------------------------
# Get Parameters
# ----------------------------------------------------------------------------------------------------

vmanage_host = os.environ.get("vmanage_host")
vmanage_port = os.environ.get("vmanage_port")
vmanage_username = os.environ.get("vmanage_username")
vmanage_password = os.environ.get("vmanage_password")

if vmanage_host is None or vmanage_port is None or vmanage_username is None or vmanage_password is None:
    print("For Windows Workstation, vManage details must be set via environment variables using below commands")
    print("set vmanage_host=198.18.1.10")
    print("set vmanage_port=8443")
    print("set vmanage_username=admin")
    print("set vmanage_password=admin")
    print("For MAC OSX Workstation, vManage details must be set via environment variables using below commands")
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
    header = {'Content-Type': "application/json",
              'Cookie': jsessionid, 'X-XSRF-TOKEN': token}
else:
    header = {'Content-Type': "application/json", 'Cookie': jsessionid}

base_url = "https://%s:%s/dataservice" % (vmanage_host, vmanage_port)


# ----------------------------------------------------------------------------------------------------
# Run commands
# ----------------------------------------------------------------------------------------------------

cli.add_command(app_list)
cli.add_command(app_list_2)
cli.add_command(qosmos_list)
cli.add_command(approute_fields)
cli.add_command(approute_stats)
cli.add_command(approute_device)

if __name__ == "__main__":
    cli()
