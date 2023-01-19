#! /usr/bin/env python

import requests
import sys
import os
import json
import cmd
import tabulate
import click
from vmanage import Authentication
from settings import Settings

requests.packages.urllib3.disable_warnings()


# ----------------------------------------------------------------------------------------------------
# Click CLI
# ----------------------------------------------------------------------------------------------------

@click.group()
def cli():
    """Command line tool for to collect application names).
    """
    pass


# ----------------------------------------------------------------------------------------------------
# app-list
# ----------------------------------------------------------------------------------------------------

@click.command()
def app_list():
    """ Retrieve the list of Applications.                                  
        \nExample command: ./app.py app-list
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
# Get Device Configuration
# d/dataservice/system/device/{0}?deviceIP={1}
# ----------------------------------------------------------------------------------------------------

@click.command()
def get_device_by_ip():

    type='vedges'
    systemip = input("Enter System IP address : ")

    api_url = "/system/device/%s?deviceIP=%s" % (type, systemip)
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        items = response.json()["data"]
        app_headers = ["UUID", "Family", "ID"]
    else:
        click.echo(
            "Failed to get device " + str(response.text))
        exit()

    for item in items:
        tr = [item['configStatusMessage'], item['uuid'], item['deviceModel'], item['vedgeCertificateState'],
                      item['deviceIP'], item['host-name'], item['version'], item['vmanageConnectionState']]

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
        items = response.json()
        running_config = items['config']
    else:
        click.echo(
            "Failed to get device configuration " + str(response.text))
        exit()
    print(running_config)


# ----------------------------------------------------------------------------------------------------
# Get Settings
# ----------------------------------------------------------------------------------------------------

@click.command()
def get_org():
    settings = Settings(header, vmanage_host, vmanage_port)
    org = settings.get_vmanage_org()
    print(org)

@click.command()
def get_vbond():
    settings = Settings(header, vmanage_host, vmanage_port)
    vbond = settings.get_vbond()
    print(vbond)




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
cli.add_command(get_org)
cli.add_command(get_vbond)
cli.add_command(get_device_config)
cli.add_command(get_device_by_ip)

if __name__ == "__main__":
    cli()
